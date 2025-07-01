"""
Generated CLI from semantic conventions
"""

import typer
from pathlib import Path
from rich.console import Console
from rich import print as rprint

app = typer.Typer(help="Generated CLI from semantic conventions")
console = Console()

@app.command()
def run(
    mode: str = typer.Option("conversation", help="Operation mode"),
    topic: str = typer.Option("System Discussion", help="Topic for conversation"),
    agents: int = typer.Option(3, help="Number of agents")
):
    """Run the generated system"""
    rprint(f"[cyan]🚀 Running generated system[/cyan]")
    rprint(f"[yellow]Mode: {mode}[/yellow]")
    rprint(f"[yellow]Topic: {topic}[/yellow]")
    rprint(f"[yellow]Agents: {agents}[/yellow]")
    
    # Import and run generated system
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from generated_system import run_generated_system
        
        result = run_generated_system(mode=mode, topic=topic, agents=agents)
        
        if result.get("success"):
            rprint("[green]✅ Generated system completed successfully[/green]")
        else:
            rprint(f"[red]❌ Generated system failed: {result.get('error')}[/red]")
            
    except ImportError as e:
        rprint(f"[red]❌ Failed to import generated system: {e}[/red]")

if __name__ == "__main__":
    app()
