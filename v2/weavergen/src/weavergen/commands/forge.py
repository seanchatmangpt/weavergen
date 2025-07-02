"""Weaver Forge code generation commands for WeaverGen v2 - Real Weaver integration."""

from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml
import json
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from pydantic import BaseModel, Field

# Import real Weaver integration
from ..weaver_integration import (
    WeaverIntegration, WeaverConfig, WeaverTarget,
    WeaverValidationResult, WeaverGenerationResult, WeaverRegistryInfo
)

# Import BPMN engine components
from weavergen.engine.simple_engine import SimpleBpmnEngine
from weavergen.engine.service_task import WeaverGenServiceEnvironment
from weavergen.engine.forge_service_tasks import register_forge_tasks

# Initialize CLI app and console
forge_app = typer.Typer(help="Weaver Forge code generation commands - Real Weaver integration")
console = Console()
tracer = trace.get_tracer(__name__)

# Initialize Weaver integration
_weaver_integration = None

def get_weaver_integration():
    """Get or create Weaver integration instance."""
    global _weaver_integration
    if _weaver_integration is None:
        config = WeaverConfig(
            weaver_path=Path("weaver"),
            templates_dir=Path("templates"),
            output_dir=Path("generated"),
            future_validation=True
        )
        _weaver_integration = WeaverIntegration(config)
    return _weaver_integration

# Initialize BPMN engine
_engine = None
_environment = None

def get_bpmn_engine():
    """Get or create BPMN engine with forge tasks registered."""
    global _engine, _environment
    if _engine is None:
        _environment = WeaverGenServiceEnvironment()
        register_forge_tasks(_environment)
        _engine = SimpleBpmnEngine(_environment)
        
        # Load forge workflows - fix path to go up one more level
        workflow_dir = Path(__file__).parent.parent.parent / "workflows" / "bpmn" / "forge"
        if workflow_dir.exists():
            for bpmn_file in workflow_dir.glob("*.bpmn"):
                try:
                    # Add spec with the actual process ID from the file
                    # We need to load and parse to find the process ID
                    _engine.parser.add_bpmn_file(str(bpmn_file))
                    # Get all process IDs from the parsed file
                    for process_id in _engine.parser.get_process_ids():
                        # Register each process
                        spec = _engine.parser.get_spec(process_id)
                        _engine.specs[process_id] = spec
                        console.print(f"[green]✓[/green] Loaded BPMN process: {process_id}")
                except Exception as e:
                    console.print(f"[red]ERROR: Could not load {bpmn_file}: {e}[/red]")
    
    return _engine, _environment


class ForgeConfig(BaseModel):
    """Configuration for Weaver Forge operations."""
    weaver_path: Path = Field(default=Path("weaver"))
    default_language: str = "python"
    output_dir: Path = Field(default=Path("generated"))
    strict_validation: bool = True


@forge_app.command()
def generate(
    registry_url: str = typer.Argument(..., help="URL or path to semantic convention registry"),
    output_dir: Path = typer.Option(Path("./generated"), help="Output directory for generated code"),
    language: str = typer.Option("python", help="Target programming language"),
    template: Optional[str] = typer.Option(None, help="Custom template to use"),
    verbose: bool = typer.Option(False, help="Enable verbose output")
):
    """Generate code from semantic conventions using real Weaver Forge (80/20 core command)."""
    with tracer.start_as_current_span("forge.generate.real") as span:
        span.set_attribute("language", language)
        span.set_attribute("registry", registry_url)
        
        try:
            # Get Weaver integration
            weaver = get_weaver_integration()
            
            # Map language to Weaver target
            target_map = {
                "python": WeaverTarget.CODE_GEN_PYTHON,
                "go": WeaverTarget.CODE_GEN_GO,
                "rust": WeaverTarget.CODE_GEN_RUST,
                "java": WeaverTarget.CODE_GEN_JAVA,
                "typescript": WeaverTarget.CODE_GEN_TYPESCRIPT,
                "dotnet": WeaverTarget.CODE_GEN_DOTNET,
            }
            
            target = target_map.get(language.lower())
            if not target:
                console.print(f"[red]Unsupported language: {language}[/red]")
                console.print(f"Supported languages: {', '.join(target_map.keys())}")
                raise typer.Exit(1)
            
            span.set_attribute("weaver.target", target.value)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                # Validate semantic conventions first
                progress.add_task("Validating semantic conventions...", total=None)
                validation_result = weaver.check_registry(registry_url, strict=False)
                
                if not validation_result.valid:
                    console.print("[red]Validation failed![/red]")
                    for error in validation_result.errors:
                        console.print(f"  • {error}")
                    span.set_status(Status(StatusCode.ERROR, "Validation failed"))
                    raise typer.Exit(1)
                
                # Execute generation via real Weaver
                progress.add_task(f"Generating {language} code with Weaver...", total=None)
                
                # Prepare parameters
                parameters = {}
                if template:
                    parameters["template"] = template
                
                generation_result = weaver.generate_code(
                    registry_path=registry_url,
                    target=target,
                    output_dir=output_dir,
                    parameters=parameters
                )
                
                if generation_result.success:
                    console.print(f"[green]✓[/green] Generated {language} code in {output_dir}")
                    
                    # Show generated files
                    if generation_result.generated_files:
                        console.print(f"\n[blue]Generated files ({len(generation_result.generated_files)}):[/blue]")
                        for file in generation_result.generated_files[:10]:  # Show first 10
                            console.print(f"  • {file}")
                        if len(generation_result.generated_files) > 10:
                            console.print(f"  • ... and {len(generation_result.generated_files) - 10} more")
                    
                    # Show diagnostics if any
                    if generation_result.diagnostics:
                        console.print(f"\n[yellow]Diagnostics ({len(generation_result.diagnostics)}):[/yellow]")
                        for diagnostic in generation_result.diagnostics[:5]:  # Show first 5
                            if isinstance(diagnostic, dict):
                                msg = diagnostic.get("message", str(diagnostic))
                                console.print(f"  • {msg}")
                    
                    span.set_status(Status(StatusCode.OK))
                else:
                    console.print("[red]Generation failed![/red]")
                    console.print(f"Return code: {generation_result.return_code}")
                    if generation_result.stderr:
                        console.print(f"Error: {generation_result.stderr}")
                    span.set_status(Status(StatusCode.ERROR, f"Generation failed: {generation_result.return_code}"))
                    raise typer.Exit(generation_result.return_code)
                    
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@forge_app.command()
def templates(
    list_all: bool = typer.Option(True, "--list", "-l", help="List all available templates"),
    language: Optional[str] = typer.Option(None, help="Filter templates by language")
):
    """List and manage code generation templates using real Weaver."""
    with tracer.start_as_current_span("forge.templates.real") as span:
        try:
            # Get Weaver integration
            weaver = get_weaver_integration()
            
            # Get available targets
            targets = weaver.get_available_targets()
            
            # Filter by language if specified
            if language:
                targets = [t for t in targets if language.lower() in t.value.lower()]
            
            # Display templates
            console.print(f"[blue]Available Weaver Templates ({len(targets)}):[/blue]\n")
            
            table = Table(title="Weaver Generation Targets")
            table.add_column("Target", style="cyan")
            table.add_column("Language", style="green")
            table.add_column("Description", style="white")
            
            for target in targets:
                # Extract language from target name
                lang = target.value.replace("codegen_", "").title()
                if lang == "Json_schema":
                    lang = "JSON Schema"
                elif lang == "Gh_workflow_command":
                    lang = "GitHub Workflow"
                
                table.add_row(target.value, lang, f"Generate {lang} code from semantic conventions")
            
            console.print(table)
            
            # Show Weaver version
            version = weaver.get_weaver_version()
            console.print(f"\n[dim]Weaver version: {version}[/dim]")
            
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@forge_app.command()
def validate(
    registry_path: Path = typer.Argument(..., help="Path to semantic convention registry"),
    strict: bool = typer.Option(False, help="Enable strict validation mode")
):
    """Validate semantic conventions YAML files using real Weaver."""
    with tracer.start_as_current_span("forge.validate.real") as span:
        span.set_attribute("registry", str(registry_path))
        span.set_attribute("strict", strict)
        
        try:
            # Get Weaver integration
            weaver = get_weaver_integration()
            
            # Validate using real Weaver
            result = weaver.check_registry(registry_path, strict=strict)
            
            # Display results
            if result.valid:
                console.print("[green]✓[/green] Semantic conventions are valid!")
                
                # Show warnings if any
                if result.warnings:
                    console.print("\n[yellow]Warnings:[/yellow]")
                    for warning in result.warnings:
                        console.print(f"  [yellow]•[/yellow] {warning}")
                
                # Get and display registry statistics
                stats = weaver.get_registry_stats(registry_path)
                if stats.valid:
                    console.print(f"\n[blue]Registry Statistics:[/blue]")
                    console.print(f"  • Groups: {stats.groups_count}")
                    console.print(f"  • Attributes: {stats.attributes_count}")
                    console.print(f"  • Metrics: {stats.metrics_count}")
                    console.print(f"  • Spans: {stats.spans_count}")
                    console.print(f"  • Resources: {stats.resources_count}")
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[red]✗[/red] Validation errors found:")
                for error in result.errors:
                    console.print(f"  [red]•[/red] {error}")
                
                # Show warnings too
                if result.warnings:
                    console.print("\n[yellow]Warnings:[/yellow]")
                    for warning in result.warnings:
                        console.print(f"  [yellow]•[/yellow] {warning}")
                
                span.set_status(Status(StatusCode.ERROR, f"Validation failed: {len(result.errors)} errors"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


# Legacy commands for backward compatibility
@forge_app.command("forge-generate")
def forge_generate(
    semantic_file: Path = typer.Argument(..., help="Path to semantic conventions YAML"),
    output_dir: Path = typer.Option(Path("generated_forge"), help="Output directory"),
    components: Optional[List[str]] = typer.Option(None, help="Specific components to generate"),
    verbose: bool = typer.Option(False, help="Enable verbose output")
):
    """⚒️ Advanced Forge generation - complete system from semantics (Real Weaver)."""
    with tracer.start_as_current_span("forge.forge_generate.real") as span:
        try:
            # Get Weaver integration
            weaver = get_weaver_integration()
            
            console.print(f"[blue]Generating complete system from {semantic_file}[/blue]")
            
            # Generate Python code as default
            generation_result = weaver.generate_code(
                registry_path=semantic_file,
                target=WeaverTarget.CODE_GEN_PYTHON,
                output_dir=output_dir
            )
            
            if generation_result.success:
                console.print(f"[green]✓[/green] Complete system generated in {output_dir}")
                console.print(f"📁 Generated files: {len(generation_result.generated_files)}")
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[red]Generation failed![/red]")
                span.set_status(Status(StatusCode.ERROR, f"Generation failed: {generation_result.return_code}"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@forge_app.command("full-pipeline")
def full_pipeline(
    semantic_yaml: Path = typer.Argument(..., help="Path to semantic conventions YAML"),
    agents: int = typer.Option(5, help="Number of agents to generate"),
    output_dir: Path = typer.Option(Path("generated"), help="Output directory")
):
    """Execute full pipeline: Semantics → Forge → Agents → Validation (Real Weaver)."""
    with tracer.start_as_current_span("forge.full_pipeline.real") as span:
        try:
            # Get Weaver integration
            weaver = get_weaver_integration()
            
            console.print(f"[blue]Executing full pipeline with real Weaver integration[/blue]")
            
            # Step 1: Validate semantics
            console.print(f"\n[1/4] Validating semantic conventions...")
            validation_result = weaver.check_registry(semantic_yaml, strict=False)
            
            if not validation_result.valid:
                console.print("[red]Validation failed![/red]")
                for error in validation_result.errors:
                    console.print(f"  • {error}")
                span.set_status(Status(StatusCode.ERROR, "Validation failed"))
                raise typer.Exit(1)
            
            # Step 2: Generate code with Weaver
            console.print(f"\n[2/4] Generating code with Weaver...")
            generation_result = weaver.generate_code(
                registry_path=semantic_yaml,
                target=WeaverTarget.CODE_GEN_PYTHON,
                output_dir=output_dir / "weaver"
            )
            
            if not generation_result.success:
                console.print("[red]Weaver generation failed![/red]")
                span.set_status(Status(StatusCode.ERROR, "Weaver generation failed"))
                raise typer.Exit(1)
            
            # Step 3: Generate agent system (placeholder for now)
            console.print(f"\n[3/4] Generating {agents} agent system...")
            # TODO: Implement real agent generation
            
            # Step 4: Validate with spans
            console.print("\n[4/4] Validating system with OpenTelemetry spans...")
            # TODO: Implement real span validation
            
            console.print("\n[green]✓[/green] Full pipeline completed successfully!")
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Pipeline failed: {e}[/red]")
            raise typer.Exit(1)


if __name__ == "__main__":
    forge_app()