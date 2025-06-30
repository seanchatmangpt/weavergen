#!/usr/bin/env python3
"""
Generated Weaver CLI implementation from semantic conventions.

This implements the 80/20 Weaver commands based on semantic definitions.
"""

import typer
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from opentelemetry import trace
import sys
import json
import yaml
import time

# Add runtime to path
sys.path.append("output")
from runtime.forge import (
    weaver_registry_check,
    weaver_registry_generate,
    weaver_registry_resolve,
    weaver_registry_stats,
)

app = typer.Typer(
    name="weaver",
    help="🌟 Generated Weaver CLI with 80/20 commands",
    no_args_is_help=True
)

console = Console()
tracer = trace.get_tracer("weaver.cli")

# Generated commands from semantic conventions






@app.command()
def check(
    path: str = typer.Argument(
        ...,
        help="Path to the registry to check"
    ),
    strict: Optional[bool] = typer.Option(
        False,
        "--strict",
        help="Enable strict validation mode"
    ),
) -> None:
    """Validate a semantic convention registry for correctness"""
    
    with tracer.start_span("weaver.registry.check") as span:
        # Set span attributes
        
        
        
        span.set_attribute("registry.check.path", path)
        
        
        
        
        
        span.set_attribute("registry.check.strict", strict)
        
        
        
        
        
        
        try:
            
            # Registry check implementation
            is_valid, errors = weaver_registry_check(path)
            
            span.set_attribute("weaver.registry.check.valid", is_valid)
            if errors:
                span.set_attribute("weaver.registry.check.errors", errors)
            
            if is_valid:
                rprint("[green]✅ Registry is valid[/green]")
            else:
                rprint("[red]❌ Registry validation failed:[/red]")
                for error in errors or []:
                    rprint(f"  • {error}")
                raise typer.Exit(1)
                
            
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            rprint(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)








@app.command()
def generate(
    registry_path: str = typer.Argument(
        ...,
        help="Path to the semantic convention registry"
    ),
    target: str = typer.Argument(
        ...,
        help="Target language or format for generation"
    ),
    output_dir: Optional[str] = typer.Option(
        "./generated",
        "--output-dir", "-o",
        help="Output directory for generated files"
    ),
    template_path: Optional[str] = typer.Option(
        None,
        "--template-path",
        help="Path to custom templates"
    ),
    params: Optional[str] = typer.Option(
        None,
        "--params",
        help="Additional parameters passed to templates (JSON format)"
    ),
) -> None:
    """Generate code or documentation from a semantic convention registry"""
    
    with tracer.start_span("weaver.registry.generate") as span:
        # Set span attributes
        span.set_attribute("registry.generate.registry_path", registry_path)
        span.set_attribute("registry.generate.target", target)
        span.set_attribute("registry.generate.template_path", template_path)
        span.set_attribute("registry.generate.output_dir", output_dir)
        if params:
            span.set_attribute("registry.generate.params", str(params))
        
        
        
        
        
        try:
            
            # Registry generate implementation
            params_dict = {}
            if params:
                # params is JSON string - convert to dict
                try:
                    params_dict = json.loads(params)
                except json.JSONDecodeError:
                    rprint("[red]Error: --params must be valid JSON[/red]")
                    raise typer.Exit(1)
            
            files = weaver_registry_generate(
                registry_path=registry_path,
                target_name=target,
                template_path=template_path or "templates",
                output_dir=output_dir,
                params=params_dict
            )
            
            span.set_attribute("weaver.registry.generate.files_count", len(files))
            if files:
                span.set_attribute("weaver.registry.generate.files", files[:10])  # First 10
            
            rprint(f"[green]✅ Generated {len(files)} files[/green]")
            for f in files[:5]:
                rprint(f"  • {f}")
            if len(files) > 5:
                rprint(f"  ... and {len(files)-5} more")
                
            
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            rprint(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)








@app.command()
def resolve(
    registry_path: str = typer.Argument(
        ...,
        help="Path to the registry to resolve"
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        help="Output format for resolved registry"
    ),
    output_path: Optional[str] = typer.Option(
        None,
        "--output-path",
        help="Path to write resolved output"
    ),
) -> None:
    """Resolve references and merge semantic conventions"""
    
    with tracer.start_span("weaver.registry.resolve") as span:
        # Set span attributes
        
        
        
        span.set_attribute("registry.resolve.registry_path", registry_path)
        
        
        
        
        
        span.set_attribute("registry.resolve.format", format)
        
        
        
        
        
        span.set_attribute("registry.resolve.output_path", output_path)
        
        
        
        
        
        
        
        
        
        try:
            
            # Registry resolve implementation
            resolved = weaver_registry_resolve(
                registry_path=registry_path,
                output_path=output_path,
                format=format or "yaml"
            )
            
            groups_count = len(resolved.get("groups", []))
            span.set_attribute("weaver.registry.resolve.groups_count", groups_count)
            
            if not output_path:
                if format == "json":
                    rprint(json.dumps(resolved, indent=2))
                else:
                    rprint(yaml.dump(resolved, default_flow_style=False))
            else:
                rprint(f"[green]✅ Resolved registry written to {output_path}[/green]")
                
            
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            rprint(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)








@app.command()
def stats(
    registry_path: str = typer.Argument(
        ...,
        help="Path to the registry"
    ),
    stable_count: Optional[int] = typer.Option(
        None,
        "--stable-count",
        help="Number of stable definitions"
    ),
    experimental_count: Optional[int] = typer.Option(
        None,
        "--experimental-count",
        help="Number of experimental definitions"
    ),
) -> None:
    """Generate statistics about a semantic convention registry"""
    
    with tracer.start_span("weaver.registry.stats") as span:
        # Set span attributes
        span.set_attribute("registry.stats.registry_path", registry_path)
        if stable_count is not None:
            span.set_attribute("registry.stats.stable_count", stable_count)
        if experimental_count is not None:
            span.set_attribute("registry.stats.experimental_count", experimental_count)
        
        
        
        
        try:
            
            # Registry stats implementation
            stats = weaver_registry_stats(registry_path)
            
            # Extract key stats
            total_groups = int(stats.get("Total groups", 0))
            total_attributes = int(stats.get("Total attributes", 0))
            
            span.set_attribute("weaver.registry.stats.total_groups", total_groups)
            span.set_attribute("weaver.registry.stats.total_attributes", total_attributes)
            
            table = Table(title="Registry Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in stats.items():
                table.add_row(key, str(value))
            
            console.print(table)
            
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            rprint(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)






# Multi-command operations










@app.command()
def multi_generate(
    registry_path: str = typer.Argument(..., help="Path to the registry"),
    languages: List[str] = typer.Option(
        ["python", "go", "rust"],
        "--language", "-l",
        help="Target languages"
    ),
    parallel: bool = typer.Option(
        True,
        "--parallel/--sequential",
        help="Generate in parallel"
    ),
) -> None:
    """Generate code for multiple languages in parallel"""
    
    with tracer.start_span("weaver.multi.generate") as span:
        span.set_attribute("multi.generate.registry_path", registry_path)
        span.set_attribute("multi.generate.languages", languages)
        span.set_attribute("multi.generate.parallel", parallel)
        
        start_time = time.time()
        total_files = 0
        
        try:
            import concurrent.futures
            
            def generate_for_lang(lang):
                return weaver_registry_generate(
                    registry_path=registry_path,
                    target_name=lang,
                    template_path="templates",
                    output_dir=f"generated/{lang}"
                )
            
            if parallel:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = {executor.submit(generate_for_lang, lang): lang 
                              for lang in languages}
                    
                    for future in concurrent.futures.as_completed(futures):
                        lang = futures[future]
                        try:
                            files = future.result()
                            total_files += len(files)
                            rprint(f"[green]✓ {lang}: {len(files)} files[/green]")
                        except Exception as e:
                            rprint(f"[red]✗ {lang}: {e}[/red]")
            else:
                for lang in languages:
                    try:
                        files = generate_for_lang(lang)
                        total_files += len(files)
                        rprint(f"[green]✓ {lang}: {len(files)} files[/green]")
                    except Exception as e:
                        rprint(f"[red]✗ {lang}: {e}[/red]")
            
            duration_ms = int((time.time() - start_time) * 1000)
            span.set_attribute("multi.generate.total_files", total_files)
            span.set_attribute("multi.generate.duration_ms", duration_ms)
            
            rprint(f"\n[bold green]✨ Generated {total_files} files in {duration_ms}ms[/bold green]")
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            rprint(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)



# Quick command for 80% use case
@app.command()
def quick(
    registry_path: str = typer.Argument(..., help="Registry path")
) -> None:
    """⚡ Quick check + generate Python (80% use case)."""
    
    with tracer.start_span("weaver.quick") as span:
        span.set_attribute("registry_path", registry_path)
        
        # Check
        ctx = typer.Context()
        ctx.invoke(check, path=registry_path)
        
        # Generate
        ctx.invoke(generate, 
                  registry_path=registry_path,
                  target="python")
        
        rprint("[bold green]✨ Quick workflow complete![/bold green]")

if __name__ == "__main__":
    app()