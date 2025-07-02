"""WeaverGen v2 XES - BPMN-first process mining and XES operations."""

from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree
import xml.etree.ElementTree as ET
import json
import yaml
from datetime import datetime, timezone
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from pydantic import BaseModel, Field
from enum import Enum
import uuid

# Import BPMN engine components
from weavergen.engine.simple_engine import SimpleBpmnEngine
from weavergen.engine.service_task import WeaverGenServiceEnvironment
from weavergen.engine.xes_service_tasks import register_xes_tasks

# Initialize CLI app and console
xes_app = typer.Typer(help="WeaverGen XES - BPMN orchestrated process mining and XES operations")
console = Console()
tracer = trace.get_tracer(__name__)

# Initialize BPMN engine
_engine = None
_environment = None

def get_bpmn_engine():
    """Get or create BPMN engine with XES tasks registered."""
    global _engine, _environment
    if _engine is None:
        _environment = WeaverGenServiceEnvironment()
        register_xes_tasks(_environment)
        _engine = SimpleBpmnEngine(_environment)
        
        # Load XES workflows
        workflow_dir = Path(__file__).parent.parent.parent / "workflows" / "bpmn" / "xes"
        if workflow_dir.exists():
            for bpmn_file in workflow_dir.glob("*.bpmn"):
                try:
                    _engine.parser.add_bpmn_file(str(bpmn_file))
                    for process_id in _engine.parser.get_process_ids():
                        spec = _engine.parser.get_spec(process_id)
                        _engine.specs[process_id] = spec
                        console.print(f"[green]✓[/green] Loaded XES workflow: {process_id}")
                except Exception as e:
                    console.print(f"[red]ERROR: Could not load {bpmn_file}: {e}[/red]")
    
    return _engine, _environment


class MiningAlgorithm(str, Enum):
    """Available process discovery algorithms."""
    ALPHA = "alpha"
    HEURISTIC = "heuristic"
    INDUCTIVE = "inductive"
    DIRECTLY_FOLLOWS = "directly_follows"


class OutputFormat(str, Enum):
    """Available output formats."""
    BPMN = "bpmn"
    PETRI = "petri"
    DFG = "dfg"
    PROCESS_TREE = "process_tree"


class VisualizationType(str, Enum):
    """Available visualization types."""
    PROCESS_MAP = "process-map"
    HEATMAP = "heatmap"
    TIMELINE = "timeline"
    DOTTED_CHART = "dotted-chart"


class ConformanceMethod(str, Enum):
    """Available conformance checking methods."""
    TOKEN_REPLAY = "token-replay"
    ALIGNMENTS = "alignments"
    FITNESS = "fitness"


class XESConfig(BaseModel):
    """Configuration for XES operations."""
    case_id_field: str = Field(default="trace_id")
    activity_field: str = Field(default="span_name")
    timestamp_field: str = Field(default="start_time")
    resource_field: str = Field(default="service_name")
    filter_noise: bool = Field(default=True)
    min_case_length: int = Field(default=2)


class ConversionResult(BaseModel):
    """Result of spans to XES conversion."""
    success: bool
    xes_file: str = ""
    total_traces: int = 0
    total_events: int = 0
    unique_activities: int = 0
    filtered_traces: int = 0
    conversion_time_ms: float = 0.0


class DiscoveryResult(BaseModel):
    """Result of process discovery."""
    success: bool
    algorithm: str = ""
    output_file: str = ""
    fitness: float = Field(ge=0.0, le=1.0, default=0.0)
    precision: float = Field(ge=0.0, le=1.0, default=0.0)
    simplicity: float = Field(ge=0.0, le=1.0, default=0.0)
    generalization: float = Field(ge=0.0, le=1.0, default=0.0)
    discovery_time_ms: float = 0.0


@xes_app.command()
def convert(
    spans_file: Path = typer.Argument(..., help="OpenTelemetry spans JSON file"),
    output: Path = typer.Option(Path("output.xes"), "--output", "-o", help="Output XES file"),
    case_field: str = typer.Option("trace_id", "--case-field", help="Field to use as case ID"),
    filter_noise: bool = typer.Option(True, "--filter-noise/--no-filter", help="Filter out noise traces"),
    min_case_length: int = typer.Option(2, "--min-length", help="Minimum case length"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Convert OpenTelemetry spans to XES format (BPMN orchestrated)."""
    with tracer.start_as_current_span("xes.convert.bpmn") as span:
        span.set_attribute("spans_file", str(spans_file))
        span.set_attribute("output_file", str(output))
        span.set_attribute("case_field", case_field)
        span.set_attribute("workflow", "XESConversionProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'spans_file': str(spans_file),
                'output_file': str(output),
                'case_field': case_field,
                'filter_noise': filter_noise,
                'min_case_length': min_case_length,
                'verbose': verbose
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing XES conversion workflow: XESConversionProcess[/cyan]")
            
            instance = engine.start_workflow('XESConversionProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                # Get results from workflow
                result_data = instance.workflow.data.get('conversion_result', {})
                console.print("[green]✓[/green] XES conversion completed successfully")
                
                # Display conversion statistics
                _display_conversion_results(result_data)
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: XES conversion workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@xes_app.command()
def discover(
    xes_file: Path = typer.Argument(..., help="XES event log file"),
    algorithm: MiningAlgorithm = typer.Option(MiningAlgorithm.ALPHA, "--algorithm", "-a", help="Discovery algorithm"),
    output_format: OutputFormat = typer.Option(OutputFormat.BPMN, "--format", "-f", help="Output format"),
    threshold: float = typer.Option(0.8, "--threshold", "-t", help="Minimum confidence threshold"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    simplify: bool = typer.Option(True, "--simplify/--no-simplify", help="Simplify discovered model")
):
    """Discover process models from XES event logs (BPMN orchestrated)."""
    with tracer.start_as_current_span("xes.discover.bpmn") as span:
        span.set_attribute("xes_file", str(xes_file))
        span.set_attribute("algorithm", algorithm.value)
        span.set_attribute("output_format", output_format.value)
        span.set_attribute("workflow", "XESDiscoveryProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'xes_file': str(xes_file),
                'algorithm': algorithm.value,
                'output_format': output_format.value,
                'threshold': threshold,
                'output_file': str(output) if output else None,
                'simplify': simplify
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing process discovery workflow: XESDiscoveryProcess[/cyan]")
            
            instance = engine.start_workflow('XESDiscoveryProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                # Get results from workflow
                result_data = instance.workflow.data.get('discovery_result', {})
                console.print("[green]✓[/green] Process discovery completed successfully")
                
                # Display discovery results
                _display_discovery_results(result_data, algorithm)
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Process discovery workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@xes_app.command()
def analyze(
    xes_file: Path = typer.Argument(..., help="XES event log file"),
    metrics: List[str] = typer.Option(["performance", "frequency", "bottlenecks"], "--metric", "-m", help="Analysis metrics"),
    visualize: bool = typer.Option(True, "--visualize/--no-visualize", help="Generate visualizations"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save analysis report"),
    time_unit: str = typer.Option("days", "--time-unit", help="Time unit for analysis")
):
    """Analyze XES event logs for performance and patterns (BPMN orchestrated)."""
    with tracer.start_as_current_span("xes.analyze.bpmn") as span:
        span.set_attribute("xes_file", str(xes_file))
        span.set_attribute("metrics", metrics)
        span.set_attribute("workflow", "XESAnalysisProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'xes_file': str(xes_file),
                'metrics': metrics,
                'visualize': visualize,
                'output_file': str(output) if output else None,
                'time_unit': time_unit
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing XES analysis workflow: XESAnalysisProcess[/cyan]")
            
            instance = engine.start_workflow('XESAnalysisProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                # Get results from workflow
                result_data = instance.workflow.data.get('analysis_result', {})
                console.print("[green]✓[/green] XES analysis completed successfully")
                
                # Display analysis results
                _display_analysis_results(result_data, metrics)
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: XES analysis workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@xes_app.command()
def conformance(
    xes_file: Path = typer.Argument(..., help="XES event log file"),
    model_file: Path = typer.Argument(..., help="Process model file (BPMN/Petri net)"),
    method: ConformanceMethod = typer.Option(ConformanceMethod.TOKEN_REPLAY, "--method", "-m", help="Conformance checking method"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed deviations"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save conformance report")
):
    """Check conformance between event logs and process models (BPMN orchestrated)."""
    with tracer.start_as_current_span("xes.conformance.bpmn") as span:
        span.set_attribute("xes_file", str(xes_file))
        span.set_attribute("model_file", str(model_file))
        span.set_attribute("method", method.value)
        span.set_attribute("workflow", "XESConformanceProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'xes_file': str(xes_file),
                'model_file': str(model_file),
                'method': method.value,
                'detailed': detailed,
                'output_file': str(output) if output else None
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing conformance checking workflow: XESConformanceProcess[/cyan]")
            
            instance = engine.start_workflow('XESConformanceProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                # Get results from workflow
                result_data = instance.workflow.data.get('conformance_result', {})
                console.print("[green]✓[/green] Conformance checking completed successfully")
                
                # Display conformance results
                _display_conformance_results(result_data, method)
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Conformance checking workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@xes_app.command()
def visualize(
    input_file: Path = typer.Argument(..., help="Input file (XES log or process model)"),
    viz_type: VisualizationType = typer.Option(VisualizationType.PROCESS_MAP, "--type", "-t", help="Visualization type"),
    output: Path = typer.Option(Path("process_viz.html"), "--output", "-o", help="Output visualization file"),
    interactive: bool = typer.Option(True, "--interactive/--static", help="Generate interactive visualization"),
    include_performance: bool = typer.Option(True, "--performance/--no-performance", help="Include performance data")
):
    """Generate visual representations of processes and event logs (BPMN orchestrated)."""
    with tracer.start_as_current_span("xes.visualize.bpmn") as span:
        span.set_attribute("input_file", str(input_file))
        span.set_attribute("viz_type", viz_type.value)
        span.set_attribute("workflow", "XESVisualizationProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'input_file': str(input_file),
                'viz_type': viz_type.value,
                'output_file': str(output),
                'interactive': interactive,
                'include_performance': include_performance
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing visualization workflow: XESVisualizationProcess[/cyan]")
            
            instance = engine.start_workflow('XESVisualizationProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                # Get results from workflow
                result_data = instance.workflow.data.get('visualization_result', {})
                console.print("[green]✓[/green] Visualization completed successfully")
                
                # Display visualization info
                _display_visualization_results(result_data, viz_type, output)
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Visualization workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


@xes_app.command()
def predict(
    model_file: Path = typer.Argument(..., help="Trained process model or XES log"),
    trace_prefix: str = typer.Argument(..., help="Partial trace prefix (comma-separated activities)"),
    top_k: int = typer.Option(3, "--top-k", "-k", help="Number of predictions to show"),
    with_probability: bool = typer.Option(True, "--probability/--no-probability", help="Show prediction probabilities"),
    confidence_threshold: float = typer.Option(0.1, "--threshold", "-t", help="Minimum confidence threshold")
):
    """Predict next activities and process outcomes (BPMN orchestrated)."""
    with tracer.start_as_current_span("xes.predict.bpmn") as span:
        span.set_attribute("model_file", str(model_file))
        span.set_attribute("trace_prefix", trace_prefix)
        span.set_attribute("workflow", "XESPredictionProcess")
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Parse trace prefix
            activities = [activity.strip() for activity in trace_prefix.split(",")]
            
            # Prepare workflow data
            workflow_data = {
                'model_file': str(model_file),
                'trace_prefix': activities,
                'top_k': top_k,
                'with_probability': with_probability,
                'confidence_threshold': confidence_threshold
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing prediction workflow: XESPredictionProcess[/cyan]")
            
            instance = engine.start_workflow('XESPredictionProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                # Get results from workflow
                result_data = instance.workflow.data.get('prediction_result', {})
                console.print("[green]✓[/green] Process prediction completed successfully")
                
                # Display prediction results
                _display_prediction_results(result_data, activities, top_k)
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Process prediction workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)


# Display helper functions

def _display_conversion_results(result_data: Dict[str, Any]) -> None:
    """Display XES conversion results."""
    table = Table(title="XES Conversion Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Traces", str(result_data.get('total_traces', 0)))
    table.add_row("Total Events", str(result_data.get('total_events', 0)))
    table.add_row("Unique Activities", str(result_data.get('unique_activities', 0)))
    table.add_row("Filtered Traces", str(result_data.get('filtered_traces', 0)))
    table.add_row("Conversion Time", f"{result_data.get('conversion_time_ms', 0):.2f}ms")
    
    console.print(table)


def _display_discovery_results(result_data: Dict[str, Any], algorithm: MiningAlgorithm) -> None:
    """Display process discovery results."""
    console.print(f"\n[green]Process Model Discovered using {algorithm.value} algorithm[/green]")
    
    # Quality metrics
    table = Table(title="Model Quality Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Quality", style="yellow")
    
    fitness = result_data.get('fitness', 0.0)
    precision = result_data.get('precision', 0.0)
    simplicity = result_data.get('simplicity', 0.0)
    generalization = result_data.get('generalization', 0.0)
    
    def get_quality(score):
        if score >= 0.9: return "Excellent"
        elif score >= 0.8: return "Good"
        elif score >= 0.7: return "Fair"
        else: return "Poor"
    
    table.add_row("Fitness", f"{fitness:.3f}", get_quality(fitness))
    table.add_row("Precision", f"{precision:.3f}", get_quality(precision))
    table.add_row("Simplicity", f"{simplicity:.3f}", get_quality(simplicity))
    table.add_row("Generalization", f"{generalization:.3f}", get_quality(generalization))
    
    console.print(table)
    
    # Output file info
    output_file = result_data.get('output_file')
    if output_file:
        console.print(f"\n[blue]Model saved to: {output_file}[/blue]")


def _display_analysis_results(result_data: Dict[str, Any], metrics: List[str]) -> None:
    """Display XES analysis results."""
    if "performance" in metrics:
        console.print("\n[yellow]Performance Analysis:[/yellow]")
        perf_data = result_data.get('performance', {})
        
        table = Table(title="Activity Performance")
        table.add_column("Activity", style="cyan")
        table.add_column("Avg Duration", style="green")
        table.add_column("Max Duration", style="red")
        table.add_column("Frequency", style="yellow")
        
        for activity, data in perf_data.items():
            table.add_row(
                activity,
                data.get('avg_duration', 'N/A'),
                data.get('max_duration', 'N/A'),
                str(data.get('frequency', 0))
            )
        
        console.print(table)
    
    if "bottlenecks" in metrics:
        console.print("\n[red]Bottlenecks Detected:[/red]")
        bottlenecks = result_data.get('bottlenecks', [])
        for bottleneck in bottlenecks:
            console.print(f"  • {bottleneck}")
    
    if "frequency" in metrics:
        console.print("\n[blue]Process Patterns:[/blue]")
        patterns = result_data.get('patterns', {})
        for pattern, frequency in patterns.items():
            console.print(f"  • {pattern}: {frequency}")


def _display_conformance_results(result_data: Dict[str, Any], method: ConformanceMethod) -> None:
    """Display conformance checking results."""
    console.print(f"\n[green]Conformance Results ({method.value}):[/green]")
    
    # Overall metrics
    table = Table(title="Conformance Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Status", style="yellow")
    
    fitness = result_data.get('fitness', 0.0)
    precision = result_data.get('precision', 0.0)
    
    def get_status(score):
        if score >= 0.9: return "✓ Excellent"
        elif score >= 0.8: return "✓ Good"
        elif score >= 0.7: return "⚠ Fair"
        else: return "✗ Poor"
    
    table.add_row("Fitness", f"{fitness:.1%}", get_status(fitness))
    table.add_row("Precision", f"{precision:.1%}", get_status(precision))
    
    console.print(table)
    
    # Deviations
    deviations = result_data.get('deviations', [])
    if deviations:
        console.print("\n[yellow]Deviations Found:[/yellow]")
        dev_table = Table()
        dev_table.add_column("Type", style="red")
        dev_table.add_column("Description", style="white")
        dev_table.add_column("Frequency", style="yellow")
        
        for dev in deviations:
            dev_table.add_row(dev['type'], dev['description'], dev['frequency'])
        
        console.print(dev_table)


def _display_visualization_results(result_data: Dict[str, Any], viz_type: VisualizationType, output: Path) -> None:
    """Display visualization results."""
    viz_info = {
        "process-map": "Interactive process flow diagram with activity frequencies",
        "heatmap": "Performance heatmap showing bottlenecks and delays",
        "timeline": "Temporal process evolution and case timelines",
        "dotted-chart": "Event distribution chart for pattern analysis"
    }
    
    description = viz_info.get(viz_type.value, "Process visualization")
    
    panel = Panel(
        f"[green]✓[/green] {description}\n\n"
        f"Output file: {output}\n"
        f"Format: {'Interactive HTML' if result_data.get('interactive') else 'Static image'}\n"
        f"Performance data: {'Included' if result_data.get('include_performance') else 'Not included'}",
        title="Visualization Created",
        border_style="green"
    )
    
    console.print(panel)


def _display_prediction_results(result_data: Dict[str, Any], activities: List[str], top_k: int) -> None:
    """Display process prediction results."""
    console.print(f"\n[blue]Predictions for trace: {' → '.join(activities)}[/blue]")
    
    predictions = result_data.get('predictions', [])
    
    if predictions:
        table = Table(title="Next Activity Predictions")
        table.add_column("Rank", style="cyan")
        table.add_column("Activity", style="green")
        table.add_column("Probability", style="yellow")
        table.add_column("Est. Duration", style="magenta")
        
        for i, pred in enumerate(predictions[:top_k], 1):
            table.add_row(
                str(i),
                pred.get('activity', 'Unknown'),
                f"{pred.get('probability', 0.0):.1%}",
                pred.get('duration', 'N/A')
            )
        
        console.print(table)
        
        # Most likely completion
        if len(predictions) > 0:
            best_pred = predictions[0]
            completion = activities + [best_pred.get('activity', 'Unknown')]
            console.print(f"\n[dim]Most likely completion: {' → '.join(completion)}[/dim]")
    else:
        console.print("[yellow]No predictions available[/yellow]")


if __name__ == "__main__":
    xes_app()