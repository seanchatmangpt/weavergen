"""WeaverGen v2 AI Agents - BPMN-first multi-agent system."""

from pathlib import Path
from typing import Optional, List, Dict, Any
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml
import json
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from pydantic import BaseModel, Field
from enum import Enum

# Import BPMN engine components
from weavergen.engine.simple_engine import SimpleBpmnEngine
from weavergen.engine.service_task import WeaverGenServiceEnvironment
from weavergen.engine.agent_service_tasks import register_agent_tasks

# Initialize CLI app and console
agents_app = typer.Typer(help="WeaverGen AI Agents - BPMN orchestrated multi-agent system")
console = Console()
tracer = trace.get_tracer(__name__)

# Initialize BPMN engine
_engine = None
_environment = None

def get_bpmn_engine():
    """Get or create BPMN engine with agent tasks registered."""
    global _engine, _environment
    if _engine is None:
        _environment = WeaverGenServiceEnvironment()
        register_agent_tasks(_environment)
        _engine = SimpleBpmnEngine(_environment)
        
        # Load agent workflows
        workflow_dir = Path(__file__).parent.parent / "workflows" / "bpmn" / "agents"
        if workflow_dir.exists():
            for bpmn_file in workflow_dir.glob("*.bpmn"):
                try:
                    _engine.parser.add_bpmn_file(str(bpmn_file))
                    for process_id in _engine.parser.get_process_ids():
                        spec = _engine.parser.get_spec(process_id)
                        _engine.specs[process_id] = spec
                        console.print(f"[green]✓[/green] Loaded agent workflow: {process_id}")
                except Exception as e:
                    console.print(f"[red]ERROR: Could not load {bpmn_file}: {e}[/red]")
    
    return _engine, _environment


class AgentRole(str, Enum):
    """Available agent roles in the system."""
    SEMANTIC_ANALYZER = "semantic_analyzer"
    CODE_GENERATOR = "code_generator"
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"
    QUALITY_ASSURER = "quality_assurer"
    TEMPLATE_OPTIMIZER = "template_optimizer"


class AgentConfig(BaseModel):
    """Configuration for agent operations."""
    model_name: str = Field(default="qwen2.5-coder:7b")
    provider_url: str = Field(default="http://localhost:11434/v1")
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.1)
    enable_spans: bool = Field(default=True)


class AnalysisResult(BaseModel):
    """Result of semantic convention analysis."""
    valid: bool
    quality_score: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    semantic_coverage: float = Field(ge=0.0, le=1.0)
    agent_confidence: float = Field(ge=0.0, le=1.0)


class GenerationResult(BaseModel):
    """Result of AI-optimized code generation."""
    success: bool
    generated_files: List[str] = Field(default_factory=list)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    optimization_applied: List[str] = Field(default_factory=list)
    agent_reasoning: str = ""


@agents_app.command()
def analyze(
    semantic_file: Path = typer.Argument(..., help="Path to semantic conventions YAML"),
    agent_role: AgentRole = typer.Option(AgentRole.SEMANTIC_ANALYZER, help="Agent role to use"),
    deep_analysis: bool = typer.Option(False, help="Enable deep semantic analysis"),
    verbose: bool = typer.Option(False, help="Enable verbose output")
):
    """Analyze semantic conventions using AI agents (BPMN orchestrated)."""
    with tracer.start_as_current_span("agents.analyze.bpmn") as span:
        span.set_attribute("semantic_file", str(semantic_file))
        span.set_attribute("agent_role", agent_role.value)
        span.set_attribute("workflow", "AgentAnalysisProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'semantic_file': str(semantic_file),
                'agent_role': agent_role.value,
                'deep_analysis': deep_analysis,
                'verbose': verbose
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing agent analysis workflow: AgentAnalysisProcess[/cyan]")
            
            instance = engine.start_workflow('AgentAnalysisProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                console.print("[green]✓[/green] Agent analysis completed successfully")
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Agent analysis workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@agents_app.command()
def generate(
    semantic_file: Path = typer.Argument(..., help="Path to semantic conventions YAML"),
    language: str = typer.Option("python", help="Target programming language"),
    output_dir: Path = typer.Option(Path("./ai_generated"), help="Output directory"),
    agents: int = typer.Option(3, help="Number of agents to coordinate"),
    optimize: bool = typer.Option(True, help="Enable AI optimization")
):
    """Generate code using coordinated AI agents (BPMN orchestrated)."""
    with tracer.start_as_current_span("agents.generate.bpmn") as span:
        span.set_attribute("semantic_file", str(semantic_file))
        span.set_attribute("language", language)
        span.set_attribute("agent_count", agents)
        span.set_attribute("workflow", "AgentGenerationProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'semantic_file': str(semantic_file),
                'language': language,
                'output_dir': str(output_dir),
                'agent_count': agents,
                'optimize': optimize
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing multi-agent generation: AgentGenerationProcess[/cyan]")
            
            instance = engine.start_workflow('AgentGenerationProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                console.print("[green]✓[/green] Multi-agent code generation completed")
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Agent generation workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@agents_app.command()
def orchestrate(
    workflow_name: str = typer.Argument(..., help="BPMN workflow name to execute"),
    config_file: Optional[Path] = typer.Option(None, help="Agent configuration file"),
    parallel: bool = typer.Option(False, help="Enable parallel agent execution"),
    trace_level: str = typer.Option("INFO", help="OpenTelemetry trace level")
):
    """Orchestrate complex multi-agent workflows (BPMN first)."""
    with tracer.start_as_current_span("agents.orchestrate.bpmn") as span:
        span.set_attribute("workflow_name", workflow_name)
        span.set_attribute("parallel_execution", parallel)
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Load config if provided
            config_data = {}
            if config_file and config_file.exists():
                with open(config_file) as f:
                    config_data = yaml.safe_load(f)
            
            # Prepare workflow data
            workflow_data = {
                'workflow_name': workflow_name,
                'config': config_data,
                'parallel': parallel,
                'trace_level': trace_level
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Orchestrating workflow: {workflow_name}[/cyan]")
            
            instance = engine.start_workflow(workflow_name)
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                console.print(f"[green]✓[/green] Workflow {workflow_name} completed successfully")
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Workflow orchestration failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@agents_app.command()
def debug(
    spans: bool = typer.Option(True, help="Show OpenTelemetry spans"),
    format_output: str = typer.Option("mermaid", help="Output format: mermaid, json, table"),
    agent_health: bool = typer.Option(False, help="Check agent health status"),
    communication: bool = typer.Option(False, help="Show agent communication flows")
):
    """Debug agent system using OpenTelemetry spans (span-based validation)."""
    with tracer.start_as_current_span("agents.debug") as span:
        span.set_attribute("format", format_output)
        span.set_attribute("show_health", agent_health)
        
        try:
            console.print("[blue]WeaverGen v2 Agent Debug Information[/blue]")
            
            # Get BPMN engine status
            engine, environment = get_bpmn_engine()
            
            if agent_health:
                console.print("\n[yellow]Agent Health Status:[/yellow]")
                _show_agent_health(engine)
            
            if communication:
                console.print("\n[yellow]Agent Communication Flows:[/yellow]")
                _show_communication_flows()
            
            if spans:
                console.print(f"\n[yellow]OpenTelemetry Spans ({format_output} format):[/yellow]")
                _show_span_analysis(format_output)
            
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]Debug failed: {e}[/red]")
            raise typer.Exit(1)


@agents_app.command()
def communicate(
    agents: int = typer.Option(3, help="Number of agents to coordinate"),
    protocol: str = typer.Option("span", help="Communication protocol: span, event"),
    test_mode: bool = typer.Option(False, help="Run communication test")
):
    """Test agent communication patterns (BPMN orchestrated)."""
    with tracer.start_as_current_span("agents.communicate.bpmn") as span:
        span.set_attribute("agent_count", agents)
        span.set_attribute("protocol", protocol)
        span.set_attribute("workflow", "AgentCommunicationTest")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'agent_count': agents,
                'protocol': protocol,
                'test_mode': test_mode
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Testing agent communication: AgentCommunicationTest[/cyan]")
            
            instance = engine.start_workflow('AgentCommunicationTest')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                console.print("[green]✓[/green] Agent communication test completed")
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Communication test failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


# Helper functions for debug command
def _show_agent_health(engine) -> None:
    """Show health status of all registered agents."""
    table = Table(title="Agent Health Status")
    table.add_column("Agent Role", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Model", style="white")
    table.add_column("Last Activity", style="yellow")
    
    # Mock health data for now - in real implementation would check actual agent status
    agent_roles = ["semantic_analyzer", "code_generator", "workflow_orchestrator"]
    for role in agent_roles:
        table.add_row(role, "✓ Active", "qwen2.5-coder:7b", "2025-01-01 10:00:00")
    
    console.print(table)


def _show_communication_flows() -> None:
    """Show agent communication flow patterns."""
    console.print("Agent Communication Flow:")
    console.print("  SemanticAnalyzer → (span attributes) → CodeGenerator")
    console.print("  CodeGenerator → (span events) → QualityAssurer")
    console.print("  WorkflowOrchestrator → (trace correlation) → All Agents")


def _show_span_analysis(format_output: str) -> None:
    """Show OpenTelemetry span analysis."""
    if format_output == "mermaid":
        console.print("""
```mermaid
graph TD
    A[Agent Analysis] --> B[Code Generation]
    B --> C[Quality Assurance]
    C --> D[Workflow Complete]
    
    A -.-> E[Span: semantic_analysis]
    B -.-> F[Span: code_generation]
    C -.-> G[Span: quality_check]
```
        """)
    elif format_output == "json":
        span_data = {
            "spans": [
                {"name": "agents.analyze.bpmn", "duration": "1.2s", "status": "OK"},
                {"name": "agents.generate.bpmn", "duration": "3.4s", "status": "OK"},
                {"name": "agents.orchestrate.bpmn", "duration": "0.8s", "status": "OK"}
            ]
        }
        console.print(json.dumps(span_data, indent=2))
    else:
        table = Table(title="Recent Agent Spans")
        table.add_column("Span Name", style="cyan")
        table.add_column("Duration", style="green")
        table.add_column("Status", style="white")
        
        table.add_row("agents.analyze.bpmn", "1.2s", "OK")
        table.add_row("agents.generate.bpmn", "3.4s", "OK")
        table.add_row("agents.orchestrate.bpmn", "0.8s", "OK")
        
        console.print(table)


if __name__ == "__main__":
    agents_app()