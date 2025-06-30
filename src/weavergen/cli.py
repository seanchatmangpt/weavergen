"""CLI interface for WeaverGen using Typer."""

import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .core import WeaverGen
from .models import GenerationConfig

app = typer.Typer(
    name="weavergen",
    help="🌟 Python wrapper for OTel Weaver Forge with Claude Code optimization",
    rich_markup_mode="rich",
)

console = Console()


@app.command()
def generate(
    registry_url: str = typer.Argument(
        ..., 
        help="URL or path to semantic convention registry"
    ),
    output_dir: Path = typer.Option(
        Path("./generated"),
        "--output", "-o",
        help="Output directory for generated code"
    ),
    language: str = typer.Option(
        "python",
        "--language", "-l", 
        help="Target language for code generation"
    ),
    template_dir: Optional[Path] = typer.Option(
        None,
        "--templates", "-t",
        help="Custom template directory (uses built-in if not specified)"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Overwrite existing files"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose output"
    ),
) -> None:
    """🚀 Generate code from semantic conventions using OTel Weaver Forge."""
    
    config = GenerationConfig(
        registry_url=registry_url,
        output_dir=output_dir,
        language=language,
        template_dir=template_dir,
        force=force,
        verbose=verbose,
    )
    
    if verbose:
        rprint(f"[bold green]🔧 Configuration:[/bold green]")
        rprint(f"  Registry: {registry_url}")
        rprint(f"  Output: {output_dir}")
        rprint(f"  Language: {language}")
        rprint(f"  Templates: {template_dir or 'built-in'}")
    
    try:
        weaver = WeaverGen(config)
        result = weaver.generate()
        
        if result.success:
            rprint(f"[bold green]✅ Successfully generated {len(result.files)} files[/bold green]")
            
            if verbose:
                table = Table(title="Generated Files")
                table.add_column("File", style="cyan")
                table.add_column("Size", style="green")
                table.add_column("Type", style="blue")
                
                for file_info in result.files:
                    table.add_row(
                        str(file_info.path.relative_to(output_dir)),
                        file_info.size_formatted,
                        file_info.file_type
                    )
                
                console.print(table)
        else:
            rprint(f"[bold red]❌ Generation failed: {result.error}[/bold red]")
            raise typer.Exit(1)
            
    except Exception as e:
        rprint(f"[bold red]💥 Error: {e}[/bold red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def validate(
    registry_path: Path = typer.Argument(
        ...,
        help="Path to semantic convention registry to validate"
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Enable strict validation mode"
    ),
) -> None:
    """🔍 Validate semantic convention registry."""
    
    try:
        weaver = WeaverGen()
        result = weaver.validate_registry(registry_path, strict=strict)
        
        if result.valid:
            rprint(f"[bold green]✅ Registry validation passed[/bold green]")
            if result.warnings:
                rprint(f"[yellow]⚠️  {len(result.warnings)} warnings found[/yellow]")
                for warning in result.warnings:
                    rprint(f"  [yellow]•[/yellow] {warning}")
        else:
            rprint(f"[bold red]❌ Registry validation failed[/bold red]")
            for error in result.errors:
                rprint(f"  [red]•[/red] {error}")
            raise typer.Exit(1)
            
    except Exception as e:
        rprint(f"[bold red]💥 Validation error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def templates(
    list_all: bool = typer.Option(
        False,
        "--list", "-l",
        help="List all available templates"
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        help="Filter templates by language"
    ),
) -> None:
    """📋 Manage and list available templates."""
    
    try:
        weaver = WeaverGen()
        available_templates = weaver.list_templates(language_filter=language)
        
        if not available_templates:
            rprint("[yellow]No templates found[/yellow]")
            return
        
        table = Table(title="Available Templates")
        table.add_column("Language", style="cyan")
        table.add_column("Template", style="green")
        table.add_column("Description", style="blue")
        table.add_column("Version", style="magenta")
        
        for template in available_templates:
            table.add_row(
                template.language,
                template.name,
                template.description,
                template.version
            )
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[bold red]💥 Error listing templates: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(
        False,
        "--show",
        help="Show current configuration"
    ),
    weaver_path: Optional[Path] = typer.Option(
        None,
        "--weaver-path",
        help="Set path to OTel Weaver binary"
    ),
) -> None:
    """⚙️ Configure WeaverGen settings."""
    
    if show:
        weaver = WeaverGen()
        config_data = weaver.get_config()
        
        rprint("[bold green]🔧 WeaverGen Configuration:[/bold green]")
        rprint(f"  Weaver Binary: {config_data.weaver_path}")
        rprint(f"  Default Templates: {config_data.template_dir}")
        rprint(f"  Cache Directory: {config_data.cache_dir}")
        
    if weaver_path:
        weaver = WeaverGen()
        weaver.set_weaver_path(weaver_path)
        rprint(f"[green]✅ Weaver path updated to: {weaver_path}[/green]")


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version information"
    ),
) -> None:
    """🌟 WeaverGen: Python wrapper for OTel Weaver Forge with Claude Code optimization."""
    
    if version:
        from . import __version__
        rprint(f"[bold cyan]WeaverGen v{__version__}[/bold cyan]")
        rprint("🌟 Python wrapper for OTel Weaver Forge")
        raise typer.Exit()


if __name__ == "__main__":
    app()
