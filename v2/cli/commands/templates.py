"""
WeaverGen v2 Template Commands
Template management and generation functionality
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
from rich.syntax import Syntax

from ...core.engine.spiff_engine import WeaverGenV2Engine

app = typer.Typer(
    name="templates",
    help="Template management and operations",
    rich_markup_mode="rich"
)

console = Console()

@app.command("list")
def templates_list(
    ctx: typer.Context,
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Filter by language"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed information"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search templates")
):
    """List available templates"""
    
    async def run_list():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "list_config": {
                "category_filter": category,
                "language_filter": language,
                "search_query": search,
                "include_metadata": detailed
            },
            "cli_command": "templates list"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📋 Loading templates...", total=None)
            
            try:
                result = await engine.execute_workflow("list_templates", context)
                
                if result.success:
                    templates = result.final_data.get("templates", [])
                    progress.update(task, description="✅ Templates loaded")
                    
                    display_template_list(templates, detailed)
                else:
                    progress.update(task, description="❌ Failed to load templates")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Failed to load templates")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_list())

@app.command("generate")
def templates_generate(
    ctx: typer.Context,
    template_name: str = typer.Argument(help="Template name to use"),
    output: Path = typer.Option(Path("./generated"), "--output", "-o", help="Output path"),
    language: str = typer.Option("python", "--language", "-l", help="Target language"),
    variables: Optional[Path] = typer.Option(None, "--vars", "-v", help="Variables JSON file"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview without generating")
):
    """Generate code from template"""
    
    async def run_generate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        # Load variables if provided
        template_vars = {}
        if variables and variables.exists():
            with open(variables) as f:
                template_vars = json.load(f)
        
        context = {
            "template_name": template_name,
            "generation_config": {
                "output_path": str(output),
                "language": language,
                "variables": template_vars,
                "preview_mode": preview
            },
            "cli_command": "templates generate"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🎨 Generating from {template_name}...", total=None)
            
            try:
                result = await engine.execute_workflow("generate_from_template", context)
                
                if result.success:
                    generation_result = result.final_data.get("generation_result", {})
                    progress.update(task, description="✅ Generation complete")
                    
                    if preview:
                        display_template_preview(generation_result)
                    else:
                        display_generation_results(generation_result, output)
                else:
                    progress.update(task, description="❌ Generation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Generation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_generate())

@app.command("create")
def templates_create(
    ctx: typer.Context,
    name: str = typer.Argument(help="Template name"),
    template_type: str = typer.Option("code", "--type", "-t", help="Template type: code, config, doc"),
    base_template: Optional[str] = typer.Option(None, "--base", "-b", help="Base template to extend"),
    output_dir: Path = typer.Option(Path("./templates"), "--output", "-o"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive creation mode")
):
    """Create a new template"""
    
    async def run_create():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "template_name": name,
            "create_config": {
                "template_type": template_type,
                "base_template": base_template,
                "output_dir": str(output_dir),
                "interactive_mode": interactive
            },
            "cli_command": "templates create"
        }
        
        console.print(Panel(
            f"[bold blue]Creating Template[/bold blue]\n"
            f"Name: {name}\n"
            f"Type: {template_type}\n"
            f"Base: {base_template or 'None'}",
            title="Template Creation"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🛠️ Creating template...", total=None)
            
            try:
                result = await engine.execute_workflow("create_template", context)
                
                if result.success:
                    creation_result = result.final_data.get("creation_result", {})
                    progress.update(task, description="✅ Template created")
                    
                    display_creation_results(creation_result, name)
                else:
                    progress.update(task, description="❌ Template creation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Template creation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_create())

@app.command("validate")
def templates_validate(
    ctx: typer.Context,
    template_path: Path = typer.Argument(help="Template file to validate"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict validation"),
    test_data: Optional[Path] = typer.Option(None, "--test-data", "-t", help="Test data for validation")
):
    """Validate template syntax and structure"""
    
    async def run_validate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        # Load test data if provided
        test_vars = {}
        if test_data and test_data.exists():
            with open(test_data) as f:
                test_vars = json.load(f)
        
        context = {
            "template_path": str(template_path),
            "validation_config": {
                "strict_mode": strict,
                "test_variables": test_vars,
                "check_syntax": True,
                "check_variables": True,
                "check_output": bool(test_vars)
            },
            "cli_command": "templates validate"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Validating template...", total=None)
            
            try:
                result = await engine.execute_workflow("validate_template", context)
                
                if result.success:
                    validation_result = result.final_data.get("validation_result", {})
                    progress.update(task, description="✅ Validation complete")
                    
                    display_validation_results(validation_result, template_path)
                else:
                    progress.update(task, description="❌ Validation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Validation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_validate())

@app.command("install")
def templates_install(
    ctx: typer.Context,
    source: str = typer.Argument(help="Template source: URL, path, or package name"),
    template_dir: Path = typer.Option(Path("./templates"), "--dir", "-d", help="Installation directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing templates")
):
    """Install templates from external sources"""
    
    async def run_install():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "source": source,
            "install_config": {
                "template_dir": str(template_dir),
                "force_overwrite": force,
                "verify_integrity": True,
                "install_dependencies": True
            },
            "cli_command": "templates install"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"📦 Installing templates from {source}...", total=None)
            
            try:
                result = await engine.execute_workflow("install_templates", context)
                
                if result.success:
                    install_result = result.final_data.get("install_result", {})
                    progress.update(task, description="✅ Installation complete")
                    
                    display_install_results(install_result)
                else:
                    progress.update(task, description="❌ Installation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Installation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_install())

# Display helper functions

def display_template_list(templates: List[dict], detailed: bool):
    """Display list of templates"""
    if not templates:
        console.print("[yellow]No templates found[/yellow]")
        return
    
    if detailed:
        for template in templates:
            panel_content = f"[bold]{template['name']}[/bold]\n"
            panel_content += f"Category: {template.get('category', 'uncategorized')}\n"
            panel_content += f"Language: {template.get('language', 'any')}\n"
            panel_content += f"Version: {template.get('version', '1.0.0')}\n"
            panel_content += f"Description: {template.get('description', 'No description')}"
            
            console.print(Panel(panel_content, title=template['name']))
            
            if template.get('variables'):
                console.print("  Variables:")
                for var in template['variables']:
                    console.print(f"    • {var['name']} ({var['type']}): {var.get('description', '')}")
            console.print("")
    else:
        table = Table(title="Available Templates")
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Language", style="green")
        table.add_column("Description", style="yellow")
        
        for template in templates:
            table.add_row(
                template['name'],
                template.get('category', 'uncategorized'),
                template.get('language', 'any'),
                template.get('description', '')[:50] + "..." if len(template.get('description', '')) > 50 else template.get('description', '')
            )
        
        console.print(table)

def display_template_preview(result: dict):
    """Display template preview"""
    preview_content = result.get("preview_content", "")
    language = result.get("language", "text")
    
    console.print("[bold]Template Preview:[/bold]")
    syntax = Syntax(preview_content, language, theme="monokai", line_numbers=True)
    console.print(syntax)
    
    # Show variable substitutions
    substitutions = result.get("substitutions", {})
    if substitutions:
        console.print("\n[bold]Variable Substitutions:[/bold]")
        for var, value in substitutions.items():
            console.print(f"  {var}: {value}")

def display_generation_results(result: dict, output_path: Path):
    """Display template generation results"""
    files_generated = result.get("files_generated", [])
    
    table = Table(title="Generated Files")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Status", style="magenta")
    
    for file_info in files_generated:
        table.add_row(
            file_info['name'],
            f"{file_info.get('size', 0)} bytes",
            "✅ Created" if file_info.get('created', False) else "📝 Updated"
        )
    
    console.print(table)
    console.print(f"\n[green]Files generated in: {output_path}[/green]")

def display_creation_results(result: dict, template_name: str):
    """Display template creation results"""
    console.print(Panel(
        f"[bold green]Template Created Successfully![/bold green]\n"
        f"Name: {template_name}\n"
        f"Location: {result.get('template_path', 'unknown')}\n"
        f"Files Created: {result.get('file_count', 0)}",
        title="Creation Summary"
    ))
    
    # Show created files
    files = result.get("created_files", [])
    if files:
        console.print("\n[bold]Created Files:[/bold]")
        for file in files:
            console.print(f"  • {file}")
    
    # Show next steps
    console.print("\n[bold]Next Steps:[/bold]")
    console.print(f"  1. Edit the template at: {result.get('template_path', '')}")
    console.print(f"  2. Test with: weavergen templates generate {template_name} --preview")
    console.print(f"  3. Validate with: weavergen templates validate {result.get('template_path', '')}")

def display_validation_results(result: dict, template_path: Path):
    """Display template validation results"""
    valid = result.get("valid", False)
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    
    status_color = "green" if valid else "red"
    status_text = "VALID" if valid else "INVALID"
    
    console.print(Panel(
        f"[bold {status_color}]Template {status_text}[/bold {status_color}]\n"
        f"File: {template_path.name}\n"
        f"Errors: {len(errors)}\n"
        f"Warnings: {len(warnings)}",
        title="Validation Result"
    ))
    
    if errors:
        console.print("\n[red]Errors:[/red]")
        for error in errors:
            console.print(f"  ❌ Line {error.get('line', '?')}: {error['message']}")
    
    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  ⚠️  Line {warning.get('line', '?')}: {warning['message']}")
    
    # Test output if available
    test_output = result.get("test_output")
    if test_output:
        console.print("\n[bold]Test Output Preview:[/bold]")
        syntax = Syntax(test_output[:500], "text", theme="monokai")
        console.print(syntax)

def display_install_results(result: dict):
    """Display template installation results"""
    installed_count = result.get("installed_count", 0)
    updated_count = result.get("updated_count", 0)
    failed_count = result.get("failed_count", 0)
    
    table = Table(title="Installation Summary")
    table.add_column("Action", style="cyan")
    table.add_column("Count", style="green")
    
    table.add_row("Installed", str(installed_count))
    table.add_row("Updated", str(updated_count))
    table.add_row("Failed", str(failed_count))
    
    console.print(table)
    
    # Show installed templates
    installed_templates = result.get("installed_templates", [])
    if installed_templates:
        console.print("\n[bold]Installed Templates:[/bold]")
        for template in installed_templates[:10]:
            console.print(f"  • {template['name']} v{template.get('version', '1.0.0')}")

if __name__ == "__main__":
    app()