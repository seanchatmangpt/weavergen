"""Structured Output Examples with Ollama.

This example demonstrates various structured output features from pydantic-ai:
- Different output modes (json_output, prompted_output)
- Validation and retries
- Dynamic schemas
- Streaming structured output
"""

import os
from datetime import date
from typing import List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


# Set up Ollama
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"

console = Console()


# Example 1: Basic Structured Output
class City(BaseModel):
    """Basic city information."""
    name: str = Field(description="The name of the city")
    country: str = Field(description="The country where the city is located")
    population: Optional[int] = Field(None, description="The population of the city")
    
    @field_validator("population")
    @classmethod
    def validate_population(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Population cannot be negative")
        return v


# Example 2: Complex Nested Structure
class Ingredient(BaseModel):
    """Recipe ingredient."""
    name: str
    amount: float
    unit: str
    
    @model_validator(mode="after")
    def validate_amount(self):
        if self.amount <= 0:
            raise ValueError(f"Amount for {self.name} must be positive")
        return self


class RecipeStep(BaseModel):
    """Single step in a recipe."""
    step_number: int
    instruction: str
    duration_minutes: Optional[int] = None


class Recipe(BaseModel):
    """Complete recipe structure."""
    name: str = Field(description="Name of the dish")
    cuisine: str = Field(description="Type of cuisine (e.g., Italian, Mexican)")
    difficulty: str = Field(description="Difficulty level: easy, medium, or hard")
    ingredients: List[Ingredient]
    steps: List[RecipeStep]
    total_time_minutes: int
    servings: int = Field(gt=0, description="Number of servings")
    
    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = ["easy", "medium", "hard"]
        if v.lower() not in allowed:
            raise ValueError(f"Difficulty must be one of {allowed}")
        return v.lower()
    
    @model_validator(mode="after")
    def validate_steps_order(self):
        """Ensure steps are numbered correctly."""
        expected = list(range(1, len(self.steps) + 1))
        actual = sorted([step.step_number for step in self.steps])
        if actual != expected:
            raise ValueError("Step numbers must be sequential starting from 1")
        return self


# Example 3: Union Types and Enums
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class Task(BaseModel):
    """Task in a project."""
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    assignee: Optional[str] = None
    priority: int = Field(ge=1, le=5, description="Priority from 1 (low) to 5 (high)")


class Project(BaseModel):
    """Project with tasks."""
    name: str
    description: str
    tasks: List[Task]
    
    @property
    def task_summary(self) -> dict:
        """Summary of tasks by status."""
        summary = {status: 0 for status in TaskStatus}
        for task in self.tasks:
            summary[task.status] += 1
        return summary


# Example 4: Dynamic Schema
def create_data_extractor(fields: List[tuple[str, type, str]]) -> type[BaseModel]:
    """Create a dynamic Pydantic model based on field specifications.
    
    Args:
        fields: List of (field_name, field_type, description) tuples
    """
    field_definitions = {}
    for field_name, field_type, description in fields:
        field_definitions[field_name] = (field_type, Field(description=description))
    
    return type("DynamicExtractor", (BaseModel,), {
        "__annotations__": {k: v[0] for k, v in field_definitions.items()},
        **{k: v[1] for k, v in field_definitions.items()}
    })


async def example_basic_output():
    """Example 1: Basic structured output."""
    console.print("\n[bold blue]Example 1: Basic Structured Output[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=City,
        system_prompt="Extract city information from the user's input."
    )
    
    inputs = [
        "London is the capital of England with about 9 million people",
        "Tokyo, Japan's capital, has a population of nearly 14 million",
        "What about Paris?",  # This should handle missing population
    ]
    
    for input_text in inputs:
        try:
            result = await agent.run(input_text)
            city = result.output
            
            table = Table(title=f"City: {city.name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Name", city.name)
            table.add_row("Country", city.country)
            table.add_row("Population", f"{city.population:,}" if city.population else "Unknown")
            
            console.print(table)
            console.print()
            
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


async def example_complex_structure():
    """Example 2: Complex nested structure with validation."""
    console.print("\n[bold blue]Example 2: Complex Nested Structure[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=Recipe,
        system_prompt="""You are a helpful cooking assistant. 
        Extract recipe information and ensure all details are accurate.
        Make sure ingredients have positive amounts and steps are numbered sequentially."""
    )
    
    # Add result validator for additional checks
    @agent.result_validator
    async def validate_recipe(ctx: RunContext[None], result: Recipe) -> Recipe:
        # Check total time makes sense
        step_time = sum(step.duration_minutes or 0 for step in result.steps)
        if step_time > result.total_time_minutes:
            raise ModelRetry(
                f"Total time ({result.total_time_minutes} min) is less than sum of step times ({step_time} min)"
            )
        return result
    
    prompt = "Give me a simple pasta carbonara recipe"
    
    try:
        result = await agent.run(prompt)
        recipe = result.output
        
        console.print(Panel(f"[bold]{recipe.name}[/bold]\n{recipe.cuisine} cuisine - {recipe.difficulty} difficulty"))
        
        # Ingredients table
        ing_table = Table(title="Ingredients")
        ing_table.add_column("Ingredient", style="cyan")
        ing_table.add_column("Amount", style="yellow")
        ing_table.add_column("Unit", style="green")
        
        for ing in recipe.ingredients:
            ing_table.add_row(ing.name, str(ing.amount), ing.unit)
        
        console.print(ing_table)
        
        # Steps
        console.print("\n[bold]Steps:[/bold]")
        for step in recipe.steps:
            time_str = f" ({step.duration_minutes} min)" if step.duration_minutes else ""
            console.print(f"{step.step_number}. {step.instruction}{time_str}")
        
        console.print(f"\n[bold]Total time:[/bold] {recipe.total_time_minutes} minutes")
        console.print(f"[bold]Servings:[/bold] {recipe.servings}")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


async def example_union_types():
    """Example 3: Union types and enums."""
    console.print("\n[bold blue]Example 3: Union Types and Enums[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=Project,
        system_prompt="""You are a project manager. 
        Create a project plan with multiple tasks.
        Ensure tasks have valid statuses and priorities (1-5)."""
    )
    
    prompt = "Create a project plan for building a simple web application"
    
    try:
        result = await agent.run(prompt)
        project = result.output
        
        console.print(Panel(f"[bold]{project.name}[/bold]\n{project.description}"))
        
        # Tasks table
        task_table = Table(title="Tasks")
        task_table.add_column("ID", style="cyan")
        task_table.add_column("Title", style="white")
        task_table.add_column("Status", style="yellow")
        task_table.add_column("Priority", style="red")
        task_table.add_column("Assignee", style="green")
        
        for task in project.tasks:
            task_table.add_row(
                str(task.id),
                task.title,
                task.status.value,
                "⭐" * task.priority,
                task.assignee or "Unassigned"
            )
        
        console.print(task_table)
        
        # Summary
        console.print("\n[bold]Task Summary:[/bold]")
        for status, count in project.task_summary.items():
            console.print(f"  {status.value}: {count}")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


async def example_dynamic_schema():
    """Example 4: Dynamic schema generation."""
    console.print("\n[bold blue]Example 4: Dynamic Schema[/bold blue]")
    
    # Define fields dynamically based on requirements
    product_fields = [
        ("product_name", str, "Name of the product"),
        ("price", float, "Price in USD"),
        ("in_stock", bool, "Whether the product is in stock"),
        ("category", str, "Product category"),
        ("rating", Optional[float], "Average customer rating (0-5)")
    ]
    
    ProductInfo = create_data_extractor(product_fields)
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=ProductInfo,
        system_prompt="Extract product information from the description."
    )
    
    descriptions = [
        "The new iPhone 15 Pro costs $999, it's in stock, rated 4.5 stars in the electronics category",
        "Organic bananas are $2.99 per pound, currently available in our produce section with a 4.2 rating"
    ]
    
    for desc in descriptions:
        try:
            result = await agent.run(desc)
            product = result.output
            
            console.print(f"\n[bold]Product Information:[/bold]")
            for field_name, _, _ in product_fields:
                value = getattr(product, field_name)
                console.print(f"  {field_name}: {value}")
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


async def example_prompted_output():
    """Example 5: Using prompted output mode."""
    console.print("\n[bold blue]Example 5: Prompted Output Mode[/bold blue]")
    
    # This mode is useful when you want more control over how the model generates structured data
    from pydantic_ai import Agent
    from pydantic_ai.output import PromptedOutput
    
    class CodeExample(BaseModel):
        """Code example with explanation."""
        language: str = Field(description="Programming language")
        code: str = Field(description="The code snippet")
        explanation: str = Field(description="Explanation of what the code does")
        complexity: str = Field(description="Complexity level: beginner, intermediate, advanced")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=PromptedOutput[CodeExample],
        system_prompt="You are a coding instructor providing examples."
    )
    
    prompt = "Show me a Python example of using list comprehension"
    
    try:
        result = await agent.run(prompt)
        example = result.output.output
        
        console.print(Panel(f"[bold]{example.language} Example[/bold] - {example.complexity}"))
        
        syntax = Syntax(example.code, example.language.lower(), theme="monokai", line_numbers=True)
        console.print(syntax)
        
        console.print(f"\n[bold]Explanation:[/bold]\n{example.explanation}")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


async def main():
    """Run all structured output examples."""
    console.print("[bold green]Structured Output Examples with Ollama[/bold green]")
    console.print("=" * 60)
    
    await example_basic_output()
    await example_complex_structure()
    await example_union_types()
    await example_dynamic_schema()
    await example_prompted_output()
    
    console.print("\n[bold green]All examples completed![/bold green]")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())