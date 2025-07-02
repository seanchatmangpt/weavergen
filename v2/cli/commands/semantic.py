"""
WeaverGen v2 Semantic Commands
AI-powered semantic convention generation and management
"""

import typer
import asyncio
import json
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ...core.engine.spiff_engine import WeaverGenV2Engine

app = typer.Typer(
    name="semantic",
    help="AI-powered semantic convention generation",
    rich_markup_mode="rich"
)

console = Console()

@app.command("generate")
def semantic_generate(
    ctx: typer.Context,
    domain: str = typer.Argument(help="Domain for semantic generation (e.g., 'cloud', 'iot', 'finance')"),
    output_file: Path = typer.Option(Path("./semantic_convention.yaml"), "--output", "-o"),
    ai_model: str = typer.Option("gpt-4", "--model", "-m", help="AI model to use"),
    examples: int = typer.Option(3, "--examples", "-e", help="Number of examples to generate"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive generation mode")
):
    """Generate semantic conventions using AI"""
    
    async def run_generate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "domain": domain,
            "ai_config": {
                "model": ai_model,
                "temperature": 0.7,
                "max_tokens": 2000,
                "include_examples": examples > 0,
                "example_count": examples
            },
            "interactive_mode": interactive,
            "cli_command": "semantic generate"
        }
        
        if interactive:
            console.print(Panel(
                "[bold blue]Interactive Semantic Generation[/bold blue]\n"
                "I'll guide you through creating semantic conventions step by step.",
                title="Welcome"
            ))
            
            # Gather additional context interactively
            context["interactive_inputs"] = {
                "description": Prompt.ask("Describe your use case"),
                "attributes": Prompt.ask("Key attributes (comma-separated)").split(","),
                "metrics": Confirm.ask("Include metrics?"),
                "traces": Confirm.ask("Include traces?"),
                "logs": Confirm.ask("Include logs?")
            }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🧠 Generating semantic conventions for {domain}...", total=None)
            
            try:
                result = await engine.execute_workflow("ai_semantic_generation", context)
                
                if result.success:
                    semantic_data = result.final_data.get("semantic_convention", {})
                    progress.update(task, description="✅ Generation complete")
                    
                    # Save to file
                    import yaml
                    with open(output_file, 'w') as f:
                        yaml.dump(semantic_data, f, default_flow_style=False)
                    
                    display_semantic_results(semantic_data, output_file)
                else:
                    progress.update(task, description="❌ Generation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Generation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_generate())

@app.command("enhance")
def semantic_enhance(
    ctx: typer.Context,
    input_file: Path = typer.Argument(help="Existing semantic convention file"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file (defaults to input)"),
    aspects: List[str] = typer.Option(["completeness", "consistency"], "--aspect", "-a"),
    ai_suggestions: bool = typer.Option(True, "--ai/--no-ai", help="Use AI for suggestions")
):
    """Enhance existing semantic conventions"""
    
    async def run_enhance():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        if not input_file.exists():
            console.print(f"[red]Input file not found: {input_file}[/red]")
            raise typer.Exit(1)
        
        context = {
            "input_file": str(input_file),
            "enhancement_config": {
                "aspects": aspects,
                "use_ai": ai_suggestions,
                "preserve_structure": True,
                "add_documentation": True
            },
            "cli_command": "semantic enhance"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔧 Enhancing semantic conventions...", total=None)
            
            try:
                result = await engine.execute_workflow("enhance_semantics", context)
                
                if result.success:
                    enhanced_data = result.final_data.get("enhanced_convention", {})
                    progress.update(task, description="✅ Enhancement complete")
                    
                    # Save to file
                    output_path = output_file or input_file
                    import yaml
                    with open(output_path, 'w') as f:
                        yaml.dump(enhanced_data, f, default_flow_style=False)
                    
                    display_enhancement_results(result.final_data, output_path)
                else:
                    progress.update(task, description="❌ Enhancement failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Enhancement failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_enhance())

@app.command("analyze")
def semantic_analyze(
    ctx: typer.Context,
    convention_file: Path = typer.Argument(help="Semantic convention file to analyze"),
    report_format: str = typer.Option("rich", "--format", "-f", help="Report format: rich, json, markdown"),
    save_report: bool = typer.Option(False, "--save", help="Save analysis report")
):
    """Analyze semantic conventions for quality and completeness"""
    
    async def run_analyze():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "convention_file": str(convention_file),
            "analysis_config": {
                "check_completeness": True,
                "check_consistency": True,
                "check_best_practices": True,
                "generate_recommendations": True
            },
            "cli_command": "semantic analyze"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Analyzing semantic conventions...", total=None)
            
            try:
                result = await engine.execute_workflow("analyze_semantics", context)
                
                if result.success:
                    analysis_data = result.final_data.get("analysis_result", {})
                    progress.update(task, description="✅ Analysis complete")
                    
                    if report_format == "rich":
                        display_analysis_results(analysis_data)
                    elif report_format == "json":
                        console.print_json(json.dumps(analysis_data, indent=2))
                    elif report_format == "markdown":
                        display_analysis_markdown(analysis_data)
                    
                    if save_report:
                        report_file = convention_file.with_suffix(f".analysis.{report_format}")
                        save_analysis_report(analysis_data, report_file, report_format)
                        console.print(f"[green]Report saved to: {report_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Analysis failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Analysis failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_analyze())

@app.command("merge")
def semantic_merge(
    ctx: typer.Context,
    files: List[Path] = typer.Argument(..., help="Semantic convention files to merge"),
    output_file: Path = typer.Option(Path("./merged_convention.yaml"), "--output", "-o"),
    strategy: str = typer.Option("smart", "--strategy", "-s", help="Merge strategy: smart, union, intersection"),
    resolve_conflicts: bool = typer.Option(True, "--resolve/--no-resolve")
):
    """Merge multiple semantic convention files"""
    
    async def run_merge():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        # Verify all files exist
        for file in files:
            if not file.exists():
                console.print(f"[red]File not found: {file}[/red]")
                raise typer.Exit(1)
        
        context = {
            "input_files": [str(f) for f in files],
            "merge_config": {
                "strategy": strategy,
                "resolve_conflicts": resolve_conflicts,
                "preserve_metadata": True,
                "validate_result": True
            },
            "cli_command": "semantic merge"
        }
        
        console.print(f"[bold]Merging {len(files)} semantic convention files...[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔀 Merging conventions...", total=None)
            
            try:
                result = await engine.execute_workflow("merge_semantics", context)
                
                if result.success:
                    merged_data = result.final_data.get("merged_convention", {})
                    progress.update(task, description="✅ Merge complete")
                    
                    # Save merged file
                    import yaml
                    with open(output_file, 'w') as f:
                        yaml.dump(merged_data, f, default_flow_style=False)
                    
                    display_merge_results(result.final_data, output_file)
                else:
                    progress.update(task, description="❌ Merge failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Merge failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_merge())

# Display helper functions

def display_semantic_results(data: dict, output_file: Path):
    """Display generated semantic convention results"""
    console.print(Panel(
        f"[bold green]Semantic Convention Generated![/bold green]\n"
        f"Domain: {data.get('domain', 'unknown')}\n"
        f"Version: {data.get('version', '1.0.0')}\n"
        f"Attributes: {len(data.get('attributes', []))}\n"
        f"Metrics: {len(data.get('metrics', []))}\n"
        f"Output: {output_file}",
        title="Generation Summary"
    ))
    
    # Show sample attributes
    attributes = data.get('attributes', [])
    if attributes:
        console.print("\n[bold]Sample Attributes:[/bold]")
        for attr in attributes[:5]:
            console.print(f"  • {attr.get('name', 'unknown')}: {attr.get('type', 'string')} - {attr.get('description', '')}")

def display_enhancement_results(data: dict, output_file: Path):
    """Display enhancement results"""
    improvements = data.get('improvements', {})
    
    table = Table(title="Enhancement Summary")
    table.add_column("Aspect", style="cyan")
    table.add_column("Before", style="red")
    table.add_column("After", style="green")
    table.add_column("Improvement", style="magenta")
    
    for aspect, stats in improvements.items():
        table.add_row(
            aspect,
            str(stats.get('before', 0)),
            str(stats.get('after', 0)),
            f"+{stats.get('added', 0)}"
        )
    
    console.print(table)
    
    # Show added elements
    added_elements = data.get('added_elements', [])
    if added_elements:
        console.print("\n[bold]Added Elements:[/bold]")
        for elem in added_elements[:5]:
            console.print(f"  • {elem}")

def display_analysis_results(data: dict):
    """Display semantic analysis results"""
    score = data.get('overall_score', 0)
    status = "Excellent" if score > 0.9 else "Good" if score > 0.7 else "Needs Improvement"
    
    console.print(Panel(
        f"[bold]Overall Score: {score:.1%} - {status}[/bold]",
        title="Analysis Summary"
    ))
    
    # Category scores
    categories = data.get('category_scores', {})
    if categories:
        table = Table(title="Category Analysis")
        table.add_column("Category", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Status", style="magenta")
        
        for category, cat_score in categories.items():
            status_icon = "✅" if cat_score > 0.8 else "⚠️" if cat_score > 0.6 else "❌"
            table.add_row(category, f"{cat_score:.1%}", status_icon)
        
        console.print(table)
    
    # Recommendations
    recommendations = data.get('recommendations', [])
    if recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(recommendations[:5], 1):
            console.print(f"{i}. {rec}")

def display_analysis_markdown(data: dict):
    """Display analysis results in markdown format"""
    md_lines = [
        "# Semantic Convention Analysis Report",
        "",
        f"**Overall Score:** {data.get('overall_score', 0):.1%}",
        "",
        "## Category Scores",
        ""
    ]
    
    categories = data.get('category_scores', {})
    for category, score in categories.items():
        md_lines.append(f"- **{category}:** {score:.1%}")
    
    md_lines.extend(["", "## Recommendations", ""])
    for rec in data.get('recommendations', []):
        md_lines.append(f"- {rec}")
    
    console.print("\n".join(md_lines))

def save_analysis_report(data: dict, report_file: Path, format: str):
    """Save analysis report to file"""
    if format == "json":
        report_file.write_text(json.dumps(data, indent=2))
    elif format == "markdown":
        # Generate markdown content
        md_content = display_analysis_markdown(data)
        report_file.write_text(md_content)
    else:
        # Default to JSON
        report_file.write_text(json.dumps(data, indent=2))

def display_merge_results(data: dict, output_file: Path):
    """Display merge results"""
    stats = data.get('merge_statistics', {})
    conflicts = data.get('conflicts_resolved', [])
    
    console.print(Panel(
        f"[bold green]Merge Complete![/bold green]\n"
        f"Files Merged: {stats.get('file_count', 0)}\n"
        f"Total Attributes: {stats.get('total_attributes', 0)}\n"
        f"Conflicts Resolved: {len(conflicts)}\n"
        f"Output: {output_file}",
        title="Merge Summary"
    ))
    
    if conflicts:
        console.print("\n[bold]Resolved Conflicts:[/bold]")
        for conflict in conflicts[:5]:
            console.print(f"  • {conflict['attribute']}: {conflict['resolution']}")

if __name__ == "__main__":
    app()