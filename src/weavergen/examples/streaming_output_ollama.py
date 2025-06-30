"""Streaming Structured Output Example with Ollama.

This example demonstrates:
- Streaming structured output for real-time processing
- Partial model updates during streaming
- Validation during streaming
- Different streaming strategies
"""

import os
import asyncio
from typing import List, Optional, AsyncIterator
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.messages import ModelResponseStreamEvent
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel


# Set up Ollama
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"

console = Console()


# Example 1: Streaming a list of items
class TodoItem(BaseModel):
    """Single todo item."""
    id: int
    title: str
    completed: bool = False
    priority: str = Field(description="high, medium, or low")


class TodoList(BaseModel):
    """List of todo items."""
    name: str = Field(description="Name of the todo list")
    items: List[TodoItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


# Example 2: Streaming analysis results
class AnalysisStep(BaseModel):
    """Single step in an analysis."""
    step_number: int
    description: str
    result: Optional[str] = None
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")


class Analysis(BaseModel):
    """Complete analysis with multiple steps."""
    title: str
    summary: Optional[str] = None
    steps: List[AnalysisStep] = Field(default_factory=list)
    conclusion: Optional[str] = None
    total_confidence: Optional[float] = None


# Example 3: Streaming story generation
class StoryChapter(BaseModel):
    """Chapter in a story."""
    number: int
    title: str
    content: str
    word_count: int = 0


class Story(BaseModel):
    """Complete story with chapters."""
    title: str
    genre: str
    chapters: List[StoryChapter] = Field(default_factory=list)
    total_words: int = 0
    
    def update_word_counts(self):
        """Update word counts after adding content."""
        for chapter in self.chapters:
            chapter.word_count = len(chapter.content.split())
        self.total_words = sum(ch.word_count for ch in self.chapters)


async def example_streaming_list():
    """Example 1: Stream a list of items."""
    console.print("\n[bold blue]Example 1: Streaming Todo List[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=TodoList,
        system_prompt="""Generate a todo list based on the user's request.
        Create items one by one with appropriate priorities."""
    )
    
    prompt = "Create a todo list for launching a new product with 8-10 tasks"
    
    # Create a live display
    with Live(console=console, refresh_per_second=4) as live:
        table = Table(title="Todo List (Streaming)")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Task", style="white", width=40)
        table.add_column("Priority", style="yellow")
        table.add_column("Status", style="green")
        
        partial_result = None
        
        async with agent.run_stream(prompt) as stream:
            async for event in stream:
                if isinstance(event, ModelResponseStreamEvent):
                    # Update partial result
                    partial_result = event.partial_response
                    
                    if partial_result and hasattr(partial_result, 'items'):
                        # Clear and rebuild table
                        table = Table(title=f"Todo List: {getattr(partial_result, 'name', 'Loading...')}")
                        table.add_column("ID", style="cyan", width=4)
                        table.add_column("Task", style="white", width=40)
                        table.add_column("Priority", style="yellow")
                        table.add_column("Status", style="green")
                        
                        for item in partial_result.items:
                            table.add_row(
                                str(item.id),
                                item.title,
                                item.priority,
                                "✓" if item.completed else "○"
                            )
                        
                        live.update(table)
        
        # Get final result
        result = await stream.get_data()
        
    console.print(f"\n[green]Streaming complete![/green] Generated {len(result.items)} tasks")


async def example_streaming_analysis():
    """Example 2: Stream analysis steps with progress."""
    console.print("\n[bold blue]Example 2: Streaming Analysis[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=Analysis,
        system_prompt="""Perform a step-by-step analysis of the given topic.
        Break it down into 4-6 clear steps with confidence scores.
        Provide a conclusion at the end."""
    )
    
    prompt = "Analyze the feasibility of switching to renewable energy for a small business"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Starting analysis...", total=None)
        
        partial_result = None
        async with agent.run_stream(prompt) as stream:
            async for event in stream:
                if isinstance(event, ModelResponseStreamEvent):
                    partial_result = event.partial_response
                    
                    if partial_result:
                        # Update progress description
                        if hasattr(partial_result, 'title'):
                            progress.update(task, description=f"Analyzing: {partial_result.title}")
                        
                        # Show current steps
                        if hasattr(partial_result, 'steps') and partial_result.steps:
                            latest_step = partial_result.steps[-1]
                            progress.update(
                                task, 
                                description=f"Step {latest_step.step_number}: {latest_step.description[:50]}..."
                            )
        
        result = await stream.get_data()
    
    # Display final analysis
    console.print(Panel(f"[bold]{result.title}[/bold]", title="Analysis Complete"))
    
    # Display steps
    for step in result.steps:
        console.print(f"\n[bold]Step {step.step_number}:[/bold] {step.description}")
        if step.result:
            console.print(f"   Result: {step.result}")
        console.print(f"   Confidence: {step.confidence:.0%}")
    
    if result.conclusion:
        console.print(Panel(result.conclusion, title="Conclusion", border_style="green"))
    
    if result.total_confidence:
        console.print(f"\n[bold]Overall Confidence:[/bold] {result.total_confidence:.0%}")


async def example_streaming_story():
    """Example 3: Stream story generation with live updates."""
    console.print("\n[bold blue]Example 3: Streaming Story Generation[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=Story,
        system_prompt="""Generate a short story with the requested genre.
        Create 3-4 chapters, each with a title and content.
        Keep chapters concise but engaging."""
    )
    
    prompt = "Write a short science fiction story about first contact with aliens"
    
    # Track streaming progress
    with Live(console=console, refresh_per_second=2) as live:
        display = Table.grid()
        display.add_column()
        
        partial_result = None
        async with agent.run_stream(prompt) as stream:
            async for event in stream:
                if isinstance(event, ModelResponseStreamEvent):
                    partial_result = event.partial_response
                    
                    if partial_result:
                        # Clear display
                        display = Table.grid()
                        display.add_column()
                        
                        # Add title and genre
                        if hasattr(partial_result, 'title'):
                            display.add_row(Panel(
                                f"[bold]{partial_result.title}[/bold]\n"
                                f"Genre: {getattr(partial_result, 'genre', '...')}",
                                title="Story in Progress"
                            ))
                        
                        # Add chapters
                        if hasattr(partial_result, 'chapters'):
                            for chapter in partial_result.chapters:
                                display.add_row("")  # Space
                                display.add_row(f"[bold]Chapter {chapter.number}: {chapter.title}[/bold]")
                                
                                # Show preview of content (first 100 chars)
                                if chapter.content:
                                    preview = chapter.content[:150] + "..." if len(chapter.content) > 150 else chapter.content
                                    display.add_row(f"[dim]{preview}[/dim]")
                        
                        live.update(display)
        
        result = await stream.get_data()
    
    # Update word counts
    result.update_word_counts()
    
    # Display final story summary
    console.print("\n[bold green]Story Generation Complete![/bold green]")
    console.print(Panel(
        f"[bold]{result.title}[/bold]\n"
        f"Genre: {result.genre}\n"
        f"Chapters: {len(result.chapters)}\n"
        f"Total Words: {result.total_words}",
        title="Story Summary"
    ))
    
    # Ask if user wants to see full story
    console.print("\n[yellow]Full story generated with streaming.[/yellow]")


async def example_custom_streaming():
    """Example 4: Custom streaming handler with validation."""
    console.print("\n[bold blue]Example 4: Custom Streaming Handler[/bold blue]")
    
    class Report(BaseModel):
        """Technical report structure."""
        title: str
        sections: List[dict] = Field(default_factory=list)
        metrics: dict = Field(default_factory=dict)
        status: str = "draft"
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=Report,
        system_prompt="Generate a technical report on the requested topic."
    )
    
    # Custom streaming handler
    class StreamHandler:
        def __init__(self):
            self.events = []
            self.partial_data = None
            self.validations_passed = 0
            
        async def handle_stream(self, stream) -> Report:
            async for event in stream:
                self.events.append(event)
                
                if isinstance(event, ModelResponseStreamEvent):
                    self.partial_data = event.partial_response
                    
                    # Perform validation during streaming
                    if self.partial_data and hasattr(self.partial_data, 'sections'):
                        if len(self.partial_data.sections) > self.validations_passed:
                            console.print(f"[dim]Section {len(self.partial_data.sections)} validated[/dim]")
                            self.validations_passed = len(self.partial_data.sections)
            
            return await stream.get_data()
    
    handler = StreamHandler()
    
    prompt = "Create a technical report on the benefits of microservices architecture"
    
    async with agent.run_stream(prompt) as stream:
        result = await handler.handle_stream(stream)
    
    console.print(f"\n[green]Report generated with {len(handler.events)} streaming events[/green]")
    console.print(f"Title: {result.title}")
    console.print(f"Sections: {len(result.sections)}")
    console.print(f"Status: {result.status}")


async def main():
    """Run all streaming examples."""
    console.print("[bold green]Streaming Structured Output Examples with Ollama[/bold green]")
    console.print("=" * 60)
    
    await example_streaming_list()
    await example_streaming_analysis()
    await example_streaming_story()
    await example_custom_streaming()
    
    console.print("\n[bold green]All streaming examples completed![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())