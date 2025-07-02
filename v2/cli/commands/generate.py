"""
WeaverGen v2 Code Generation Commands
Core code generation functionality with BPMN orchestration
"""

import typer
import asyncio
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from ...core.engine.spiff_engine import WeaverGenV2Engine
from ...core.weaver_integration import WeaverGen, GenerationConfig

app = typer.Typer(
    name="generate",
    help="Code generation commands",
    rich_markup_mode="rich"
)

console = Console()

@app.command("code")
def generate_code(
    ctx: typer.Context,
    registry_url: str = typer.Argument(help="URL or path to semantic convention registry"),
    output_dir: Path = typer.Option(Path("./generated"), "--output", "-o", help="Output directory"),
    language: str = typer.Option("python", "--language", "-l", help="Target language"),
    template_dir: Optional[Path] = typer.Option(None, "--templates", "-t", help="Custom template directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Generate code from semantic conventions using OTel Weaver Forge"""
    
    async def run_generate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "registry_url": registry_url,
            "generation_config": {
                "output_dir": str(output_dir),
                "language": language,
                "template_dir": str(template_dir) if template_dir else None,
                "force": force,
                "verbose": verbose
            },
            "cli_command": "generate code"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🚀 Generating code from semantic conventions...", total=None)
            
            try:
                # Try BPMN workflow first
                result = await engine.execute_workflow("code_generation", context)
                
                if result.success:
                    generation_result = result.final_data.get("generation_result", {})
                    progress.update(task, description="✅ Code generation complete")
                    
                    display_generation_results(generation_result, output_dir)
                else:
                    # Fallback to direct generation
                    progress.update(task, description="⚡ Using direct generation...")
                    
                    config = GenerationConfig(
                        target_dir=output_dir,
                        templates_dir=template_dir,
                        force_overwrite=force
                    )
                    
                    weaver = WeaverGen(config=config, verbose=verbose)
                    result = weaver.generate(registry_url, str(output_dir))
                    
                    if result.success:
                        progress.update(task, description="✅ Code generation complete")
                        console.print(f"[green]Generated {len(result.files)} files[/green]")
                    else:
                        raise Exception(result.error or "Generation failed")
                        
            except Exception as e:
                progress.update(task, description="❌ Code generation failed")
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_generate())

@app.command("models")
def generate_models(
    ctx: typer.Context,
    semantic_yaml: Path = typer.Argument(help="Path to semantic convention YAML file"),
    output_dir: Path = typer.Option(Path("./generated/models"), "--output", "-o"),
    languages: List[str] = typer.Option(["python"], "--language", "-l", help="Target languages"),
    include_validation: bool = typer.Option(True, "--validation/--no-validation")
):
    """Generate data models from semantic conventions"""
    
    async def run_generate_models():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "semantic_file": str(semantic_yaml),
            "model_config": {
                "output_dir": str(output_dir),
                "languages": languages,
                "include_validation": include_validation,
                "include_serialization": True
            },
            "cli_command": "generate models"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🏗️ Generating data models...", total=None)
            
            try:
                result = await engine.execute_workflow("model_generation", context)
                
                if result.success:
                    models_result = result.final_data.get("models_result", {})
                    progress.update(task, description="✅ Model generation complete")
                    
                    display_model_results(models_result, languages)
                else:
                    progress.update(task, description="❌ Model generation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Model generation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_generate_models())

@app.command("forge")
def generate_forge(
    ctx: typer.Context,
    semantic_file: Path = typer.Argument(help="Path to semantic conventions YAML"),
    output_dir: Path = typer.Option(Path("./forge_output"), "--output", "-o"),
    template_type: str = typer.Option("all", "--template", "-t", help="Template type: metrics, traces, logs, all"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate after generation")
):
    """Generate using Forge templates with enhanced features"""
    
    async def run_forge_generate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "semantic_file": str(semantic_file),
            "forge_config": {
                "output_dir": str(output_dir),
                "template_type": template_type,
                "validate_output": validate,
                "include_documentation": True,
                "include_examples": True
            },
            "cli_command": "generate forge"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔨 Generating with Forge templates...", total=None)
            
            try:
                result = await engine.execute_workflow("forge_generation", context)
                
                if result.success:
                    forge_result = result.final_data.get("forge_result", {})
                    progress.update(task, description="✅ Forge generation complete")
                    
                    display_forge_results(forge_result, template_type)
                else:
                    progress.update(task, description="❌ Forge generation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Forge generation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_forge_generate())

@app.command("smart")
def generate_smart(
    ctx: typer.Context,
    convention: Path = typer.Argument(help="Path to semantic convention YAML"),
    agents: int = typer.Option(3, "--agents", "-a", help="Number of AI agents"),
    optimization_level: str = typer.Option("balanced", "--optimize", help="Optimization: fast, balanced, quality"),
    output_dir: Path = typer.Option(Path("./smart_generated"), "--output", "-o")
):
    """Smart generation with AI agent optimization"""
    
    async def run_smart_generate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "semantic_file": str(convention),
            "smart_config": {
                "agent_count": agents,
                "optimization_level": optimization_level,
                "output_dir": str(output_dir),
                "parallel_processing": True,
                "quality_checks": optimization_level == "quality"
            },
            "cli_command": "generate smart"
        }
        
        console.print(Panel(
            f"[bold blue]Smart Generation[/bold blue]\n"
            f"Convention: {convention.name}\n"
            f"Agents: {agents}\n"
            f"Optimization: {optimization_level}",
            title="Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🧠 Smart generation in progress...", total=None)
            
            try:
                result = await engine.execute_workflow("smart_generation", context)
                
                if result.success:
                    smart_result = result.final_data.get("smart_result", {})
                    progress.update(task, description="✅ Smart generation complete")
                    
                    display_smart_results(smart_result, agents)
                else:
                    progress.update(task, description="❌ Smart generation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Smart generation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_smart_generate())

# Display helper functions

def display_generation_results(result: dict, output_dir: Path):
    """Display code generation results"""
    table = Table(title="Code Generation Results")
    table.add_column("File", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Size", style="green")
    
    files = result.get("files", [])
    for file_info in files[:10]:  # Show first 10 files
        table.add_row(
            file_info.get("name", "unknown"),
            file_info.get("type", "code"),
            f"{file_info.get('size', 0)} bytes"
        )
    
    if len(files) > 10:
        table.add_row("...", f"({len(files) - 10} more files)", "...")
    
    console.print(table)
    console.print(f"\n[green]Total files generated: {len(files)}[/green]")
    console.print(f"[green]Output directory: {output_dir}[/green]")

def display_model_results(result: dict, languages: List[str]):
    """Display model generation results"""
    table = Table(title="Generated Models")
    table.add_column("Language", style="cyan")
    table.add_column("Models", style="magenta")
    table.add_column("Validators", style="green")
    table.add_column("Tests", style="yellow")
    
    for lang in languages:
        lang_result = result.get(lang, {})
        table.add_row(
            lang,
            str(lang_result.get("model_count", 0)),
            str(lang_result.get("validator_count", 0)),
            str(lang_result.get("test_count", 0))
        )
    
    console.print(table)

def display_forge_results(result: dict, template_type: str):
    """Display Forge generation results"""
    console.print(Panel(
        f"[bold green]Forge Generation Complete[/bold green]\n"
        f"Template Type: {template_type}\n"
        f"Files Generated: {result.get('file_count', 0)}\n"
        f"Documentation: {'✅' if result.get('docs_generated', False) else '❌'}\n"
        f"Examples: {'✅' if result.get('examples_generated', False) else '❌'}",
        title="Forge Results"
    ))

def display_smart_results(result: dict, agents: int):
    """Display smart generation results"""
    table = Table(title="Smart Generation Performance")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Agents Used", str(agents))
    table.add_row("Generation Time", f"{result.get('generation_time', 0):.2f}s")
    table.add_row("Optimization Score", f"{result.get('optimization_score', 0):.2%}")
    table.add_row("Quality Score", f"{result.get('quality_score', 0):.2%}")
    table.add_row("Files Generated", str(result.get('file_count', 0)))
    
    console.print(table)
    
    # Show agent contributions
    agent_contributions = result.get('agent_contributions', {})
    if agent_contributions:
        console.print("\n[bold]Agent Contributions:[/bold]")
        for agent_id, contribution in agent_contributions.items():
            console.print(f"  {agent_id}: {contribution:.1%}")

if __name__ == "__main__":
    app()