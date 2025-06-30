#!/usr/bin/env python3
"""
Weaver 80/20 CLI Wrapper

This wrapper implements the 20% of Weaver commands that provide 80% of the value.
"""

import typer
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import sys
import json
import yaml

# Add output directory to path
sys.path.append("output")

from runtime.forge import (
    weaver_registry_check,
    weaver_registry_generate,
    weaver_registry_resolve,
    weaver_registry_stats
)

app = typer.Typer(
    name="weaver80",
    help="🎯 80/20 Weaver CLI - Essential commands only",
    no_args_is_help=True
)

console = Console()

@app.command()
def check(
    registry: Path = typer.Argument(..., help="Registry path"),
    strict: bool = typer.Option(False, "--strict", help="Strict validation")
) -> None:
    """✅ Check registry validity (Most used command)."""
    try:
        is_valid, errors = weaver_registry_check(str(registry))
        if is_valid:
            rprint("[green]✅ Registry is valid[/green]")
        else:
            rprint("[red]❌ Registry validation failed:[/red]")
            for error in errors or []:
                rprint(f"  • {error}")
            raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def generate(
    target: str = typer.Argument(..., help="Target language"),
    registry: Path = typer.Argument(..., help="Registry path"),
    output: Path = typer.Option(Path("./generated"), "-o", "--output"),
    templates: Optional[Path] = typer.Option(None, "-t", "--templates"),
    param: Optional[List[str]] = typer.Option(None, "-p", "--param", help="key=value")
) -> None:
    """🚀 Generate code from registry (Core functionality)."""
    try:
        # Parse parameters
        params = {}
        if param:
            for p in param:
                if "=" in p:
                    key, value = p.split("=", 1)
                    params[key] = value
        
        files = weaver_registry_generate(
            registry_path=str(registry),
            target_name=target,
            template_path=str(templates) if templates else "templates",
            output_dir=str(output),
            params=params
        )
        
        rprint(f"[green]✅ Generated {len(files)} files[/green]")
        for f in files[:5]:
            rprint(f"  • {f}")
        if len(files) > 5:
            rprint(f"  ... and {len(files)-5} more")
            
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def resolve(
    registry: Path = typer.Argument(..., help="Registry path"),
    format: str = typer.Option("yaml", "-f", "--format", help="Output format"),
    output: Optional[Path] = typer.Option(None, "-o", "--output")
) -> None:
    """🔄 Resolve registry references."""
    try:
        resolved = weaver_registry_resolve(
            registry_path=str(registry),
            output_path=str(output) if output else None,
            format=format
        )
        
        if not output:
            if format == "json":
                rprint(json.dumps(resolved, indent=2))
            else:
                rprint(yaml.dump(resolved, default_flow_style=False))
        else:
            rprint(f"[green]✅ Resolved registry written to {output}[/green]")
            
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def stats(
    registry: Path = typer.Argument(..., help="Registry path")
) -> None:
    """📊 Show registry statistics."""
    try:
        stats = weaver_registry_stats(str(registry))
        
        table = Table(title="Registry Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key, str(value))
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def quick(
    registry: Path = typer.Argument(..., help="Registry path")
) -> None:
    """⚡ Quick check + generate Python (80% use case)."""
    rprint("[cyan]Running quick workflow (check + generate)...[/cyan]\n")
    
    # Check first
    try:
        is_valid, errors = weaver_registry_check(str(registry))
        if is_valid:
            rprint("[green]✅ Registry is valid[/green]")
        else:
            rprint("[red]❌ Registry invalid, aborting[/red]")
            raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Check failed: {e}[/red]")
        raise typer.Exit(1)
    
    # Then generate
    try:
        files = weaver_registry_generate(
            registry_path=str(registry),
            target_name="python",
            template_path="templates",
            output_dir="quick_output"
        )
        rprint(f"\n[green]✅ Generated {len(files)} Python files[/green]")
    except Exception as e:
        rprint(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
