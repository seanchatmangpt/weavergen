"""Direct Weaver binary commands for WeaverGen v2."""

from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Import real Weaver integration
from ..weaver_integration import (
    WeaverIntegration, WeaverConfig, WeaverTarget,
    WeaverValidationResult, WeaverGenerationResult, WeaverRegistryInfo
)

# Initialize CLI app and console
weaver_app = typer.Typer(help="Direct Weaver binary commands")
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


@weaver_app.command()
def version():
    """Show Weaver version."""
    with tracer.start_as_current_span("weaver.version") as span:
        try:
            weaver = get_weaver_integration()
            version = weaver.get_weaver_version()
            console.print(f"[blue]Weaver version: {version}[/blue]")
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@weaver_app.command()
def check(
    registry_path: Path = typer.Argument(..., help="Path to semantic convention registry"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Enable strict validation mode"),
    future: bool = typer.Option(True, "--future", "-f", help="Enable future validation rules"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode")
):
    """Validate a semantic convention registry using Weaver."""
    with tracer.start_as_current_span("weaver.check") as span:
        span.set_attribute("registry", str(registry_path))
        span.set_attribute("strict", strict)
        
        try:
            weaver = get_weaver_integration()
            
            # Configure validation mode
            if strict:
                weaver.config.future_validation = True
            if future:
                weaver.config.future_validation = True
            if quiet:
                weaver.config.quiet = True
            
            # Validate using real Weaver
            result = weaver.check_registry(registry_path, strict=strict)
            
            # Display results
            if result.valid:
                console.print("[green]✓[/green] Registry validation passed!")
                
                # Show warnings if any
                if result.warnings and not quiet:
                    console.print("\n[yellow]Warnings:[/yellow]")
                    for warning in result.warnings:
                        console.print(f"  [yellow]•[/yellow] {warning}")
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[red]✗[/red] Validation errors found:")
                for error in result.errors:
                    console.print(f"  [red]•[/red] {error}")
                
                # Show warnings too
                if result.warnings and not quiet:
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


@weaver_app.command()
def stats(
    registry_path: Path = typer.Argument(..., help="Path to semantic convention registry"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output in JSON format")
):
    """Get detailed statistics about a semantic convention registry."""
    with tracer.start_as_current_span("weaver.stats") as span:
        span.set_attribute("registry", str(registry_path))
        
        try:
            weaver = get_weaver_integration()
            
            # Get registry statistics
            stats = weaver.get_registry_stats(registry_path)
            
            if stats.valid:
                if json_output:
                    # Output as JSON
                    output = {
                        "registry": str(registry_path),
                        "valid": stats.valid,
                        "groups": stats.groups_count,
                        "attributes": stats.attributes_count,
                        "metrics": stats.metrics_count,
                        "spans": stats.spans_count,
                        "resources": stats.resources_count,
                        "detailed_stats": stats.stats
                    }
                    console.print(json.dumps(output, indent=2))
                else:
                    # Pretty output
                    console.print(f"[blue]Registry Statistics for {registry_path.name}:[/blue]\n")
                    
                    # Display basic stats
                    console.print(f"📊 Groups: {stats.groups_count}")
                    console.print(f"🏷️  Attributes: {stats.attributes_count}")
                    console.print(f"📈 Metrics: {stats.metrics_count}")
                    console.print(f"🔗 Spans: {stats.spans_count}")
                    console.print(f"📦 Resources: {stats.resources_count}")
                    
                    # Display detailed stats if available
                    if stats.stats:
                        console.print(f"\n[blue]Detailed Statistics:[/blue]")
                        for key, value in stats.stats.items():
                            if isinstance(value, (int, float)):
                                console.print(f"  • {key}: {value}")
                            elif isinstance(value, dict):
                                console.print(f"  • {key}:")
                                for sub_key, sub_value in value.items():
                                    console.print(f"    - {sub_key}: {sub_value}")
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[red]Failed to get registry statistics[/red]")
                span.set_status(Status(StatusCode.ERROR, "Stats failed"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@weaver_app.command()
def resolve(
    registry_path: Path = typer.Argument(..., help="Path to semantic convention registry"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for resolved registry")
):
    """Resolve a semantic convention registry to a single file."""
    with tracer.start_as_current_span("weaver.resolve") as span:
        span.set_attribute("registry", str(registry_path))
        
        try:
            weaver = get_weaver_integration()
            
            # Resolve registry
            resolved_file = weaver.resolve_registry(registry_path, output_file)
            
            console.print(f"[green]✓[/green] Registry resolved successfully!")
            console.print(f"📁 Resolved file: {resolved_file}")
            
            # Show file size
            if resolved_file.exists():
                size = resolved_file.stat().st_size
                console.print(f"📏 File size: {size:,} bytes")
            
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@weaver_app.command()
def generate(
    registry_path: Path = typer.Argument(..., help="Path to semantic convention registry"),
    target: str = typer.Option("codegen_python", "--target", "-t", help="Generation target"),
    output_dir: Path = typer.Option(Path("./generated"), "--output", "-o", help="Output directory"),
    templates_dir: Optional[Path] = typer.Option(None, "--templates", help="Templates directory"),
    parameters: Optional[List[str]] = typer.Option(None, "--param", "-D", help="Template parameters (key=value)"),
    policies: Optional[List[Path]] = typer.Option(None, "--policy", "-p", help="Policy files"),
    skip_policies: bool = typer.Option(False, "--skip-policies", help="Skip policy validation"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Generate artifacts from a semantic convention registry."""
    with tracer.start_as_current_span("weaver.generate") as span:
        span.set_attribute("registry", str(registry_path))
        span.set_attribute("target", target)
        
        try:
            weaver = get_weaver_integration()
            
            # Map target string to WeaverTarget enum
            target_map = {
                "codegen_python": WeaverTarget.CODE_GEN_PYTHON,
                "codegen_go": WeaverTarget.CODE_GEN_GO,
                "codegen_rust": WeaverTarget.CODE_GEN_RUST,
                "codegen_java": WeaverTarget.CODE_GEN_JAVA,
                "codegen_typescript": WeaverTarget.CODE_GEN_TYPESCRIPT,
                "codegen_dotnet": WeaverTarget.CODE_GEN_DOTNET,
                "markdown": WeaverTarget.MARKDOWN,
                "json_schema": WeaverTarget.JSON_SCHEMA,
                "policy": WeaverTarget.POLICY,
            }
            
            weaver_target = target_map.get(target)
            if not weaver_target:
                console.print(f"[red]Unsupported target: {target}[/red]")
                console.print(f"Supported targets: {', '.join(target_map.keys())}")
                raise typer.Exit(1)
            
            # Parse parameters
            params_dict = {}
            if parameters:
                for param in parameters:
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params_dict[key] = value
            
            # Configure weaver
            if verbose:
                weaver.config.debug_level = 1
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                # Validate first
                progress.add_task("Validating registry...", total=None)
                validation_result = weaver.check_registry(registry_path, strict=False)
                
                if not validation_result.valid:
                    console.print("[red]Validation failed![/red]")
                    for error in validation_result.errors:
                        console.print(f"  • {error}")
                    span.set_status(Status(StatusCode.ERROR, "Validation failed"))
                    raise typer.Exit(1)
                
                # Generate
                progress.add_task(f"Generating {target}...", total=None)
                generation_result = weaver.generate_code(
                    registry_path=registry_path,
                    target=weaver_target,
                    output_dir=output_dir,
                    templates_dir=templates_dir,
                    parameters=params_dict,
                    policies=policies,
                    skip_policies=skip_policies
                )
                
                if generation_result.success:
                    console.print(f"[green]✓[/green] Generated {target} in {output_dir}")
                    
                    # Show generated files
                    if generation_result.generated_files:
                        console.print(f"\n[blue]Generated files ({len(generation_result.generated_files)}):[/blue]")
                        for file in generation_result.generated_files[:10]:  # Show first 10
                            console.print(f"  • {file}")
                        if len(generation_result.generated_files) > 10:
                            console.print(f"  • ... and {len(generation_result.generated_files) - 10} more")
                    
                    # Show diagnostics if any
                    if generation_result.diagnostics and verbose:
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


@weaver_app.command()
def targets():
    """List available Weaver generation targets."""
    with tracer.start_as_current_span("weaver.targets") as span:
        try:
            weaver = get_weaver_integration()
            
            # Get available targets
            targets = weaver.get_available_targets()
            
            # Display targets
            console.print(f"[blue]Available Weaver Targets ({len(targets)}):[/blue]\n")
            
            table = Table(title="Weaver Generation Targets")
            table.add_column("Target", style="cyan")
            table.add_column("Language/Type", style="green")
            table.add_column("Description", style="white")
            
            for target in targets:
                # Extract language from target name
                lang = target.value.replace("codegen_", "").title()
                if lang == "Json_schema":
                    lang = "JSON Schema"
                elif lang == "Gh_workflow_command":
                    lang = "GitHub Workflow"
                
                table.add_row(target.value, lang, f"Generate {lang} from semantic conventions")
            
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


@weaver_app.command()
def init(
    name: str = typer.Argument(..., help="Name of your semantic convention registry"),
    output_dir: Path = typer.Option(Path("./semantic_conventions"), help="Output directory for semantic conventions"),
    with_examples: bool = typer.Option(True, help="Include example semantic convention files")
):
    """Initialize a new semantic convention registry with starter YAML files."""
    with tracer.start_as_current_span("weaver.init") as span:
        span.set_attribute("registry_name", name)
        span.set_attribute("output_dir", str(output_dir))
        
        try:
            # Get Weaver integration
            weaver = get_weaver_integration()
            span.set_attribute("weaver.version", weaver.get_weaver_version())
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create registry manifest
            manifest_file = output_dir / "registry_manifest.yaml"
            manifest_content = f"""# WeaverGen Registry Manifest
registry:
  name: {name}
  version: "1.0.0"
  description: "Semantic convention registry for {name}"
  maintainers:
    - name: "WeaverGen"
      email: "weavergen@example.com"
  
  # Registry configuration
  config:
    future_validation: true
    strict_mode: false
    
  # Dependencies
  dependencies:
    - url: "https://github.com/open-telemetry/semantic-conventions.git[model]"
      version: "main"
      
  # Local semantic conventions
  conventions:
    - path: "./model"
      description: "Local semantic conventions"
"""
            
            manifest_file.write_text(manifest_content)
            console.print(f"[green]✓[/green] Created registry manifest: {manifest_file}")
            
            # Create model directory
            model_dir = output_dir / "model"
            model_dir.mkdir(exist_ok=True)
            
            # Create example semantic conventions if requested
            if with_examples:
                example_file = model_dir / f"{name}_common.yaml"
                example_content = f"""# {name} Common Semantic Conventions
groups:
  - id: {name}.service
    prefix: service
    type: attribute_group
    brief: 'Common service attributes for {name}'
    attributes:
      - id: name
        type: string
        requirement_level: required
        brief: 'Service name'
        examples: ['{name}-api', '{name}-worker']
      - id: version
        type: string
        requirement_level: recommended
        brief: 'Service version'
        examples: ['1.0.0', '2.1.3']
      - id: instance.id
        type: string
        requirement_level: recommended
        brief: 'Service instance identifier'
        examples: ['instance-1', 'pod-abc123']

  - id: {name}.operation
    prefix: operation
    type: span
    brief: 'Common operation attributes for {name}'
    attributes:
      - ref: {name}.service.name
      - id: duration_ms
        type: int
        requirement_level: recommended
        brief: 'Operation duration in milliseconds'
      - id: status
        type: string
        requirement_level: required
        brief: 'Operation status'
        examples: ['success', 'failure', 'timeout']
"""
                
                example_file.write_text(example_content)
                console.print(f"[green]✓[/green] Created example conventions: {example_file}")
            
            # Validate the registry using Weaver
            console.print(f"\n[blue]Validating registry with Weaver...[/blue]")
            validation_result = weaver.check_registry(output_dir, strict=False)
            
            if validation_result.valid:
                console.print("[green]✓[/green] Registry validation passed!")
                
                # Get registry statistics
                stats = weaver.get_registry_stats(output_dir)
                if stats.valid:
                    console.print(f"\n[blue]Registry Statistics:[/blue]")
                    console.print(f"  • Groups: {stats.groups_count}")
                    console.print(f"  • Attributes: {stats.attributes_count}")
                    console.print(f"  • Metrics: {stats.metrics_count}")
                    console.print(f"  • Spans: {stats.spans_count}")
                    console.print(f"  • Resources: {stats.resources_count}")
            else:
                console.print("[yellow]⚠[/yellow] Registry validation warnings:")
                for warning in validation_result.warnings:
                    console.print(f"  • {warning}")
            
            console.print(f"\n[green]✓[/green] Registry '{name}' initialized successfully!")
            console.print(f"📁 Registry location: {output_dir.absolute()}")
            console.print(f"🔧 Weaver version: {weaver.get_weaver_version()}")
            
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Registry initialization failed: {e}[/red]")
            raise typer.Exit(1)


if __name__ == "__main__":
    weaver_app() 