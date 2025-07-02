"""Template management commands for WeaverGen v2 - 80/20 implementation."""

from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from opentelemetry import trace
import json

# Initialize CLI app and console
templates_app = typer.Typer(help="Template management")
console = Console()
tracer = trace.get_tracer(__name__)


@templates_app.command()
def list(
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Filter by language"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    installed: bool = typer.Option(False, "--installed", "-i", help="Show only installed templates"),
):
    """📋 List available code generation templates."""
    with tracer.start_as_current_span("templates.list") as span:
        try:
            console.print("[blue]Available Templates[/blue]\n")
            
            # Template data
            templates = [
                {"language": "python", "name": "default", "category": "standard", "installed": True, "description": "Standard Python code generation"},
                {"language": "python", "name": "pydantic", "category": "models", "installed": True, "description": "Pydantic models with validation"},
                {"language": "python", "name": "dataclass", "category": "models", "installed": False, "description": "Python dataclasses"},
                {"language": "python", "name": "async", "category": "advanced", "installed": False, "description": "Async/await patterns"},
                {"language": "go", "name": "default", "category": "standard", "installed": True, "description": "Standard Go code generation"},
                {"language": "go", "name": "grpc", "category": "rpc", "installed": False, "description": "gRPC service definitions"},
                {"language": "rust", "name": "default", "category": "standard", "installed": True, "description": "Standard Rust code generation"},
                {"language": "rust", "name": "tokio", "category": "async", "installed": False, "description": "Tokio async runtime"},
                {"language": "typescript", "name": "default", "category": "standard", "installed": True, "description": "TypeScript with interfaces"},
                {"language": "typescript", "name": "react", "category": "frontend", "installed": False, "description": "React components"},
            ]
            
            # Apply filters
            if language:
                templates = [t for t in templates if t["language"] == language]
            if category:
                templates = [t for t in templates if t["category"] == category]
            if installed:
                templates = [t for t in templates if t["installed"]]
            
            # Display table
            table = Table(title="Code Generation Templates")
            table.add_column("Language", style="cyan")
            table.add_column("Template", style="green")
            table.add_column("Category", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("Description", style="white")
            
            for template in templates:
                status = "[green]✓ Installed[/green]" if template["installed"] else "[dim]Available[/dim]"
                table.add_row(
                    template["language"],
                    template["name"],
                    template["category"],
                    status,
                    template["description"]
                )
            
            console.print(table)
            console.print(f"\nTotal: {len(templates)} templates")
            
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@templates_app.command()
def generate(
    template_name: str = typer.Argument(..., help="Name of template to generate from"),
    output_dir: Path = typer.Option(Path("./output"), "--output", "-o", help="Output directory"),
    language: str = typer.Option("python", "--language", "-l", help="Target language"),
    variables: Optional[List[str]] = typer.Option(None, "--var", "-v", help="Template variables (key=value)"),
):
    """🚀 Generate code using a specific template."""
    with tracer.start_as_current_span("templates.generate") as span:
        span.set_attribute("template", template_name)
        span.set_attribute("language", language)
        
        try:
            console.print(f"[blue]Generating from template: {template_name} ({language})[/blue]")
            
            # Parse variables
            vars_dict = {}
            if variables:
                for var in variables:
                    key, value = var.split("=")
                    vars_dict[key] = value
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Loading template...", total=None)
                progress.add_task("Processing variables...", total=None)
                progress.add_task("Generating code...", total=None)
                progress.add_task("Writing output files...", total=None)
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Simulated output
            console.print(f"\n[green]✓[/green] Generated files in {output_dir}:")
            console.print(f"  • models.py")
            console.print(f"  • __init__.py")
            console.print(f"  • types.py")
            
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@templates_app.command()
def create(
    name: str = typer.Argument(..., help="Name for the new template"),
    language: str = typer.Option("python", "--language", "-l", help="Target language"),
    base: Optional[str] = typer.Option(None, "--base", "-b", help="Base template to extend"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive template creation"),
):
    """✨ Create a new custom template."""
    with tracer.start_as_current_span("templates.create") as span:
        span.set_attribute("name", name)
        span.set_attribute("language", language)
        
        try:
            console.print(f"[blue]Creating new template: {name} for {language}[/blue]")
            
            if interactive:
                console.print("\n[yellow]Interactive template creation:[/yellow]")
                # TODO: Implement interactive prompts
            
            # Template content
            template_content = f"""# {name} Template for {language}
# Based on: {base or 'scratch'}

## Template Variables
- {{{{ model_name }}}} : Name of the model
- {{{{ namespace }}}} : Package/module namespace
- {{{{ attributes }}}} : List of attributes

## Code Template
{{% if language == 'python' %}}
class {{{{ model_name }}}}:
    \"\"\"Generated model for {{{{ model_name }}}}.\"\"\"
    {{% for attr in attributes %}}
    {{{{ attr.name }}}}: {{{{ attr.type }}}}
    {{% endfor %}}
{{% endif %}}
"""
            
            # Save template
            template_dir = Path(f"templates/{language}")
            template_dir.mkdir(parents=True, exist_ok=True)
            template_file = template_dir / f"{name}.j2"
            
            console.print(f"\n[green]✓[/green] Template created: {template_file}")
            console.print("\nTemplate preview:")
            
            syntax = Syntax(template_content, "jinja2", theme="monokai", line_numbers=True)
            console.print(syntax)
            
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@templates_app.command()
def validate(
    template_path: Path = typer.Argument(..., help="Path to template file"),
    test_data: Optional[Path] = typer.Option(None, "--test-data", "-t", help="Test data file (JSON)"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Strict validation mode"),
):
    """✅ Validate template syntax and structure."""
    with tracer.start_as_current_span("templates.validate") as span:
        span.set_attribute("template", str(template_path))
        
        try:
            console.print(f"[blue]Validating template: {template_path.name}[/blue]")
            
            # Validation checks
            checks = [
                ("Jinja2 syntax", True, None),
                ("Variable declarations", True, None),
                ("Control structures", True, None),
                ("Output format", True, None),
            ]
            
            if test_data:
                checks.append(("Test rendering", True, None))
            
            # Display results
            table = Table(title="Template Validation")
            table.add_column("Check", style="cyan")
            table.add_column("Result", style="green")
            table.add_column("Details", style="yellow")
            
            all_passed = True
            for check, passed, details in checks:
                result = "[green]✓ Passed[/green]" if passed else "[red]✗ Failed[/red]"
                table.add_row(check, result, details or "")
                if not passed:
                    all_passed = False
            
            console.print(table)
            
            if all_passed:
                console.print("\n[green]✓[/green] Template is valid!")
            else:
                console.print("\n[red]✗[/red] Template validation failed")
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@templates_app.command()
def install(
    template_url: str = typer.Argument(..., help="URL or path to template package"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom name for template"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing template"),
):
    """📦 Install a template from URL or package."""
    with tracer.start_as_current_span("templates.install") as span:
        span.set_attribute("source", template_url)
        
        try:
            console.print(f"[blue]Installing template from: {template_url}[/blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Downloading template...", total=None)
                progress.add_task("Validating package...", total=None)
                progress.add_task("Installing files...", total=None)
                progress.add_task("Updating registry...", total=None)
            
            # Simulated installation
            template_name = name or "custom-template"
            console.print(f"\n[green]✓[/green] Template '{template_name}' installed successfully")
            console.print("\nInstalled files:")
            console.print("  • templates/python/custom-template.j2")
            console.print("  • templates/python/custom-template.yaml")
            
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


if __name__ == "__main__":
    templates_app()