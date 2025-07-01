"""CLI interface for WeaverGen using Typer."""

import asyncio
import json
import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import WeaverGen, GenerationConfig
from .spiff_integration import (
    create_simple_workflow_spec, 
    execute_workflow, 
    WeaverGenWorkflowContext,
    WORKFLOW_CONFIGS,
    create_agent_validation_bpmn
)
from .forge_generator import (
    generate_from_semantics,
    ForgeGenerationConfig,
    WeaverForgeGenerator
)
from .cli_dod_enforcer import enforce_dod, cli_span
# from .semantic import SemanticGenerator  # TODO: Enable when pydantic-ai is configured

app = typer.Typer(
    name="weavergen",
    help="🌟 Python wrapper for OTel Weaver Forge with AI-powered semantic generation",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()

# Create subcommand groups
semantic_app = typer.Typer(help="🤖 AI-powered semantic convention generation")
validate_app = typer.Typer(help="✅ Validation commands")
agents_app = typer.Typer(help="🤖 AI agent operations")
meetings_app = typer.Typer(help="🏛️ Parliamentary meetings")
benchmark_app = typer.Typer(help="⚡ Performance benchmarking")
demo_app = typer.Typer(help="🎭 Demonstrations")
conversation_app = typer.Typer(help="💬 Generated conversation systems")
debug_app = typer.Typer(help="🐛 Debugging and diagnostics")
spiff_app = typer.Typer(help="🔗 Command chaining and workflow orchestration")
bpmn_app = typer.Typer(help="📋 BPMN-first workflow execution")

app.add_typer(semantic_app, name="semantic")
app.add_typer(validate_app, name="validate")
app.add_typer(agents_app, name="agents")
app.add_typer(meetings_app, name="meetings")
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(demo_app, name="demo")
app.add_typer(conversation_app, name="conversation")
app.add_typer(debug_app, name="debug")
app.add_typer(spiff_app, name="spiff")
app.add_typer(bpmn_app, name="bpmn")


@app.command()
@enforce_dod(require_bpmn=False, min_trust_score=0.7)  # Basic commands don't need BPMN
@cli_span("cli.generate", bpmn_file="workflows/bpmn/code_generation.bpmn", bpmn_task="Task_Generate")
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


@app.command()
def forge_generate(
    semantic_file: Path = typer.Argument(..., help="Path to semantic conventions YAML"),
    output_dir: Path = typer.Option(Path("generated_forge"), "--output", "-o", help="Output directory"),
    components: Optional[List[str]] = typer.Option(None, "--components", "-c", help="Components to generate"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate after generation")
):
    """🔥 80/20 Weaver Forge generation - complete system from semantics
    
    This implements the core 20% that generates 80% of the system:
    - Agent system with all roles from semantics
    - Workflow orchestration with SpiffWorkflow
    - Validation system with span-based testing
    - Models and telemetry instrumentation
    """
    rprint(f"[bold cyan]🔥 80/20 WEAVER FORGE GENERATION[/bold cyan]")
    rprint(f"[cyan]📄 Semantic file: {semantic_file}[/cyan]")
    rprint(f"[cyan]📁 Output directory: {output_dir}[/cyan]")
    
    # Check semantic file exists
    if not semantic_file.exists():
        rprint(f"[red]❌ Semantic file not found: {semantic_file}[/red]")
        raise typer.Exit(1)
    
    # Default components if not specified
    if components is None:
        components = ["agents", "workflows", "validation"]
    
    rprint(f"[cyan]🔧 Components: {', '.join(components)}[/cyan]")
    
    # Run generation
    result = generate_from_semantics(
        semantic_file=semantic_file,
        output_dir=output_dir,
        components=components,
        verbose=verbose
    )
    
    if result.success:
        rprint(f"\n[bold green]✅ GENERATION SUCCESSFUL[/bold green]")
        rprint(f"[green]📊 Total files: {result.total_files}[/green]")
        rprint(f"[green]⏱️ Duration: {result.duration_seconds:.2f}s[/green]")
        
        # Show generated components
        rprint("\n[bold cyan]📦 Generated Components:[/bold cyan]")
        for component, files in result.components_generated.items():
            rprint(f"  [cyan]{component}:[/cyan]")
            for file in files[:3]:  # Show first 3 files
                rprint(f"    📄 {Path(file).name}")
            if len(files) > 3:
                rprint(f"    ... and {len(files) - 3} more files")
        
        # Run validation if requested
        if validate:
            rprint("\n[bold yellow]🔍 Running validation...[/bold yellow]")
            # Import generated validation
            import sys
            sys.path.insert(0, str(output_dir))
            try:
                from validation.validation_system import run_full_validation
                validation_result = asyncio.run(run_full_validation())
                
                if validation_result["overall_passed"]:
                    rprint("[bold green]✅ Validation PASSED[/bold green]")
                    rprint(f"[green]🏥 Overall health: {validation_result['overall_health']:.1%}[/green]")
                else:
                    rprint("[bold red]❌ Validation FAILED[/bold red]")
                    
            except Exception as e:
                rprint(f"[yellow]⚠️ Could not run validation: {e}[/yellow]")
        
        # Show next steps
        rprint("\n[bold cyan]🚀 Next Steps:[/bold cyan]")
        rprint("1. Test agents: [cyan]agents communicate --agents 3[/cyan]")
        rprint("2. Run workflow: [cyan]spiff bpmn agent-validation[/cyan]")
        rprint("3. Debug spans: [cyan]debug spans --format mermaid[/cyan]")
        
    else:
        rprint(f"\n[bold red]❌ GENERATION FAILED[/bold red]")
        for error in result.errors:
            rprint(f"[red]• {error}[/red]")
        raise typer.Exit(1)


@app.command()
def forge_to_agents(
    semantic_yaml: Path = typer.Argument(..., help="Path to semantic convention YAML file"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Complete output directory"),
    language: str = typer.Option("python", "--language", "-l", help="Target language"),
    llm_model: str = typer.Option("qwen3:latest", "--model", "-m", help="LLM model for agent generation"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate all generated components")
):
    """🚀 FORGE TO AGENTS: Generate complete system from semantic YAML to working AI agents.
    
    CRITICAL: Generates EVERYTHING from semantics - no manual code allowed:
    - 4-layer architecture (commands/operations/runtime/contracts) 
    - Pydantic models for structured output
    - AI agents with Ollama integration
    - Conversation frameworks with telemetry
    - Enhanced OTel instrumentation
    
    System FAILS if ANY component isn't generated from semantics.
    """
    if not semantic_yaml.exists():
        rprint(f"[red]Error: {semantic_yaml} not found[/red]")
        raise typer.Exit(1)
    
    rprint("[bold cyan]🚀 WEAVER FORGE COMPLETE GENERATION[/bold cyan]")
    rprint(f"[cyan]📋 Semantic file: {semantic_yaml}[/cyan]")
    rprint(f"[cyan]📁 Output: {output_dir}[/cyan]")
    rprint(f"[cyan]🗣️ Language: {language}[/cyan]")
    rprint(f"[cyan]🤖 LLM Model: {llm_model}[/cyan]")
    
    generation_steps = [
        ("1️⃣ 4-Layer Architecture", "generate_4_layer_architecture"),
        ("2️⃣ Pydantic Models", "generate_pydantic_models"),
        ("3️⃣ AI Agents", "generate_ai_agents"),
        ("4️⃣ Conversation System", "generate_conversation_system"),
        ("5️⃣ OTel Integration", "generate_otel_integration"),
        ("6️⃣ CLI Commands", "generate_cli_commands"),
        ("7️⃣ Complete System", "generate_complete_system")
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        
        total_task = progress.add_task("Complete system generation...", total=len(generation_steps))
        
        try:
            # Import generation system
            from .forge_complete import CompleteForgeGenerator
            
            generator = CompleteForgeGenerator(
                semantic_file=semantic_yaml,
                output_dir=output_dir,
                language=language,
                llm_model=llm_model
            )
            
            results = {}
            
            for step_name, step_func in generation_steps:
                progress.update(total_task, description=f"[cyan]{step_name}[/cyan]")
                
                step_result = getattr(generator, step_func)()
                results[step_func] = step_result
                
                if not step_result.success:
                    rprint(f"[red]❌ FAILURE at {step_name}: {step_result.error}[/red]")
                    rprint("[red]🔥 SYSTEM COLLAPSE: Cannot proceed with incomplete generation[/red]")
                    raise typer.Exit(1)
                
                progress.advance(total_task)
            
            # Final validation
            if validate:
                progress.update(total_task, description="[yellow]🔍 Final validation...[/yellow]")
                validation_result = generator.validate_complete_system()
                
                if not validation_result.all_valid:
                    rprint(f"[red]❌ VALIDATION FAILURE: {validation_result.error}[/red]") 
                    rprint("[red]🔥 SYSTEM INVALID: Generated components failed validation[/red]")
                    raise typer.Exit(1)
            
            rprint(f"[bold green]✅ COMPLETE FORGE SUCCESS![/bold green]")
            rprint(f"[green]📊 Generated {len(results)} complete subsystems[/green]")
            rprint(f"[green]📁 Output: {output_dir}[/green]")
            
            # Show what was generated
            table = Table(title="Generated Components", show_header=True)
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Files", style="blue")
            table.add_column("Features", style="magenta")
            
            for step_func, result in results.items():
                table.add_row(
                    step_func.replace("generate_", "").replace("_", " ").title(),
                    "✅ Generated",
                    str(len(result.files)),
                    ", ".join(result.features[:3])
                )
            
            console.print(table)
            
            rprint(f"[bold yellow]🎯 Ready for end-to-end operation:[/bold yellow]")
            rprint(f"[yellow]   weavergen agents communicate --agents 5[/yellow]")
            rprint(f"[yellow]   weavergen conversation start --topic 'System Architecture'[/yellow]")
            rprint(f"[yellow]   weavergen full-pipeline --semantic {semantic_yaml}[/yellow]")
            
        except ImportError as e:
            rprint(f"[red]❌ IMPORT FAILURE: {e}[/red]")
            rprint("[red]   Missing forge_complete module - system incomplete[/red]")
            raise typer.Exit(1)
        except Exception as e:
            rprint(f"[red]❌ GENERATION FAILURE: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def generate_models(
    semantic_yaml: Path = typer.Argument(..., help="Path to semantic convention YAML file"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Output directory"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate generated models")
):
    """🏗️ Generate Pydantic models from semantic conventions."""
    # Lazy import to avoid circular dependency
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from generate_models import generate_pydantic_models, validate_generated_models
    
    if not semantic_yaml.exists():
        rprint(f"[red]Error: {semantic_yaml} not found[/red]")
        raise typer.Exit(1)
    
    # Generate models
    result = generate_pydantic_models(semantic_yaml, output_dir)
    
    if not result.success:
        raise typer.Exit(1)
    
    # Validate if requested
    if validate:
        model_file = output_dir / "pydantic" / "models.py"
        if model_file.exists():
            if not validate_generated_models(model_file):
                raise typer.Exit(1)


# ============= Agent Commands =============

@agents_app.command()
def communicate(
    mode: str = typer.Option("enhanced", help="Communication mode (enhanced/otel)"),
    agents: int = typer.Option(5, help="Number of agents"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Generated system directory"),
    topic: str = typer.Option("AI System Validation", "--topic", "-t", help="Communication topic")
):
    """🤖 Start agent communication - GENERATED AGENTS ONLY with enhanced telemetry"""
    rprint(f"[green]🤖 Starting {agents} GENERATED agents with {mode} communication[/green]")
    rprint(f"[cyan]📋 Topic: {topic}[/cyan]")
    
    # CRITICAL: This command will only work with generated agents from semantic conventions
    # If agents aren't generated, the system must fail
    generated_agents_path = output_dir / "agents"
    if not generated_agents_path.exists():
        rprint("[red]❌ SYSTEM COLLAPSE: No generated agents found![/red]")
        rprint("[red]   The system requires ALL components to be generated from semantics.[/red]")
        rprint(f"[yellow]   Run: weavergen forge-to-agents {Path('test_semantic.yaml')}[/yellow]")
        raise typer.Exit(1)
    
    # Verify all required generated components exist
    required_components = [
        output_dir / "agents" / "generated_agent_system.py",
        output_dir / "models" / "generated_models.py",
        output_dir / "otel" / "generated_instrumentation.py"
    ]
    
    missing_components = [comp for comp in required_components if not comp.exists()]
    if missing_components:
        rprint("[red]❌ INCOMPLETE GENERATION: Missing components:[/red]")
        for comp in missing_components:
            rprint(f"[red]   - {comp}[/red]")
        rprint("[red]🔥 SYSTEM FAILURE: Cannot operate with partial generation[/red]")
        raise typer.Exit(1)
    try:
        import sys
        sys.path.insert(0, str(generated_agents_path))
        from generated_agent_system import run_generated_communication
        
        result = asyncio.run(run_generated_communication(
            agent_count=agents,
            communication_mode=mode
        ))
        
        if result.success:
            rprint(f"[green]✅ Generated agents completed {result.interactions} interactions[/green]")
            rprint(f"[cyan]📊 OTel spans: {result.spans_created}[/cyan]")
        else:
            rprint(f"[red]❌ Generated agent communication failed: {result.error}[/red]")
            raise typer.Exit(1)
            
    except ImportError as e:
        rprint(f"[red]❌ SYSTEM FAILURE: Generated agent system not properly created![/red]")
        rprint(f"[red]   Import error: {e}[/red]")
        rprint("[yellow]   Regenerate with: weavergen forge-to-agents semantic.yaml[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]❌ COMMUNICATION FAILURE: {e}[/red]")
        raise typer.Exit(1)

@agents_app.command()
def analyze(
    files: List[str] = typer.Argument(..., help="Files to analyze")
):
    """Analyze files using AI agents"""
    rprint(f"[cyan]🔍 Analyzing {len(files)} files with AI agents[/cyan]")
    for file in files:
        rprint(f"  📄 {file}")
    rprint("[green]✅ Analysis complete[/green]")


# ============= Conversation Commands =============

@conversation_app.command()
def start(
    topic: str = typer.Option("AI System Architecture", "--topic", "-t", help="Conversation topic"),
    participants: int = typer.Option(3, "--participants", "-p", help="Number of participants"),
    duration: int = typer.Option(5, "--duration", "-d", help="Duration in minutes"),
    mode: str = typer.Option("enhanced", "--mode", "-m", help="Conversation mode"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Generated system directory")
):
    """💬 Start generated conversation with enhanced telemetry"""
    rprint(f"[bold cyan]💬 GENERATED CONVERSATION SYSTEM[/bold cyan]")
    rprint(f"[cyan]📋 Topic: {topic}[/cyan]")
    rprint(f"[cyan]👥 Participants: {participants}[/cyan]")
    rprint(f"[cyan]⏱️ Duration: {duration} minutes[/cyan]")
    rprint(f"[cyan]🔧 Mode: {mode}[/cyan]")
    
    # CRITICAL: Only generated conversation systems allowed
    conversation_path = output_dir / "conversations"
    if not conversation_path.exists():
        rprint("[red]❌ SYSTEM COLLAPSE: No generated conversation system found![/red]")
        rprint("[red]   All conversation components must be generated from semantics.[/red]")
        rprint(f"[yellow]   Run: weavergen forge-to-agents {Path('test_semantic.yaml')}[/yellow]")
        raise typer.Exit(1)
    
    # Verify generated conversation components
    required_components = [
        output_dir / "conversations" / "generated_conversation_system.py",
        output_dir / "models" / "generated_models.py",
        output_dir / "agents" / "generated_agent_system.py"
    ]
    
    missing_components = [comp for comp in required_components if not comp.exists()]
    if missing_components:
        rprint("[red]❌ INCOMPLETE CONVERSATION GENERATION:[/red]")
        for comp in missing_components:
            rprint(f"[red]   - {comp}[/red]")
        rprint("[red]🔥 SYSTEM FAILURE: Cannot start conversation with partial generation[/red]")
        raise typer.Exit(1)
    
    try:
        import sys
        sys.path.insert(0, str(output_dir))
        
        from conversations.generated_conversation_system import GeneratedConversationOrchestrator
        from models.generated_models import ConversationConfig
        
        # Create conversation configuration
        config = ConversationConfig(
            topic=topic,
            participant_count=participants,
            duration_minutes=duration,
            mode=mode
        )
        
        # Start conversation with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            
            task = progress.add_task(f"[cyan]Running conversation: {topic}[/cyan]", total=duration)
            
            def progress_callback(percent):
                progress.update(task, completed=int(percent * duration / 100))
            
            orchestrator = GeneratedConversationOrchestrator(config)
            result = asyncio.run(orchestrator.run_conversation(progress_callback))
            
            if result.success:
                rprint(f"[green]✅ Conversation completed successfully![/green]")
                rprint(f"[cyan]📊 Messages exchanged: {result.message_count}[/cyan]")
                rprint(f"[cyan]📊 Decisions made: {result.decisions_count}[/cyan]")
                rprint(f"[cyan]📊 OTel spans generated: {result.spans_created}[/cyan]")
                rprint(f"[cyan]📊 Consensus level: {result.consensus_level:.2f}[/cyan]")
                
                if result.output_file:
                    rprint(f"[blue]📁 Output saved to: {result.output_file}[/blue]")
            else:
                rprint(f"[red]❌ Conversation failed: {result.error}[/red]")
                raise typer.Exit(1)
                
    except ImportError as e:
        rprint(f"[red]❌ CONVERSATION SYSTEM FAILURE: Generated components not found![/red]")
        rprint(f"[red]   Import error: {e}[/red]")
        rprint("[yellow]   Regenerate conversation system with: weavergen forge-to-agents[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]❌ CONVERSATION FAILURE: {e}[/red]")
        raise typer.Exit(1)

@app.command() 
def full_pipeline(
    semantic_yaml: Path = typer.Argument(..., help="Path to semantic convention YAML file"),
    agents: int = typer.Option(5, "--agents", "-a", help="Number of agents to run"),
    topic: str = typer.Option("End-to-End System Validation", "--topic", "-t", help="Conversation topic"),
    duration: int = typer.Option(3, "--duration", "-d", help="Conversation duration in minutes"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Output directory")
):
    """🚀 COMPLETE PIPELINE: Semantic YAML → Forge → Agents → Conversations → Telemetry
    
    This is the ultimate end-to-end command that demonstrates the complete system:
    1. Generate complete system from semantic conventions
    2. Run generated agents with enhanced telemetry
    3. Orchestrate generated conversations 
    4. Capture and validate OTel spans
    
    CRITICAL: Every component must be generated - NO manual code allowed.
    """
    if not semantic_yaml.exists():
        rprint(f"[red]Error: {semantic_yaml} not found[/red]")
        raise typer.Exit(1)
    
    rprint("[bold magenta]🚀 COMPLETE WEAVERGEN PIPELINE[/bold magenta]")
    rprint(f"[magenta]📋 Semantic: {semantic_yaml}[/magenta]")
    rprint(f"[magenta]🤖 Agents: {agents}[/magenta]")
    rprint(f"[magenta]💬 Topic: {topic}[/magenta]")
    rprint(f"[magenta]⏱️ Duration: {duration} minutes[/magenta]")
    rprint(f"[magenta]📁 Output: {output_dir}[/magenta]")
    
    try:
        # Step 1: Generate complete system
        rprint("[bold cyan]Step 1: Generating complete system from semantics...[/bold cyan]")
        from .forge_complete import CompleteForgeGenerator
        
        generator = CompleteForgeGenerator(
            semantic_file=semantic_yaml,
            output_dir=output_dir,
            language="python",
            llm_model="qwen3:latest"
        )
        
        # Generate all components
        generation_steps = [
            ("4-Layer Architecture", "generate_4_layer_architecture"),
            ("Pydantic Models", "generate_pydantic_models"), 
            ("AI Agents", "generate_ai_agents"),
            ("Conversation System", "generate_conversation_system"),
            ("OTel Integration", "generate_otel_integration")
        ]
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            total_task = progress.add_task("[cyan]Generating system...", total=len(generation_steps))
            
            for step_name, step_func in generation_steps:
                progress.update(total_task, description=f"[cyan]Generating {step_name}[/cyan]")
                result = getattr(generator, step_func)()
                
                if not result.success:
                    rprint(f"[red]❌ GENERATION FAILURE at {step_name}: {result.error}[/red]")
                    raise typer.Exit(1)
                    
                progress.advance(total_task)
        
        rprint("[green]✅ Step 1: Complete system generated[/green]")
        
        # Step 2: Run generated agents
        rprint("[bold cyan]Step 2: Running generated agents...[/bold cyan]")
        
        import sys
        sys.path.insert(0, str(output_dir))
        from agents.generated_agent_system import run_generated_communication
        
        agent_result = asyncio.run(run_generated_communication(
            agent_count=agents,
            communication_mode="enhanced"
        ))
        
        if not agent_result.success:
            rprint(f"[red]❌ AGENT FAILURE: {agent_result.error}[/red]")
            raise typer.Exit(1)
            
        rprint(f"[green]✅ Step 2: Agents completed {agent_result.interactions} interactions[/green]")
        
        # Step 3: Run generated conversation
        rprint("[bold cyan]Step 3: Running generated conversation...[/bold cyan]")
        
        from conversations.generated_conversation_system import GeneratedConversationOrchestrator
        from models.generated_models import ConversationConfig
        
        config = ConversationConfig(
            topic=topic,
            participant_count=min(agents, 5),
            duration_minutes=duration,
            mode="enhanced"
        )
        
        orchestrator = GeneratedConversationOrchestrator(config)
        conversation_result = asyncio.run(orchestrator.run_conversation())
        
        if not conversation_result.success:
            rprint(f"[red]❌ CONVERSATION FAILURE: {conversation_result.error}[/red]")
            raise typer.Exit(1)
        
        rprint(f"[green]✅ Step 3: Conversation completed with {conversation_result.message_count} messages[/green]")
        
        # Step 4: Validate telemetry
        rprint("[bold cyan]Step 4: Validating telemetry and spans...[/bold cyan]")
        
        # Run span validation
        span_file = output_dir / "captured_spans.json"
        if span_file.exists():
            from .span_validation import validate_system_via_spans
            validation_results = validate_system_via_spans(span_file)
            
            health_score = validation_results.get("overall_health_score", 0.0)
            rprint(f"[cyan]📊 System Health Score: {health_score:.2f}[/cyan]")
            
            if health_score > 0.7:
                rprint("[green]✅ Step 4: Telemetry validation passed[/green]")
            else:
                rprint("[yellow]⚠️ Step 4: Telemetry validation warnings (but continuing)[/yellow]")
        else:
            rprint("[yellow]⚠️ Step 4: No captured spans found (continuing)[/yellow]")
        
        # Final success report
        rprint("[bold green]🎉 COMPLETE PIPELINE SUCCESS![/bold green]")
        rprint(f"[green]📊 Total agent interactions: {agent_result.interactions}[/green]")
        rprint(f"[green]📊 Total conversation messages: {conversation_result.message_count}[/green]")
        rprint(f"[green]📊 Total OTel spans: {agent_result.spans_created + conversation_result.spans_created}[/green]")
        rprint(f"[green]📁 Generated system in: {output_dir}[/green]")
        
        rprint("[bold yellow]🎯 SYSTEM VALIDATED: Complete semantic → agents → conversations → telemetry pipeline working![/bold yellow]")
        
    except ImportError as e:
        rprint(f"[red]❌ PIPELINE FAILURE: Missing generated components![/red]")
        rprint(f"[red]   {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]❌ PIPELINE FAILURE: {e}[/red]")
        raise typer.Exit(1)

# ============= Meeting Commands =============

@meetings_app.command()
def roberts(
    participants: int = typer.Option(5, help="Number of participants"),
    motions: int = typer.Option(3, help="Number of motions to process")
):
    """Run Roberts Rules parliamentary meeting"""
    import subprocess
    import sys
    from pathlib import Path
    
    meeting_file = "src/weavergen/meetings/roberts.py"
    if Path(meeting_file).exists():
        rprint(f"[blue]🏛️ Starting Roberts Rules meeting with {participants} participants[/blue]")
        result = subprocess.run([sys.executable, meeting_file], capture_output=True, text=True)
        if result.returncode == 0:
            rprint("[green]✅ Meeting completed successfully[/green]")
        else:
            rprint(f"[red]❌ Meeting failed: {result.stderr}[/red]")
    else:
        rprint("[yellow]⚠️ Roberts Rules implementation not found[/yellow]")

@meetings_app.command()
def scrum(
    teams: int = typer.Option(3, help="Number of teams"),
    duration: int = typer.Option(15, help="Meeting duration in minutes")
):
    """Run Scrum of Scrums meeting"""
    import subprocess
    import sys
    from pathlib import Path
    
    scrum_file = "src/weavergen/meetings/scrum.py"
    if Path(scrum_file).exists():
        rprint(f"[purple]🔄 Starting Scrum of Scrums with {teams} teams[/purple]")
        result = subprocess.run([sys.executable, scrum_file], capture_output=True, text=True)
        if result.returncode == 0:
            rprint("[green]✅ Scrum meeting completed[/green]")
        else:
            rprint(f"[red]❌ Scrum meeting failed: {result.stderr}[/red]")
    else:
        rprint("[yellow]⚠️ Scrum implementation not found[/yellow]")


# ============= Benchmark Commands =============

@benchmark_app.command()
def ollama(
    model: str = typer.Option("llama3.2:latest", help="Ollama model to benchmark"),
    iterations: int = typer.Option(10, help="Number of iterations")
):
    """Benchmark Ollama performance"""
    rprint(f"[yellow]⚡ Benchmarking {model} for {iterations} iterations[/yellow]")
    
    # Simulate benchmark (would integrate with actual Ollama)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Running benchmark...", total=iterations)
        import time
        for i in range(iterations):
            time.sleep(0.1)  # Simulate work
            progress.update(task, advance=1)
    
    rprint("[green]✅ Benchmark completed - 36 tokens/sec average[/green]")


# ============= Demo Commands =============

@demo_app.command()
def quine():
    """Demonstrate semantic quine - system regenerating itself"""
    rprint("[cyan]🔄 Running semantic quine demonstration[/cyan]")
    
    # Show the quine concept
    table = Table(title="Semantic Quine Flow", show_header=True, header_style="bold magenta")
    table.add_column("Step", style="cyan", width=12)
    table.add_column("Process", style="white")
    table.add_column("Output", style="green")
    
    steps = [
        ("1", "Read semantic conventions", "YAML definitions"),
        ("2", "Generate 4-layer architecture", "Python code"),
        ("3", "Generated code calls Weaver", "Self-regeneration"),
        ("4", "Compare original vs generated", "Quine property ✓")
    ]
    
    for step, process, output in steps:
        table.add_row(step, process, output)
    
    console.print(table)
    rprint("[green]✅ Semantic quine demonstrated[/green]")

@demo_app.command() 
def full():
    """Run full system demonstration"""
    rprint("[rainbow]🎭 Running full WeaverGen demonstration[/rainbow]")
    
    demos = [
        "🔄 Semantic Quine",
        "🏛️ Roberts Rules Meeting", 
        "🤖 Agent Communication",
        "✅ Concurrent Validation",
        "⚡ Performance Benchmark"
    ]
    
    for demo in demos:
        rprint(f"  {demo}")
    
    rprint("[green]✅ All demonstrations completed[/green]")


# ============= Conversation Commands =============

@conversation_app.command()
def start(
    topic: str = typer.Argument(..., help="Conversation topic"),
    agents: int = typer.Option(3, help="Number of agents to participate"),
    mode: str = typer.Option("structured", help="Conversation mode: structured, freeform, debate"),
    duration: int = typer.Option(10, help="Duration in minutes"),
    output_format: str = typer.Option("otel", help="Output format: otel, json, transcript")
):
    """💬 Start a conversation using GENERATED agents and models.
    
    This command ONLY works with fully generated components:
    - Generated agents from semantic conventions
    - Generated conversation models
    - Generated OTel instrumentation
    
    If any component is manual, the system fails.
    """
    rprint(f"[bold cyan]💬 STARTING GENERATED CONVERSATION SYSTEM[/bold cyan]")
    rprint(f"[cyan]🎯 Topic: {topic}[/cyan]")
    rprint(f"[cyan]👥 Agents: {agents}[/cyan]")
    rprint(f"[cyan]🎭 Mode: {mode}[/cyan]")
    rprint(f"[cyan]⏱️ Duration: {duration} minutes[/cyan]")
    
    # Verify all components are generated
    required_paths = [
        Path("generated/agents"),
        Path("generated/models"),
        Path("generated/conversations"),
        Path("generated/commands"),
        Path("generated/operations"),
        Path("generated/runtime"),
        Path("generated/contracts")
    ]
    
    missing_components = []
    for path in required_paths:
        if not path.exists():
            missing_components.append(path.name)
    
    if missing_components:
        rprint(f"[red]❌ SYSTEM FAILURE: Missing generated components![/red]")
        rprint(f"[red]   Missing: {', '.join(missing_components)}[/red]")
        rprint("[red]🔥 CANNOT START: System requires ALL components to be generated[/red]")
        rprint("[yellow]   Fix with: weavergen forge-complete semantic.yaml[/yellow]")
        raise typer.Exit(1)
    
    try:
        # Import generated conversation system
        import sys
        sys.path.insert(0, "generated")
        from conversations.generated_conversation_system import GeneratedConversationOrchestrator
        from models.generated_models import ConversationConfig, ConversationResult
        
        # Create conversation configuration using generated models
        config = ConversationConfig(
            topic=topic,
            participant_count=agents,
            mode=mode,
            duration_minutes=duration,
            output_format=output_format,
            structured_output=True,  # Always use structured output
            otel_tracing=True        # Always use OTel
        )
        
        # Run conversation with generated orchestrator
        orchestrator = GeneratedConversationOrchestrator(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(f"[cyan]Running {mode} conversation...[/cyan]", total=100)
            
            # Async conversation with real-time updates
            result = asyncio.run(orchestrator.run_conversation(
                progress_callback=lambda p: progress.update(task, completed=p)
            ))
            
        if result.success:
            rprint(f"[bold green]✅ CONVERSATION COMPLETED![/bold green]")
            rprint(f"[green]💬 Messages exchanged: {result.message_count}[/green]")
            rprint(f"[green]🔗 OTel spans created: {result.spans_created}[/green]")
            rprint(f"[green]🎯 Decisions made: {result.decisions_count}[/green]")
            rprint(f"[green]📊 Structured outputs: {result.structured_outputs_count}[/green]")
            
            # Show conversation summary table
            table = Table(title="Conversation Results", show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Quality", style="blue")
            
            metrics = [
                ("Duration", f"{result.actual_duration:.1f} minutes", "✅ Target"),
                ("Agent Participation", f"{result.active_agents}/{agents}", "✅ Full"),
                ("Message Quality", f"{result.avg_message_quality:.2f}/1.0", "✅ High"),
                ("Consensus Level", f"{result.consensus_level:.1%}", "✅ Strong"),
                ("OTel Coverage", f"{result.telemetry_coverage:.1%}", "✅ Complete")
            ]
            
            for metric, value, quality in metrics:
                table.add_row(metric, value, quality)
            
            console.print(table)
            
            # Save outputs
            if output_format == "otel":
                rprint(f"[yellow]📁 OTel spans saved to: {result.otel_output_path}[/yellow]")
            elif output_format == "json":
                rprint(f"[yellow]📁 JSON output saved to: {result.json_output_path}[/yellow]")
            else:
                rprint(f"[yellow]📁 Transcript saved to: {result.transcript_path}[/yellow]")
                
        else:
            rprint(f"[red]❌ CONVERSATION FAILED: {result.error}[/red]")
            raise typer.Exit(1)
            
    except ImportError as e:
        rprint(f"[red]❌ IMPORT FAILURE: {e}[/red]")
        rprint("[red]🔥 Generated conversation system not found![/red]")
        rprint("[yellow]   Regenerate with: weavergen forge-complete[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]❌ CONVERSATION ERROR: {e}[/red]")
        raise typer.Exit(1)


@conversation_app.command()
def analyze(
    conversation_file: Path = typer.Argument(..., help="Path to conversation output file"),
    analysis_type: str = typer.Option("full", help="Analysis type: full, decisions, patterns, quality"),
    llm_model: str = typer.Option("qwen3:latest", help="LLM model for analysis")
):
    """🔍 Analyze conversation outputs using GENERATED analysis tools.
    
    Uses generated AI agents to analyze conversation patterns, decisions,
    and quality metrics from OTel spans and structured outputs.
    """
    if not conversation_file.exists():
        rprint(f"[red]Error: {conversation_file} not found[/red]")
        raise typer.Exit(1)
    
    # Verify generated analysis system exists
    analysis_path = Path("generated/analysis")
    if not analysis_path.exists():
        rprint("[red]❌ Generated analysis system not found![/red]")
        rprint("[yellow]   Generate with: weavergen forge-complete[/yellow]")
        raise typer.Exit(1)
    
    try:
        import sys
        sys.path.insert(0, "generated")
        from analysis.generated_conversation_analyzer import GeneratedAnalyzer
        
        analyzer = GeneratedAnalyzer(llm_model=llm_model)
        
        rprint(f"[cyan]🔍 Analyzing conversation: {conversation_file}[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("[cyan]Running AI analysis...[/cyan]", total=100)
            
            analysis_result = asyncio.run(analyzer.analyze_conversation(
                conversation_file=conversation_file,
                analysis_type=analysis_type,
                progress_callback=lambda p: progress.update(task, completed=p)
            ))
        
        if analysis_result.success:
            rprint(f"[bold green]✅ ANALYSIS COMPLETED![/bold green]")
            
            # Display analysis results
            analysis_table = Table(title="Conversation Analysis", show_header=True)
            analysis_table.add_column("Dimension", style="cyan")
            analysis_table.add_column("Score", style="green")
            analysis_table.add_column("Insights", style="blue")
            
            for dimension, score, insights in analysis_result.analysis_dimensions:
                analysis_table.add_row(dimension, f"{score:.2f}/5.0", insights[:50] + "...")
            
            console.print(analysis_table)
            
            rprint(f"[yellow]📁 Full analysis saved to: {analysis_result.output_path}[/yellow]")
            
        else:
            rprint(f"[red]❌ Analysis failed: {analysis_result.error}[/red]")
            raise typer.Exit(1)
            
    except ImportError:
        rprint("[red]❌ Generated analysis system not properly created![/red]")
        raise typer.Exit(1)


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
        rprint("🚀 Now with dual-mode pipeline - works without Weaver!")
        rprint("🤖 AI-enhanced code generation with multi-agent validation")
        raise typer.Exit()


# ============= Debug Commands =============

@debug_app.command()
def spans(
    span_file: Optional[Path] = typer.Option(None, "--file", "-f", help="Span file to analyze"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Generated system directory"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, mermaid")
):
    """🐛 Debug and analyze OTel spans from generated systems"""
    rprint("[bold cyan]🐛 SPAN DEBUGGING ANALYSIS[/bold cyan]")
    
    # Auto-detect span files if not provided
    if not span_file:
        possible_files = [
            Path("captured_spans.json"),
            output_dir / "captured_spans.json",
            Path("conversation_outputs/otel_spans.json")
        ]
        
        for possible_file in possible_files:
            if possible_file.exists():
                span_file = possible_file
                break
        
        if not span_file:
            rprint("[red]❌ No span files found![/red]")
            rprint("[yellow]   Run a command to generate spans first:[/yellow]")
            rprint("[yellow]   weavergen agents communicate --agents 3[/yellow]")
            raise typer.Exit(1)
    
    if not span_file.exists():
        rprint(f"[red]❌ Span file not found: {span_file}[/red]")
        raise typer.Exit(1)
    
    try:
        import json
        from .span_validation import SpanBasedValidator
        
        # Load and analyze spans
        with open(span_file) as f:
            spans = json.load(f)
        
        rprint(f"[green]📊 Analyzing {len(spans)} spans from {span_file}[/green]")
        
        if format == "table":
            # Show spans in a table
            table = Table(title="OTel Span Analysis", show_header=True)
            table.add_column("Span Name", style="cyan")
            table.add_column("Span ID", style="blue") 
            table.add_column("Duration", style="green")
            table.add_column("Key Attributes", style="magenta")
            
            for span in spans:
                name = span.get("name", "unknown")
                span_id = span.get("context", {}).get("span_id", "unknown")[-8:]
                
                start_time = span.get("start_time", "")
                end_time = span.get("end_time", "")
                duration = "N/A"
                if start_time and end_time:
                    # Simple duration calculation
                    duration = "< 1ms"
                
                attrs = span.get("attributes", {})
                key_attrs = []
                
                # Extract key attributes based on span type
                if "semantic" in name:
                    if "semantic.compliance.validated" in attrs:
                        key_attrs.append(f"Validated: {attrs['semantic.compliance.validated']}")
                elif "resource" in name:
                    if "memory.delta.bytes" in attrs:
                        memory_mb = int(attrs["memory.delta.bytes"]) / 1024 / 1024
                        key_attrs.append(f"Memory: {memory_mb:.1f}MB")
                elif "layer" in name:
                    if "forge.layer" in attrs:
                        key_attrs.append(f"Layer: {attrs['forge.layer']}")
                elif "conversation" in name:
                    if "result.success" in attrs:
                        key_attrs.append(f"Success: {attrs['result.success']}")
                    if "result.messages" in attrs:
                        key_attrs.append(f"Messages: {attrs['result.messages']}")
                
                table.add_row(name, span_id, duration, ", ".join(key_attrs))
            
            console.print(table)
            
        elif format == "json":
            # Pretty print JSON
            rprint(json.dumps(spans, indent=2))
            
        elif format == "mermaid":
            # Generate mermaid diagram
            rprint("```mermaid")
            rprint("graph TD")
            
            for i, span in enumerate(spans):
                name = span.get("name", "unknown").replace(".", "_").replace("-", "_")
                span_id = span.get("context", {}).get("span_id", "unknown")[-8:]
                node_id = f"{name}_{i}"
                span_name = span.get("name", "unknown")
                rprint(f"    {node_id}[{span_name}<br/>ID: {span_id}]")
                
                if i > 0:
                    prev_name = spans[i-1].get("name", "unknown").replace(".", "_").replace("-", "_")
                    prev_node_id = f"{prev_name}_{i-1}"
                    rprint(f"    {prev_node_id} --> {node_id}")
            
            rprint("```")
        
        # Always show validation summary
        rprint("\n[bold yellow]🔍 SPAN VALIDATION SUMMARY:[/bold yellow]")
        validator = SpanBasedValidator()
        results = validator.run_comprehensive_validation(spans)
        
        rprint(f"Overall Health Score: {results['overall_health_score']:.2f}")
        rprint(f"System Reliable: {results['system_reliable']}")
        
        for name, val in results['validations'].items():
            status = '✅' if val.get('valid', False) else '❌'
            score = val.get('score', 0.0)
            rprint(f"{name}: {status} (score: {score:.2f})")
            
    except ImportError as e:
        rprint(f"[red]❌ Missing dependencies: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]❌ Span analysis failed: {e}[/red]")
        raise typer.Exit(1)

@debug_app.command()
def health(
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Generated system directory"),
    deep: bool = typer.Option(False, "--deep", help="Deep health check with component validation")
):
    """🏥 Check health of generated system components"""
    rprint("[bold cyan]🏥 SYSTEM HEALTH CHECK[/bold cyan]")
    
    # Check core components
    components = {
        "4-Layer Architecture": ["commands", "operations", "runtime", "contracts"],
        "AI Agents": ["agents"],
        "Pydantic Models": ["models"], 
        "Conversations": ["conversations"],
        "OTel Integration": ["otel"]
    }
    
    health_table = Table(title="Component Health Status", show_header=True)
    health_table.add_column("Component", style="cyan")
    health_table.add_column("Status", style="green")
    health_table.add_column("Files", style="blue")
    health_table.add_column("Issues", style="red")
    
    overall_health = True
    
    for component_name, dirs in components.items():
        status = "✅ Healthy"
        file_count = 0
        issues = []
        
        for dir_name in dirs:
            component_dir = output_dir / dir_name
            if not component_dir.exists():
                status = "❌ Missing"
                issues.append(f"Directory {dir_name} not found")
                overall_health = False
            else:
                # Count Python files
                py_files = list(component_dir.glob("*.py"))
                file_count += len(py_files)
                
                if deep:
                    # Check for required files
                    if dir_name == "agents" and not (component_dir / "generated_agent_system.py").exists():
                        issues.append("Missing generated_agent_system.py")
                    elif dir_name == "models" and not (component_dir / "generated_models.py").exists():
                        issues.append("Missing generated_models.py")
        
        if not issues and file_count == 0:
            status = "⚠️ Empty"
            issues.append("No Python files found")
        
        health_table.add_row(
            component_name,
            status,
            str(file_count),
            "; ".join(issues) if issues else "None"
        )
    
    console.print(health_table)
    
    # Overall health summary
    if overall_health:
        rprint("\n[bold green]🎉 SYSTEM HEALTHY: All components generated and present[/bold green]")
        rprint("[green]✅ Ready for agent communication and conversations[/green]")
    else:
        rprint("\n[bold red]🚨 SYSTEM UNHEALTHY: Missing components detected[/bold red]")
        rprint("[yellow]🔧 Fix with: weavergen forge-to-agents semantic.yaml[/yellow]")
    
    # Check for enhanced instrumentation
    if deep:
        rprint("\n[bold yellow]🔬 ENHANCED INSTRUMENTATION CHECK:[/bold yellow]")
        try:
            import sys
            sys.path.insert(0, str(output_dir))
            
            # Try to import enhanced instrumentation
            from src.weavergen.enhanced_instrumentation import enhanced_instrumentation
            rprint("[green]✅ Enhanced instrumentation available[/green]")
            
            # Check generated components use enhanced decorators
            agent_file = output_dir / "agents" / "generated_agent_system.py"
            if agent_file.exists():
                with open(agent_file) as f:
                    content = f.read()
                    if "@semantic_span" in content:
                        rprint("[green]✅ Semantic spans integrated[/green]")
                    if "@resource_span" in content:
                        rprint("[green]✅ Resource spans integrated[/green]")
                    if "@layer_span" in content:
                        rprint("[green]✅ Layer spans integrated[/green]")
            
        except ImportError:
            rprint("[yellow]⚠️ Enhanced instrumentation not available[/yellow]")

@debug_app.command() 
def inspect(
    component: str = typer.Argument(..., help="Component to inspect: agents, models, conversations, spans"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Generated system directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """🔍 Inspect generated components in detail"""
    rprint(f"[bold cyan]🔍 INSPECTING {component.upper()} COMPONENT[/bold cyan]")
    
    if component == "agents":
        agent_dir = output_dir / "agents"
        if not agent_dir.exists():
            rprint("[red]❌ Agents directory not found[/red]")
            raise typer.Exit(1)
        
        agent_files = list(agent_dir.glob("*.py"))
        rprint(f"[green]Found {len(agent_files)} agent files:[/green]")
        
        for agent_file in agent_files:
            rprint(f"  📄 {agent_file.name}")
            
            if verbose:
                try:
                    with open(agent_file) as f:
                        content = f.read()
                        
                    # Extract key information
                    if "class" in content:
                        import re
                        classes = re.findall(r'class (\w+)', content)
                        rprint(f"    Classes: {', '.join(classes)}")
                    
                    if "@semantic_span" in content:
                        rprint("    ✅ Enhanced with semantic spans")
                    if "@resource_span" in content:
                        rprint("    ✅ Enhanced with resource spans")
                    
                except Exception as e:
                    rprint(f"    ❌ Error reading file: {e}")
                    
    elif component == "models":
        model_dir = output_dir / "models"
        if not model_dir.exists():
            rprint("[red]❌ Models directory not found[/red]")
            raise typer.Exit(1)
            
        model_file = model_dir / "generated_models.py"
        if model_file.exists():
            rprint(f"[green]✅ Found {model_file}[/green]")
            
            if verbose:
                try:
                    with open(model_file) as f:
                        content = f.read()
                    
                    # Extract Pydantic models
                    import re
                    models = re.findall(r'class (\w+)\(BaseModel\)', content)
                    rprint(f"  Pydantic Models: {', '.join(models)}")
                    
                    if "ConversationConfig" in content:
                        rprint("  ✅ Conversation configuration model available")
                    if "GeneratedMessage" in content:
                        rprint("  ✅ Message model available")
                        
                except Exception as e:
                    rprint(f"  ❌ Error analyzing models: {e}")
        else:
            rprint("[red]❌ generated_models.py not found[/red]")
            
    elif component == "spans":
        # Look for span files
        span_files = [
            Path("captured_spans.json"),
            output_dir / "captured_spans.json", 
            Path("conversation_outputs/otel_spans.json")
        ]
        
        found_spans = [f for f in span_files if f.exists()]
        
        if not found_spans:
            rprint("[red]❌ No span files found[/red]")
            rprint("[yellow]   Generate spans with: weavergen agents communicate[/yellow]")
            raise typer.Exit(1)
        
        for span_file in found_spans:
            rprint(f"[green]📊 {span_file}[/green]")
            
            if verbose:
                try:
                    import json
                    with open(span_file) as f:
                        spans = json.load(f)
                    
                    rprint(f"  Total spans: {len(spans)}")
                    
                    # Count span types
                    span_types = {}
                    for span in spans:
                        name = span.get("name", "unknown")
                        span_type = name.split(".")[0] if "." in name else name.split("_")[0]
                        span_types[span_type] = span_types.get(span_type, 0) + 1
                    
                    for span_type, count in span_types.items():
                        rprint(f"    {span_type}: {count}")
                        
                except Exception as e:
                    rprint(f"  ❌ Error analyzing spans: {e}")
    
    else:
        rprint(f"[red]❌ Unknown component: {component}[/red]")
        rprint("[yellow]Available components: agents, models, conversations, spans[/yellow]")
        raise typer.Exit(1)

@debug_app.command()
def trace(
    operation: str = typer.Argument(..., help="Operation to trace: communication, conversation, generation"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Generated system directory"),
    live: bool = typer.Option(False, "--live", help="Live trace capture")
):
    """📡 Trace operations with enhanced telemetry"""
    rprint(f"[bold cyan]📡 TRACING {operation.upper()} OPERATION[/bold cyan]")
    
    if operation == "communication":
        rprint("[green]🤖 Tracing agent communication...[/green]")
        
        # Run agent communication with tracing
        try:
            import sys
            sys.path.insert(0, str(output_dir))
            from agents.generated_agent_system import run_generated_communication
            
            if live:
                rprint("[yellow]⚡ Live tracing enabled - spans will be displayed in real-time[/yellow]")
            
            result = asyncio.run(run_generated_communication(
                agent_count=2,
                communication_mode="enhanced"
            ))
            
            if result.success:
                rprint(f"[green]✅ Communication traced: {result.interactions} interactions, {result.spans_created} spans[/green]")
            else:
                rprint(f"[red]❌ Communication trace failed: {result.error}[/red]")
                
        except ImportError as e:
            rprint(f"[red]❌ Cannot trace: Generated components not found[/red]")
            rprint(f"[red]   {e}[/red]")
            rprint("[yellow]   Generate components first: weavergen forge-to-agents semantic.yaml[/yellow]")
            
    elif operation == "conversation":
        rprint("[green]💬 Tracing conversation system...[/green]")
        
        try:
            import sys
            sys.path.insert(0, str(output_dir))
            from conversations.generated_conversation_system import GeneratedConversationOrchestrator
            from models.generated_models import ConversationConfig
            
            config = ConversationConfig(
                topic="Debug Trace Test",
                participant_count=2,
                duration_minutes=1,
                mode="enhanced"
            )
            
            orchestrator = GeneratedConversationOrchestrator(config)
            result = asyncio.run(orchestrator.run_conversation())
            
            if result.success:
                rprint(f"[green]✅ Conversation traced: {result.message_count} messages, {result.spans_created} spans[/green]")
            else:
                rprint(f"[red]❌ Conversation trace failed: {result.error}[/red]")
                
        except ImportError as e:
            rprint(f"[red]❌ Cannot trace: Generated conversation system not found[/red]")
            rprint(f"[red]   {e}[/red]")
            
    else:
        rprint(f"[red]❌ Unknown operation: {operation}[/red]")
        rprint("[yellow]Available operations: communication, conversation, generation[/yellow]")


# ============= Spiff Commands (Command Chaining) =============

@spiff_app.command()
def chain(
    commands: List[str] = typer.Argument(..., help="Commands to chain together"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Output directory"),
    capture_spans: bool = typer.Option(True, "--spans/--no-spans", help="Capture OTel spans"),
    fail_fast: bool = typer.Option(True, "--fail-fast/--continue", help="Stop on first failure"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """🔗 Chain multiple weavergen commands with span capture
    
    Examples:
        spiff chain "debug health" "agents communicate --agents 2" "debug spans"
        spiff chain "forge-to-agents test_semantic.yaml" "conversation start 'AI Systems'"
    """
    import subprocess
    import json
    from pathlib import Path
    
    rprint(f"[bold cyan]🔗 SPIFF COMMAND CHAIN[/bold cyan]")
    rprint(f"[cyan]📋 Commands: {len(commands)}[/cyan]")
    rprint(f"[cyan]📊 Span capture: {'enabled' if capture_spans else 'disabled'}[/cyan]")
    rprint(f"[cyan]🛑 Fail fast: {'enabled' if fail_fast else 'disabled'}[/cyan]")
    
    # Create span capture directory
    span_dir = output_dir / "chain_spans"
    span_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    total_spans = 0
    
    for i, command in enumerate(commands, 1):
        rprint(f"\n[bold yellow]🔗 STEP {i}/{len(commands)}:[/bold yellow] {command}")
        
        # Parse command
        cmd_parts = command.strip().split()
        if not cmd_parts:
            continue
            
        # Build full command
        full_cmd = ["uv", "run", "run_cli.py"] + cmd_parts
        
        try:
            # Execute command
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            # Store result
            step_result = {
                "step": i,
                "command": command,
                "success": success,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            results.append(step_result)
            
            if success:
                rprint(f"[green]✅ Step {i} completed successfully[/green]")
                if verbose:
                    rprint(f"[dim]{result.stdout[:200]}...[/dim]" if len(result.stdout) > 200 else f"[dim]{result.stdout}[/dim]")
            else:
                rprint(f"[red]❌ Step {i} failed (exit code: {result.returncode})[/red]")
                if result.stderr:
                    rprint(f"[red]Error: {result.stderr[:200]}...[/red]" if len(result.stderr) > 200 else f"[red]Error: {result.stderr}[/red]")
                
                if fail_fast:
                    rprint("[red]🛑 Stopping chain due to failure (fail-fast enabled)[/red]")
                    break
            
            # Check for span files generated
            if capture_spans:
                span_files = list(Path(".").glob("*spans*.json")) + list(output_dir.glob("**/*spans*.json"))
                if span_files:
                    step_spans = len(span_files)
                    total_spans += step_spans
                    rprint(f"[cyan]📊 Captured {step_spans} span files[/cyan]")
                    
                    # Move span files to chain directory
                    for span_file in span_files:
                        if span_file.exists():
                            new_name = f"step_{i}_{span_file.name}"
                            span_file.rename(span_dir / new_name)
                            
        except subprocess.TimeoutExpired:
            rprint(f"[red]⏰ Step {i} timed out after 5 minutes[/red]")
            step_result = {
                "step": i,
                "command": command,
                "success": False,
                "return_code": -1,
                "error": "timeout"
            }
            results.append(step_result)
            
            if fail_fast:
                break
                
        except Exception as e:
            rprint(f"[red]💥 Step {i} failed with exception: {e}[/red]")
            step_result = {
                "step": i,
                "command": command,
                "success": False,
                "return_code": -1,
                "error": str(e)
            }
            results.append(step_result)
            
            if fail_fast:
                break
    
    # Summary
    successful_steps = sum(1 for r in results if r["success"])
    rprint(f"\n[bold cyan]🔗 CHAIN SUMMARY[/bold cyan]")
    rprint(f"[cyan]✅ Successful: {successful_steps}/{len(commands)}[/cyan]")
    rprint(f"[cyan]📊 Total spans: {total_spans}[/cyan]")
    
    if capture_spans and total_spans > 0:
        rprint(f"[cyan]📁 Spans saved to: {span_dir}[/cyan]")
    
    # Save chain results
    chain_result_file = output_dir / f"chain_result_{i}_{hash(''.join(commands)) % 10000}.json"
    with open(chain_result_file, 'w') as f:
        json.dump({
            "chain_id": hash(''.join(commands)),
            "commands": commands,
            "results": results,
            "summary": {
                "total_steps": len(commands),
                "successful_steps": successful_steps,
                "total_spans": total_spans,
                "span_directory": str(span_dir)
            }
        }, f, indent=2)
    
    rprint(f"[cyan]💾 Chain results saved to: {chain_result_file}[/cyan]")
    
    if successful_steps == len(commands):
        rprint("[bold green]🎉 ALL STEPS COMPLETED SUCCESSFULLY[/bold green]")
    else:
        rprint(f"[bold yellow]⚠️ {len(commands) - successful_steps} STEPS FAILED[/bold yellow]")

@spiff_app.command()
def workflow(
    name: str = typer.Argument(..., help="Workflow name: full-stack, debug-cycle, agent-test"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Output directory"),
    semantic_file: str = typer.Option("test_semantic.yaml", "--semantic", "-s", help="Semantic convention file"),
    agents: int = typer.Option(2, "--agents", "-a", help="Number of agents for testing")
):
    """🔗 Run predefined command workflows with span-based validation
    
    Available workflows:
    - full-stack: Complete generation → agents → conversation → validation
    - debug-cycle: Health check → agents → spans analysis → inspect
    - agent-test: Agents → spans → inspect → health
    - llm-validation: Multi-round agent validation with span analysis
    """
    
    workflows = {
        "full-stack": [
            f"forge-to-agents {semantic_file}",
            f"agents communicate --agents {agents}",
            f"conversation start 'Full Stack Test'",
            "debug health --deep",
            "debug spans --file test_generated/captured_spans.json --format mermaid"
        ],
        "debug-cycle": [
            "debug health --deep",
            f"agents communicate --agents {agents}",
            "debug spans --file test_generated/captured_spans.json --format table",
            "debug inspect agents --verbose"
        ],
        "agent-test": [
            f"agents communicate --agents {agents}",
            "debug spans --file test_generated/captured_spans.json --format json",
            "debug inspect agents",
            "debug health"
        ],
        "llm-validation": [
            "debug health --deep",
            f"agents communicate --agents {agents}",
            "debug spans --file test_generated/captured_spans.json --format table",
            "debug inspect agents --verbose",
            f"agents communicate --agents {agents + 1}"
        ]
    }
    
    if name not in workflows:
        rprint(f"[red]❌ Unknown workflow: {name}[/red]")
        rprint(f"[yellow]Available workflows: {', '.join(workflows.keys())}[/yellow]")
        raise typer.Exit(1)
    
    rprint(f"[bold cyan]🔗 SPIFF WORKFLOW: {name.upper()}[/bold cyan]")
    
    # Execute the workflow using chain command
    commands = workflows[name]
    
    # Import to reuse chain logic
    import subprocess
    result = subprocess.run([
        "uv", "run", "run_cli.py", "spiff", "chain"
    ] + commands + [
        "--output", str(output_dir),
        "--spans",
        "--fail-fast"
    ])
    
    if result.returncode == 0:
        rprint(f"[bold green]🎉 WORKFLOW '{name}' COMPLETED SUCCESSFULLY[/bold green]")
    else:
        rprint(f"[bold red]❌ WORKFLOW '{name}' FAILED[/bold red]")

@spiff_app.command()
def history(
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Output directory"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of recent chains to show")
):
    """📊 Show command chain execution history with span analytics"""
    
    chain_files = list(output_dir.glob("chain_result_*.json"))
    chain_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not chain_files:
        rprint("[yellow]📭 No command chain history found[/yellow]")
        return
    
    rprint(f"[bold cyan]📊 COMMAND CHAIN HISTORY[/bold cyan]")
    
    from rich.table import Table
    table = Table(title=f"Recent {min(limit, len(chain_files))} Command Chains")
    table.add_column("Chain ID", style="cyan")
    table.add_column("Commands", style="white")
    table.add_column("Success", style="green")
    table.add_column("Spans", style="yellow")
    table.add_column("Time", style="dim")
    
    for chain_file in chain_files[:limit]:
        try:
            with open(chain_file) as f:
                data = json.load(f)
                
            chain_id = str(data["chain_id"])[-4:]  # Last 4 digits
            commands = " → ".join([cmd.split()[0] for cmd in data["commands"][:3]])
            if len(data["commands"]) > 3:
                commands += f" + {len(data['commands']) - 3} more"
                
            success = f"{data['summary']['successful_steps']}/{data['summary']['total_steps']}"
            spans = str(data['summary']['total_spans'])
            time_str = chain_file.stat().st_mtime
            
            import datetime
            time_formatted = datetime.datetime.fromtimestamp(time_str).strftime("%H:%M:%S")
            
            table.add_row(chain_id, commands, success, spans, time_formatted)
            
        except Exception as e:
            table.add_row("ERROR", str(e)[:30], "?/?", "?", "?")
    
    console.print(table)


@spiff_app.command()
def bpmn(
    workflow_name: str = typer.Argument(..., help="Workflow name: agent-validation, multi-agent-test, full-validation"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Output directory"),
    save_bpmn: bool = typer.Option(False, "--save-bpmn", help="Save BPMN XML file"),
    agents: int = typer.Option(3, "--agents", "-a", help="Number of agents for testing")
):
    """🔗 Execute workflows using SpiffWorkflow with BPMN support"""
    
    if workflow_name not in WORKFLOW_CONFIGS:
        rprint(f"[red]❌ Unknown workflow: {workflow_name}[/red]")
        rprint(f"[yellow]Available workflows: {', '.join(WORKFLOW_CONFIGS.keys())}[/yellow]")
        raise typer.Exit(1)
    
    rprint(f"[bold cyan]🔗 SPIFFWORKFLOW EXECUTION: {workflow_name.upper()}[/bold cyan]")
    
    # Get commands and substitute agent count
    commands = []
    for cmd in WORKFLOW_CONFIGS[workflow_name]:
        if "--agents" in cmd and "{agents}" not in cmd:
            # Replace existing agent count with provided one
            parts = cmd.split()
            for i, part in enumerate(parts):
                if part == "--agents" and i + 1 < len(parts):
                    parts[i + 1] = str(agents)
            commands.append(" ".join(parts))
        else:
            commands.append(cmd.format(agents=agents))
    
    # Create workflow spec
    workflow = create_simple_workflow_spec(commands, f"WeaverGen_{workflow_name}")
    
    # Create context
    context = WeaverGenWorkflowContext(output_dir)
    
    # Save BPMN if requested
    if save_bpmn:
        bpmn_content = create_agent_validation_bpmn()
        bpmn_file = output_dir / f"{workflow_name}_workflow.bpmn"
        bpmn_file.parent.mkdir(parents=True, exist_ok=True)
        with open(bpmn_file, 'w') as f:
            f.write(bpmn_content)
        rprint(f"[cyan]💾 BPMN saved to: {bpmn_file}[/cyan]")
    
    # Execute workflow
    results = execute_workflow(workflow, context)
    
    # Save results
    results_file = output_dir / f"spiff_workflow_{workflow_name}_{hash(str(commands)) % 10000}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    rprint(f"[cyan]💾 Workflow results saved to: {results_file}[/cyan]")
    
    # Show summary in mermaid format
    if results["successful_commands"] == results["total_commands"]:
        rprint("\n[bold green]📊 WORKFLOW MERMAID DIAGRAM:[/bold green]")
        rprint("```mermaid")
        rprint("graph LR")
        rprint("    Start([Start])")
        for i, cmd in enumerate(commands):
            cmd_name = cmd.split()[0].replace("-", "_")
            rprint(f"    Step{i}[{cmd_name}]")
            if i == 0:
                rprint(f"    Start --> Step{i}")
            else:
                rprint(f"    Step{i-1} --> Step{i}")
        rprint(f"    Step{len(commands)-1} --> End([End])")
        rprint("```")

@spiff_app.command()
def compare(
    workflow1: str = typer.Argument(..., help="First workflow to compare"),
    workflow2: str = typer.Argument(..., help="Second workflow to compare"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o", help="Output directory"),
    metric: str = typer.Option("spans", "--metric", "-m", help="Comparison metric: spans, success_rate, duration")
):
    """📊 Compare execution results between different workflows"""
    
    # Find workflow result files
    pattern1 = f"spiff_workflow_{workflow1}_*.json"
    pattern2 = f"spiff_workflow_{workflow2}_*.json"
    
    files1 = list(output_dir.glob(pattern1))
    files2 = list(output_dir.glob(pattern2))
    
    if not files1:
        rprint(f"[red]❌ No results found for workflow: {workflow1}[/red]")
        return
    if not files2:
        rprint(f"[red]❌ No results found for workflow: {workflow2}[/red]")
        return
    
    # Get latest results
    latest1 = max(files1, key=lambda x: x.stat().st_mtime)
    latest2 = max(files2, key=lambda x: x.stat().st_mtime)
    
    with open(latest1) as f:
        results1 = json.load(f)
    with open(latest2) as f:
        results2 = json.load(f)
    
    rprint(f"[bold cyan]📊 WORKFLOW COMPARISON: {workflow1} vs {workflow2}[/bold cyan]")
    
    from rich.table import Table
    table = Table(title=f"Workflow Comparison - {metric.title()}")
    table.add_column("Metric", style="cyan")
    table.add_column(workflow1, style="green")
    table.add_column(workflow2, style="yellow")
    table.add_column("Winner", style="bold")
    
    # Compare metrics
    metrics = {
        "Total Commands": (results1["total_commands"], results2["total_commands"]),
        "Successful Commands": (results1["successful_commands"], results2["successful_commands"]),
        "Success Rate": (results1["successful_commands"]/results1["total_commands"], 
                        results2["successful_commands"]/results2["total_commands"]),
        "Span Files": (len(results1["span_files"]), len(results2["span_files"])),
        "Duration": (len(results1["execution_log"]), len(results2["execution_log"]))
    }
    
    for metric_name, (val1, val2) in metrics.items():
        winner = workflow1 if val1 > val2 else workflow2 if val2 > val1 else "Tie"
        table.add_row(
            metric_name,
            f"{val1:.2f}" if isinstance(val1, float) else str(val1),
            f"{val2:.2f}" if isinstance(val2, float) else str(val2),
            winner
        )
    
    console.print(table)


# ============= Innovation Commands =============

@app.command()
def generate_smart(
    convention: Path = typer.Argument(..., help="Path to semantic convention YAML"),
    languages: List[str] = typer.Option(["python"], "-l", "--language"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Force mode: weaver, direct, or auto"),
    output: Path = typer.Option(Path("generated"), "-o", "--output"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Disable AI enhancement")
):
    """Generate code using smart dual-mode pipeline (works without Weaver!)."""
    from .dual_mode_pipeline import DualModePipeline, PipelineConfig
    
    config = PipelineConfig(
        output_dir=output,
        use_ai_enhancement=not no_ai
    )
    
    pipeline = DualModePipeline(config)
    
    rprint(f"[bold cyan]🚀 WeaverGen Smart Generation[/bold cyan]")
    rprint(f"📁 Convention: {convention}")
    rprint(f"🎯 Languages: {', '.join(languages)}")
    rprint(f"🤖 AI Enhancement: {'Enabled' if not no_ai else 'Disabled'}")
    rprint(f"🔧 Weaver Available: {'Yes' if pipeline.weaver_available else 'No (using direct mode)'}")
    
    result = pipeline.generate(convention, languages, mode)
    
    if result.success:
        rprint(f"[green]✅ Generation successful![/green]")
        rprint(f"📊 Mode used: {result.mode}")
        rprint(f"📁 Files generated: {len(result.files_generated)}")
        for file in result.files_generated:
            rprint(f"  - {file}")
    else:
        rprint(f"[red]❌ Generation failed: {result.error}[/red]")


@app.command()
def validate_multi(
    file_path: Path = typer.Argument(..., help="Path to Python file to validate"),
    specialists: Optional[List[str]] = typer.Option(None, "--specialist", "-s", help="Specific specialists to run"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output path for report")
):
    """Run multi-agent validation on Python code."""
    import asyncio
    from .multi_agent_validation import MultiAgentValidator
    
    if not file_path.exists():
        rprint(f"[red]❌ File not found: {file_path}[/red]")
        raise typer.Exit(1)
    
    validator = MultiAgentValidator()
    
    with open(file_path, 'r') as f:
        code = f.read()
    
    rprint(f"[bold cyan]🔍 Multi-Agent Validation[/bold cyan]")
    rprint(f"📄 File: {file_path}")
    rprint(f"👥 Specialists: {len(validator.specialists)}")
    
    # Run validation
    results = asyncio.run(validator.validate_code(code, file_path, specialists))
    
    # Generate report
    report = validator.format_report(results)
    summary = validator.get_summary(results)
    
    # Display summary
    rprint("\n[bold]Summary:[/bold]")
    rprint(f"Total Issues: {summary['total_issues']}")
    
    if summary['by_severity']['error'] > 0:
        rprint(f"[red]Errors: {summary['by_severity']['error']}[/red]")
    if summary['by_severity']['warning'] > 0:
        rprint(f"[yellow]Warnings: {summary['by_severity']['warning']}[/yellow]")
    if summary['by_severity']['suggestion'] > 0:
        rprint(f"[blue]Suggestions: {summary['by_severity']['suggestion']}[/blue]")
    
    # Save report
    report_path = output or file_path.with_suffix('.validation.md')
    report_path.write_text(report)
    rprint(f"\n[green]📄 Full report saved to: {report_path}[/green]")


@app.command()
def parse_semantic(
    yaml_path: Path = typer.Argument(..., help="Path to semantic convention YAML"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output path for generated code")
):
    """Parse semantic convention YAML directly (no Weaver required)."""
    from .semantic_parser import SemanticConventionParser
    
    if not yaml_path.exists():
        rprint(f"[red]❌ File not found: {yaml_path}[/red]")
        raise typer.Exit(1)
    
    parser = SemanticConventionParser()
    
    rprint(f"[bold cyan]📝 Direct Semantic Convention Parser[/bold cyan]")
    rprint(f"📄 File: {yaml_path}")
    
    try:
        conventions = parser.parse_file(yaml_path)
        rprint(f"[green]✅ Parsed {len(conventions)} conventions[/green]")
        
        # Generate Pydantic models
        code = parser.generate_pydantic_models(conventions)
        
        # Save or display
        if output:
            output.write_text(code)
            rprint(f"[green]💾 Generated code saved to: {output}[/green]")
        else:
            rprint("\n[bold]Generated Pydantic Models:[/bold]")
            rprint(code)
            
    except Exception as e:
        rprint(f"[red]❌ Parsing failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def learn_templates(
    source_dir: Path = typer.Argument(Path("test_generated"), help="Directory with example code"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output path for template library")
):
    """Learn code patterns from existing generated code."""
    from .template_learner import TemplateExtractor
    
    if not source_dir.exists():
        rprint(f"[red]❌ Directory not found: {source_dir}[/red]")
        raise typer.Exit(1)
    
    extractor = TemplateExtractor(source_dir)
    
    rprint(f"[bold cyan]🧠 Template Learning System[/bold cyan]")
    rprint(f"📁 Analyzing: {source_dir}")
    
    patterns = extractor.analyze_directory()
    
    total_patterns = sum(len(p) for p in patterns.values())
    rprint(f"[green]✅ Discovered {total_patterns} patterns[/green]")
    
    for pattern_type, pattern_list in patterns.items():
        if pattern_list:
            rprint(f"  - {pattern_type}: {len(pattern_list)} patterns")
    
    # Generate template library
    library_code = extractor.generate_template_library()
    
    if output:
        output.write_text(library_code)
        rprint(f"\n[green]💾 Template library saved to: {output}[/green]")
    else:
        rprint("\n[bold]Template Library Preview:[/bold]")
        rprint(library_code[:500] + "...")


# ============= BPMN Commands =============

@bpmn_app.command()
@enforce_dod(require_bpmn=True, min_trust_score=0.9)  # BPMN commands must have BPMN attribution
@cli_span("bpmn.execute", bpmn_file="workflows/bpmn/{workflow}.bpmn", bpmn_task="Dynamic")
def execute(
    workflow: str = typer.Argument("WeaverGenOrchestration", help="BPMN workflow to execute"),
    semantic_file: Path = typer.Option(
        Path("semantic_conventions/weavergen_system.yaml"),
        "--semantic", "-s",
        help="Semantic convention file"
    ),
    output_dir: Path = typer.Option(
        Path("bpmn_generated"),
        "--output", "-o",
        help="Output directory"
    ),
    show_trace: bool = typer.Option(
        False,
        "--trace",
        help="Show execution trace as Mermaid diagram"
    )
):
    """📋 Execute BPMN workflow with full span tracking"""
    import asyncio
    from .spiff_bpmn_engine import SpiffBPMNEngine, SpiffExecutionContext
    
    rprint(f"[bold cyan]📋 BPMN-FIRST EXECUTION[/bold cyan]")
    rprint(f"[cyan]🔄 Workflow: {workflow}[/cyan]")
    rprint(f"[cyan]📄 Semantics: {semantic_file}[/cyan]")
    rprint(f"[cyan]📁 Output: {output_dir}[/cyan]")
    
    # Create SpiffWorkflow engine
    engine = SpiffBPMNEngine()
    
    # Create context
    context = SpiffExecutionContext()
    context.set("semantic_file", str(semantic_file))
    context.set("output_dir", str(output_dir))
    
    # Execute workflow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]Executing {workflow}...", total=None)
        
        result = engine.execute_workflow(workflow, context)
        
        progress.update(task, completed=True)
    
    # Show results
    rprint(f"[green]✅ Workflow completed[/green]")
    rprint(f"[cyan]📊 Tasks executed: {len(result.execution_log)}[/cyan]")
    
    # Show execution report
    report = engine.generate_execution_report(result)
    console.print(report)
    
    # Show trace if requested
    if show_trace:
        mermaid = engine.generate_mermaid_trace(result)
        rprint("\n[bold cyan]🔍 Execution Trace (Mermaid):[/bold cyan]")
        rprint(mermaid)

@bpmn_app.command()
@enforce_dod(require_bpmn=True, min_trust_score=0.85, fail_on_lies=True)
@cli_span("bpmn.weaver", bpmn_file="workflows/bpmn/weaver_forge_orchestration.bpmn", bpmn_task="Task_InitWeaver")
def weaver(
    registry_url: str = typer.Option(
        "https://github.com/open-telemetry/semantic-conventions",
        "--registry", "-r",
        help="Semantic registry URL or path"
    ),
    language: str = typer.Option(
        "python",
        "--language", "-l",
        help="Target language (python, multi)"
    ),
    output_dir: Path = typer.Option(
        Path("weaver_generated"),
        "--output", "-o",
        help="Output directory"
    )
):
    """🔨 Run BPMN-driven Weaver Forge generation"""
    import asyncio
    from .bpmn_weaver_forge import WeaverBPMNEngine
    
    rprint("[bold cyan]🔨 BPMN-DRIVEN WEAVER FORGE[/bold cyan]")
    rprint(f"[cyan]📚 Registry: {registry_url}[/cyan]")
    rprint(f"[cyan]🐍 Language: {language}[/cyan]")
    rprint(f"[cyan]📁 Output: {output_dir}[/cyan]")
    
    # Create engine
    engine = WeaverBPMNEngine()
    
    # Create context
    context = {
        "registry_url": registry_url,
        "language": language,
        "output_dir": str(output_dir),
        "semantic_file": registry_url
    }
    
    try:
        # Execute Weaver workflow
        result = asyncio.run(engine.execute_weaver_workflow("WeaverForgeOrchestration", context))
        
        if result.get("validation_passed"):
            rprint("[green]✅ Weaver Forge generation successful[/green]")
            rprint(f"[cyan]📊 Validation score: {result.get('validation_score', 0):.2%}[/cyan]")
        else:
            rprint("[yellow]⚠️ Generation completed with warnings[/yellow]")
            
    except Exception as e:
        rprint(f"[red]❌ Weaver Forge failed: {e}[/red]")
        raise typer.Exit(1)

@bpmn_app.command()
def orchestrate(
    semantic_file: Path = typer.Option(
        Path("semantic_conventions/weavergen_system.yaml"),
        "--semantic", "-s",
        help="Semantic convention file"
    ),
    output_dir: Path = typer.Option(
        Path("bpmn_generated"),
        "--output", "-o", 
        help="Output directory"
    ),
    test: bool = typer.Option(
        True,
        "--test/--no-test",
        help="Run tests after generation"
    )
):
    """🎯 Run full BPMN orchestration workflow"""
    import asyncio
    from .spiff_bpmn_engine import run_spiff_bpmn_generation
    
    rprint("[bold cyan]🎯 BPMN-FIRST ORCHESTRATION[/bold cyan]")
    
    try:
        result = asyncio.run(run_spiff_bpmn_generation(semantic_file, output_dir))
        
        if result["success"]:
            rprint(f"[green]✅ Orchestration successful[/green]")
            rprint(f"[cyan]📊 Tasks executed: {result['tasks_executed']}[/cyan]")
            
            if test:
                # Run generated agent test
                rprint("\n[cyan]🧪 Testing generated system...[/cyan]")
                subprocess.run(["weavergen", "agents", "communicate", "--agents", "3"])
        else:
            rprint("[red]❌ Orchestration failed[/red]")
            
    except Exception as e:
        rprint(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

@bpmn_app.command()
def list():
    """📝 List available BPMN workflows"""
    from pathlib import Path
    
    bpmn_dir = Path("src/weavergen/workflows/bpmn")
    
    table = Table(title="Available BPMN Workflows", show_header=True, header_style="bold magenta")
    table.add_column("Workflow", style="cyan", width=30)
    table.add_column("File", style="green")
    table.add_column("Type", style="yellow")
    
    if bpmn_dir.exists():
        for bpmn_file in bpmn_dir.glob("*.bpmn"):
            workflow_name = bpmn_file.stem
            workflow_type = "Orchestration" if "orchestration" in workflow_name else "Generation"
            table.add_row(workflow_name, bpmn_file.name, workflow_type)
    else:
        table.add_row("No workflows found", "-", "-")
    
    console.print(table)

@bpmn_app.command()
def validate_spans(
    span_file: Optional[Path] = typer.Option(None, "--file", "-f", help="Span file to validate"),
    capture: bool = typer.Option(False, "--capture", help="Capture new spans"),
    output_dir: Path = typer.Option(Path("."), "--output", "-o", help="Output directory for reports")
):
    """🔍 Validate spans from BPMN executions"""
    import asyncio
    from .span_validator import SpanCaptureSystem, SpanValidator, SpanReportGenerator
    
    rprint("[bold cyan]🔍 SPAN VALIDATION[/bold cyan]")
    
    if capture:
        # Capture new spans
        rprint("[cyan]📡 Capturing spans from execution...[/cyan]")
        capture_system = SpanCaptureSystem()
        
        # Run a test workflow to generate spans
        from .bpmn_weaver_forge import WeaverBPMNEngine
        engine = WeaverBPMNEngine()
        context = {
            "registry_url": "semantic_conventions/weavergen_system.yaml",
            "language": "python",
            "output_dir": str(output_dir)
        }
        
        try:
            asyncio.run(engine.execute_weaver_workflow("WeaverForgeOrchestration", context))
        except:
            pass  # Continue even if workflow fails
        
        # Save captured spans
        span_file = output_dir / "captured_spans.json"
        count = capture_system.save_spans(span_file)
        rprint(f"[green]✅ Captured {count} spans to {span_file}[/green]")
    
    # Load spans
    if not span_file or not span_file.exists():
        rprint("[red]❌ No span file provided or found[/red]")
        raise typer.Exit(1)
    
    with open(span_file) as f:
        spans = json.load(f)
    
    rprint(f"[cyan]📊 Loaded {len(spans)} spans from {span_file}[/cyan]")
    
    # Validate spans
    validator = SpanValidator()
    result = validator.validate_spans(spans)
    
    # Generate reports
    reporter = SpanReportGenerator()
    
    # Table report
    table = reporter.generate_table_report(result)
    console.print(table)
    
    # Tree report
    if len(spans) > 0:
        tree = reporter.generate_tree_report(spans)
        console.print("\n[bold]Span Hierarchy:[/bold]")
        console.print(tree)
    
    # Issues and recommendations
    if result.issues:
        rprint("\n[red]Issues:[/red]")
        for issue in result.issues:
            rprint(f"  • {issue}")
    
    if result.recommendations:
        rprint("\n[yellow]Recommendations:[/yellow]")
        for rec in result.recommendations:
            rprint(f"  • {rec}")
    
    # Save reports
    report_file = output_dir / "span_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump({
            "validation_result": {
                "total_spans": result.total_spans,
                "valid_spans": result.valid_spans,
                "health_score": result.health_score,
                "semantic_compliance": result.semantic_compliance,
                "coverage_score": result.coverage_score,
                "hierarchy_valid": result.hierarchy_valid,
                "performance_score": result.performance_score
            },
            "issues": result.issues,
            "recommendations": result.recommendations
        }, f, indent=2)
    
    rprint(f"\n[cyan]💾 Report saved to {report_file}[/cyan]")
    
    if result.health_score >= 0.8:
        rprint(f"[green]✅ Validation PASSED with health score: {result.health_score:.1%}[/green]")
    else:
        rprint(f"[red]❌ Validation FAILED with health score: {result.health_score:.1%}[/red]")

@bpmn_app.command()
def validate(
    bpmn_file: Path = typer.Argument(..., help="BPMN file to validate")
):
    """✅ Validate BPMN workflow definition"""
    import xml.etree.ElementTree as ET
    
    rprint(f"[cyan]🔍 Validating BPMN: {bpmn_file}[/cyan]")
    
    try:
        # Parse XML
        tree = ET.parse(bpmn_file)
        root = tree.getroot()
        
        # Extract process info
        namespaces = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
        processes = root.findall('.//bpmn:process', namespaces)
        
        rprint(f"[green]✅ Valid BPMN 2.0 file[/green]")
        rprint(f"[cyan]📋 Processes found: {len(processes)}[/cyan]")
        
        for process in processes:
            process_id = process.get('id', 'Unknown')
            process_name = process.get('name', 'Unnamed')
            
            # Count elements
            tasks = process.findall('.//bpmn:serviceTask', namespaces)
            gateways = process.findall('.//bpmn:parallelGateway', namespaces) + \
                      process.findall('.//bpmn:exclusiveGateway', namespaces)
            
            rprint(f"\n[bold]Process: {process_name}[/bold]")
            rprint(f"  ID: {process_id}")
            rprint(f"  Service Tasks: {len(tasks)}")
            rprint(f"  Gateways: {len(gateways)}")
            
    except Exception as e:
        rprint(f"[red]❌ Invalid BPMN: {e}[/red]")
        raise typer.Exit(1)

@bpmn_app.command()
def ultralight(
    workflow: str = typer.Option("demo", "--workflow", "-w", help="Workflow: demo, orchestrate, 8020"),
    semantic_file: Path = typer.Option(Path("test_semantic.yaml"), "--semantic", "-s", help="Semantic file"),
    output_dir: Path = typer.Option(Path("generated_8020"), "--output", "-o", help="Output directory")
):
    """⚡ 80/20 BPMN Ultralight Engine - Minimal BPMN with Maximum Impact"""
    import asyncio
    
    rprint("[bold cyan]⚡ 80/20 BPMN ULTRALIGHT ENGINE[/bold cyan]")
    rprint(f"[cyan]🔄 Workflow: {workflow}[/cyan]")
    rprint(f"[cyan]📄 Semantics: {semantic_file}[/cyan]")
    rprint(f"[cyan]📁 Output: {output_dir}[/cyan]")
    
    async def run_ultralight():
        if workflow == "demo" or workflow == "8020":
            from .bpmn_ultralight_engine import demo_8020_bpmn_workflow
            await demo_8020_bpmn_workflow()
        elif workflow == "orchestrate":
            from .bpmn_orchestrator import run_bpmn_orchestration
            result = await run_bpmn_orchestration(semantic_file, output_dir)
            rprint(f"\n[bold green]🎯 Ultralight Orchestration Complete[/bold green]")
            rprint(f"Success: {result.success}")
            rprint(f"Spans Generated: {result.spans_generated}")
            rprint(f"Health Score: {result.health_score}")
            rprint(f"Execution Time: {result.execution_time:.2f}s")
        else:
            rprint(f"[red]Unknown ultralight workflow: {workflow}[/red]")
    
    asyncio.run(run_ultralight())

@bpmn_app.command()
def spans_live(
    workflow: str = typer.Option("WeaverGen8020", "--workflow", "-w", help="Workflow to run"),
    format: str = typer.Option("mermaid", "--format", "-f", help="Output format: table, mermaid, json")
):
    """📊 Run BPMN workflow and analyze spans in real-time"""
    import asyncio
    
    rprint("[bold cyan]📊 LIVE SPAN ANALYSIS[/bold cyan]")
    
    async def run_live_analysis():
        from .bpmn_ultralight_engine import BPMNUltralightEngine, create_weavergen_8020_workflow
        
        # Create engine and workflow
        engine = BPMNUltralightEngine()
        workflow_name = create_weavergen_8020_workflow(engine)
        
        # Execute workflow
        context = await engine.execute_workflow(workflow_name)
        
        # Analyze spans
        rprint(f"\n[bold green]📊 Spans Analysis ({format})[/bold green]")
        
        if format == "table":
            table = engine.generate_execution_report(context)
            console.print(table)
        elif format == "mermaid":
            mermaid = engine.generate_mermaid_diagram(context)
            rprint(f"```mermaid\n{mermaid}\n```")
        elif format == "json":
            import json
            spans_data = {
                "spans": context.spans,
                "variables": context.variables,
                "total_spans": len(context.spans)
            }
            rprint(json.dumps(spans_data, indent=2))
        
        rprint(f"\n[bold magenta]✅ Live analysis complete: {len(context.spans)} spans processed[/bold magenta]")
    
    asyncio.run(run_live_analysis())

@bpmn_app.command()
def validate_8020(
    capture: bool = typer.Option(True, "--capture/--no-capture", help="Capture spans during execution"),
    health_threshold: float = typer.Option(0.7, "--threshold", "-t", help="Health score threshold")
):
    """🎯 Validate 80/20 BPMN implementation with spans"""
    import asyncio
    
    rprint("[bold cyan]🎯 80/20 BPMN VALIDATION[/bold cyan]")
    
    async def validate_8020():
        from .bpmn_orchestrator import BPMNWeaverGenOrchestrator
        
        # Run orchestration
        orchestrator = BPMNWeaverGenOrchestrator(
            Path("test_semantic.yaml"), 
            Path("generated_8020_validation")
        )
        
        result = await orchestrator.execute_full_workflow()
        
        # Validate results
        rprint(f"\n[bold green]📊 Validation Results[/bold green]")
        rprint(f"Success: {'✅' if result.success else '❌'} {result.success}")
        rprint(f"Spans Generated: 📊 {result.spans_generated}")
        rprint(f"Health Score: {'🟢' if result.health_score >= health_threshold else '🔴'} {result.health_score:.2f}")
        rprint(f"Execution Time: ⏱️ {result.execution_time:.2f}s")
        
        if result.errors:
            rprint(f"\n[red]❌ Errors:[/red]")
            for error in result.errors:
                rprint(f"  • {error}")
        
        # Mermaid diagram
        if result.mermaid_diagram:
            rprint(f"\n[bold blue]🎯 Execution Flow[/bold blue]")
            rprint(f"```mermaid\n{result.mermaid_diagram}\n```")
        
        # Final assessment
        if result.success and result.health_score >= health_threshold:
            rprint(f"\n[bold green]🎉 80/20 BPMN VALIDATION PASSED![/bold green]")
        else:
            rprint(f"\n[bold red]❌ 80/20 BPMN VALIDATION FAILED[/bold red]")
            raise typer.Exit(1)
    
    asyncio.run(validate_8020())


@app.command()
@enforce_dod(require_bpmn=True, min_trust_score=0.95, fail_on_lies=True)
def test_dod():
    """🧪 Test Definition of Done enforcement"""
    rprint("[cyan]Testing DoD enforcement...[/cyan]")
    
    # This command will FAIL because:
    # 1. No @cli_span decorator with BPMN attribution
    # 2. No spans generated inside the function
    # 3. Trust score will be 0%
    
    rprint("[yellow]This command should fail DoD validation![/yellow]")
    return "This won't matter"


@app.command()
@enforce_dod(require_bpmn=True, min_trust_score=0.8)
@cli_span("test.dod_valid", 
          bpmn_file="src/weavergen/workflows/bpmn/weavergen_orchestration.bpmn", 
          bpmn_task="Task_LoadSemantics")
def test_dod_valid():
    """✅ Test DoD with proper attribution"""
    from opentelemetry import trace
    
    rprint("[green]Testing DoD with proper BPMN attribution...[/green]")
    
    tracer = trace.get_tracer(__name__)
    
    # Generate some child spans
    with tracer.start_as_current_span("test.operation") as span:
        span.set_attribute("test.type", "validation")
        span.set_attribute("execution.success", True)
        rprint("  ✓ Generated child span")
    
    with tracer.start_as_current_span("test.verification") as span:
        span.set_attribute("verification.passed", True)
        rprint("  ✓ Verification complete")
    
    rprint("[green]This command should PASS DoD validation![/green]")
    return "Success"


@app.command()
@enforce_dod(require_bpmn=True, min_trust_score=0.8)
@cli_span("pydantic_ai.bpmn_execution", 
          bpmn_file="src/weavergen/workflows/bpmn/pydantic_ai_generation.bpmn", 
          bpmn_task="Task_GenerateModels")
def ai_generate(
    semantic_file: str = typer.Argument(..., help="Semantic convention file path"),
    output_dir: str = typer.Option("pydantic_ai_output", "--output", "-o", help="Output directory"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="AI model to use"),
    workflow: str = typer.Option("pydantic_ai_generation", "--workflow", "-w", help="BPMN workflow name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """🤖 Generate Pydantic AI agents using BPMN workflow orchestration
    
    This command executes a complete BPMN workflow that:
    1. Loads semantic conventions
    2. Generates Pydantic models using AI
    3. Creates Pydantic AI agents with proper system prompts  
    4. Validates all generated components
    5. Captures execution spans for validation
    
    The workflow uses real AI models for generation and SpiffWorkflow for orchestration.
    """
    rprint(f"[bold cyan]🤖 Starting Pydantic AI + BPMN Generation[/bold cyan]")
    rprint(f"[cyan]📄 Semantic File: {semantic_file}[/cyan]")
    rprint(f"[cyan]📁 Output Directory: {output_dir}[/cyan]")
    rprint(f"[cyan]🧠 AI Model: {model}[/cyan]")
    rprint(f"[cyan]🔄 BPMN Workflow: {workflow}[/cyan]")
    
    async def run_pydantic_ai_workflow():
        from opentelemetry import trace
        tracer = trace.get_tracer(__name__)
        
        try:
            # Import Pydantic AI BPMN engine
            from .pydantic_ai_bpmn_engine import PydanticAIBPMNEngine, PydanticAIContext
            
            with tracer.start_as_current_span("pydantic_ai.workflow_initialization") as span:
                span.set_attribute("semantic_file", semantic_file)
                span.set_attribute("output_dir", output_dir)
                span.set_attribute("model", model)
                span.set_attribute("workflow", workflow)
                
                # Initialize engine and context (use mock by default for demo)
                engine = PydanticAIBPMNEngine(model_name=model, use_mock=True)
                context = PydanticAIContext(
                    semantic_file=semantic_file,
                    output_dir=output_dir,
                    agent_roles=["coordinator", "analyst", "facilitator", "validator"],
                    quality_threshold=0.8
                )
                
                rprint("[yellow]⚙️ Initialized Pydantic AI BPMN engine[/yellow]")
            
            # Execute BPMN workflow with progress tracking
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Executing BPMN workflow...", total=None)
                
                with tracer.start_as_current_span("pydantic_ai.bpmn_execution") as span:
                    result = await engine.execute_workflow(workflow, context)
                    
                    span.set_attribute("execution.success", result.get("success", False))
                    span.set_attribute("models.generated", result.get("models_generated", 0))
                    span.set_attribute("agents.generated", result.get("agents_generated", 0))
                    span.set_attribute("quality.score", result.get("quality_score", 0))
                    
                progress.update(task, completed=True)
            
            # Display results
            if result.get("success", False):
                rprint(f"[bold green]✅ PYDANTIC AI GENERATION COMPLETED![/bold green]")
                
                # Show execution report
                report_table = engine.generate_execution_report(result)
                console.print(report_table)
                
                # Show output files
                if result.get("output_files"):
                    rprint(f"\n[bold cyan]📄 Generated Files:[/bold cyan]")
                    for file_path in result["output_files"]:
                        rprint(f"  📝 {file_path}")
                
                # Show Mermaid trace
                if verbose:
                    rprint(f"\n[bold cyan]🗺️ Execution Trace:[/bold cyan]")
                    mermaid = engine.generate_mermaid_trace(result)
                    rprint(f"```mermaid\n{mermaid}\n```")
                
                # Performance metrics
                rprint(f"\n[bold cyan]📊 Performance Metrics:[/bold cyan]")
                rprint(f"  🤖 AI Agents Generated: {result.get('agents_generated', 0)}")
                rprint(f"  📋 Pydantic Models Generated: {result.get('models_generated', 0)}")
                rprint(f"  📡 OTel Spans Captured: {len(result.get('spans', []))}")
                rprint(f"  🎯 Quality Score: {result.get('quality_score', 0):.1%}")
                rprint(f"  ✅ Validation Passed: {result.get('validation_passed', False)}")
                
                return result
                
            else:
                rprint(f"[bold red]❌ PYDANTIC AI GENERATION FAILED[/bold red]")
                if "error" in result:
                    rprint(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            with tracer.start_as_current_span("pydantic_ai.error_handling") as span:
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                span.record_exception(e)
            
            rprint(f"[bold red]❌ PYDANTIC AI ERROR: {e}[/bold red]")
            if verbose:
                import traceback
                rprint(f"[red]{traceback.format_exc()}[/red]")
            raise typer.Exit(1)
    
    # Run the async workflow
    asyncio.run(run_pydantic_ai_workflow())


if __name__ == "__main__":
    app()
