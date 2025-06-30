"""Main entry point for WeaverGen examples.

Usage:
    python -m weavergen.examples
    python -m weavergen.examples --help
    python -m weavergen.examples sql
    python -m weavergen.examples structured
"""

import sys
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


def show_menu():
    """Show interactive menu."""
    console.print(Panel.fit(
        "[bold]WeaverGen Ollama Examples[/bold]\n"
        "Structured output with pydantic-ai",
        border_style="blue"
    ))
    
    table = Table(show_header=False, box=None)
    table.add_column("Option", style="cyan", width=10)
    table.add_column("Description")
    
    table.add_row("1", "Check Setup - Verify Ollama installation")
    table.add_row("2", "SQL Generation - Generate SQL from natural language")
    table.add_row("3", "Structured Output - Extract typed data")
    table.add_row("4", "Validation Demo - See validation and retries")
    table.add_row("5", "Quick Demo - Run all examples")
    table.add_row("q", "Quit")
    
    console.print(table)
    console.print()


async def run_sql_demo():
    """Run SQL generation demo."""
    console.print("[bold]SQL Generation Demo[/bold]\n")
    
    from .ollama_utils import get_ollama_model
    from .sql_gen_ollama_simple import SqlQuery
    from pydantic_ai import Agent
    
    try:
        model = get_ollama_model()
        agent = Agent(
            model=model,
            result_type=SqlQuery,
            system_prompt="Generate PostgreSQL queries."
        )
        
        prompts = [
            "Show top 5 users by creation date",
            "Count active sessions in the last hour"
        ]
        
        for prompt in prompts:
            console.print(f"[yellow]Prompt:[/yellow] {prompt}")
            result = await agent.run(prompt)
            output = result.output
            console.print(f"[green]SQL:[/green] {output.query}")
            console.print(f"[blue]Explanation:[/blue] {output.explanation}\n")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


async def run_structured_demo():
    """Run structured output demo."""
    console.print("[bold]Structured Output Demo[/bold]\n")
    
    from .ollama_utils import get_ollama_model
    from pydantic import BaseModel, Field
    from pydantic_ai import Agent
    
    class Product(BaseModel):
        name: str
        price: float = Field(gt=0)
        in_stock: bool
        category: str
    
    try:
        model = get_ollama_model()
        agent = Agent(
            model=model,
            result_type=Product,
            system_prompt="Extract product information."
        )
        
        result = await agent.run(
            "The new MacBook Pro M3 costs $1599 and is available in our electronics section"
        )
        product = result.output
        
        console.print(f"Product: {product.name}")
        console.print(f"Price: ${product.price}")
        console.print(f"In Stock: {'Yes' if product.in_stock else 'No'}")
        console.print(f"Category: {product.category}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


async def run_validation_demo():
    """Run validation demo."""
    console.print("[bold]Validation and Retries Demo[/bold]\n")
    
    from .ollama_utils import get_ollama_model
    from pydantic import BaseModel, field_validator
    from pydantic_ai import Agent, ModelRetry
    import re
    
    class Email(BaseModel):
        address: str
        
        @field_validator("address")
        @classmethod
        def validate_email(cls, v: str) -> str:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
                raise ValueError("Invalid email format")
            return v.lower()
    
    try:
        model = get_ollama_model()
        agent = Agent(
            model=model,
            result_type=Email,
            system_prompt="Extract email addresses.",
            retries=3
        )
        
        # Add output validator for business logic
        @agent.output_validator
        async def check_email(ctx, result):
            if result.address.endswith(".test"):
                raise ModelRetry("Please extract a real email, not test domain")
            return result
        
        result = await agent.run("Contact me at john.doe@example.com")
        console.print(f"Extracted email: {result.output.address}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


async def run_all_demos():
    """Run all demos."""
    demos = [
        ("SQL Generation", run_sql_demo),
        ("Structured Output", run_structured_demo),
        ("Validation", run_validation_demo),
    ]
    
    for name, demo_func in demos:
        console.print(f"\n{'='*50}")
        console.print(f"[bold blue]{name}[/bold blue]")
        console.print(f"{'='*50}\n")
        await demo_func()
        await asyncio.sleep(1)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ["--help", "-h"]:
            console.print("Usage: python -m weavergen.examples [option]")
            console.print("\nOptions:")
            console.print("  sql        - Run SQL generation demo")
            console.print("  structured - Run structured output demo")
            console.print("  validation - Run validation demo")
            console.print("  all        - Run all demos")
            console.print("  setup      - Check Ollama setup")
            return
        
        elif arg == "setup":
            from . import check_setup
            check_setup.main()
            return
            
        elif arg == "sql":
            asyncio.run(run_sql_demo())
            return
            
        elif arg == "structured":
            asyncio.run(run_structured_demo())
            return
            
        elif arg == "validation":
            asyncio.run(run_validation_demo())
            return
            
        elif arg == "all":
            asyncio.run(run_all_demos())
            return
    
    # Interactive menu
    while True:
        show_menu()
        choice = console.input("Select an option: ").strip().lower()
        
        if choice == "1":
            from . import check_setup
            check_setup.main()
        elif choice == "2":
            asyncio.run(run_sql_demo())
        elif choice == "3":
            asyncio.run(run_structured_demo())
        elif choice == "4":
            asyncio.run(run_validation_demo())
        elif choice == "5":
            asyncio.run(run_all_demos())
        elif choice == "q":
            console.print("[yellow]Goodbye![/yellow]")
            break
        else:
            console.print("[red]Invalid option[/red]")
        
        if choice in ["1", "2", "3", "4", "5"]:
            console.print("\n[dim]Press Enter to continue...[/dim]")
            input()


if __name__ == "__main__":
    main()