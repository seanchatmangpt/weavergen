"""
WeaverGen v2 Debug Commands
System debugging, diagnostics, and health monitoring
"""

import typer
import asyncio
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax

from ...core.engine.spiff_engine import WeaverGenV2Engine
from ...weavergen.src.visualizers.mermaid import MermaidVisualizer, MermaidLifecycleGenerator

app = typer.Typer(
    name="debug",
    help="Debugging, diagnostics, and system health monitoring",
    rich_markup_mode="rich"
)

console = Console()

@app.command("spans")
def debug_spans(
    ctx: typer.Context,
    span_file: Optional[Path] = typer.Option(None, "--file", "-f", help="Span file to analyze"),
    format: str = typer.Option("rich", "--format", help="Output format: rich, json, mermaid"),
    filter_service: Optional[str] = typer.Option(None, "--service", "-s", help="Filter by service name"),
    min_duration: Optional[float] = typer.Option(None, "--min-duration", help="Minimum span duration (ms)"),
    errors_only: bool = typer.Option(False, "--errors-only", help="Show only error spans")
):
    """Analyze OpenTelemetry spans for debugging"""
    
    async def run_debug_spans():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "span_file": str(span_file) if span_file else None,
            "span_analysis_config": {
                "output_format": format,
                "service_filter": filter_service,
                "min_duration_ms": min_duration,
                "errors_only": errors_only,
                "calculate_metrics": True
            },
            "cli_command": "debug spans"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Analyzing spans...", total=None)
            
            try:
                result = await engine.execute_workflow("span_analysis", context)
                
                if result.success:
                    span_data = result.final_data.get("span_analysis", {})
                    progress.update(task, description="✅ Span analysis complete")
                    
                    if format == "rich":
                        display_span_analysis_rich(span_data)
                    elif format == "json":
                        console.print_json(json.dumps(span_data, indent=2, default=str))
                    elif format == "mermaid":
                        # Use the new mermaid visualizer
                        visualizer = MermaidVisualizer()
                        spans = span_data.get("spans", [])
                        diagram = visualizer.generate_span_trace_diagram(spans)
                        console.print(Panel(
                            Syntax(diagram, "mermaid", theme="monokai"),
                            title="[bold cyan]Span Trace Visualization[/bold cyan]"
                        ))
                else:
                    progress.update(task, description="❌ Span analysis failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Span analysis failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_debug_spans())

@app.command("health")
def debug_health(
    ctx: typer.Context,
    components: List[str] = typer.Option(["all"], "--component", "-c", help="Components to check"),
    deep: bool = typer.Option(False, "--deep", help="Perform deep health check"),
    output_dir: Path = typer.Option(Path("./health_reports"), "--output", "-o"),
    generate_report: bool = typer.Option(True, "--report/--no-report")
):
    """Check system health and component status"""
    
    async def run_health_check():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "health_config": {
                "components": components if "all" not in components else None,
                "deep_check": deep,
                "include_dependencies": True,
                "include_metrics": True
            },
            "cli_command": "debug health"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🏥 Checking system health...", total=None)
            
            try:
                result = await engine.execute_workflow("health_check", context)
                
                if result.success:
                    health_data = result.final_data.get("health_status", {})
                    progress.update(task, description="✅ Health check complete")
                    
                    display_health_status(health_data, deep)
                    
                    if generate_report:
                        output_dir.mkdir(exist_ok=True)
                        report_file = output_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(report_file, 'w') as f:
                            json.dump(health_data, f, indent=2, default=str)
                        console.print(f"[green]Health report saved to: {report_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Health check failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Health check failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_health_check())

@app.command("inspect")
def debug_inspect(
    ctx: typer.Context,
    component: str = typer.Argument(help="Component to inspect: agents, models, conversations, spans, workflows"),
    item_id: Optional[str] = typer.Option(None, "--id", "-i", help="Specific item ID to inspect"),
    show_internals: bool = typer.Option(False, "--internals", help="Show internal details"),
    export: Optional[Path] = typer.Option(None, "--export", "-e", help="Export inspection data")
):
    """Deep inspection of system components"""
    
    async def run_inspect():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "component_type": component,
            "item_id": item_id,
            "inspection_config": {
                "show_internals": show_internals,
                "include_metadata": True,
                "include_relationships": True
            },
            "cli_command": "debug inspect"
        }
        
        console.print(f"[bold]Inspecting {component}{'#' + item_id if item_id else ''}...[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🔎 Inspecting {component}...", total=None)
            
            try:
                result = await engine.execute_workflow("component_inspection", context)
                
                if result.success:
                    inspection_data = result.final_data.get("inspection_result", {})
                    progress.update(task, description="✅ Inspection complete")
                    
                    display_inspection_results(inspection_data, component, show_internals)
                    
                    if export:
                        export.write_text(json.dumps(inspection_data, indent=2, default=str))
                        console.print(f"[green]Inspection data exported to: {export}[/green]")
                        
                else:
                    progress.update(task, description="❌ Inspection failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Inspection failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_inspect())

@app.command("trace")
def debug_trace(
    ctx: typer.Context,
    operation: str = typer.Argument(help="Operation to trace: communication, generation, validation"),
    duration: int = typer.Option(30, "--duration", "-d", help="Trace duration in seconds"),
    save_traces: bool = typer.Option(True, "--save/--no-save", help="Save trace data"),
    real_time: bool = typer.Option(False, "--real-time", help="Show real-time trace updates")
):
    """Trace specific operations for debugging"""
    
    async def run_trace():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "operation": operation,
            "trace_config": {
                "duration_seconds": duration,
                "capture_all_spans": True,
                "include_logs": True,
                "real_time_updates": real_time
            },
            "cli_command": "debug trace"
        }
        
        console.print(Panel(
            f"[bold yellow]Trace Configuration[/bold yellow]\n"
            f"Operation: {operation}\n"
            f"Duration: {duration}s\n"
            f"Real-time: {'Yes' if real_time else 'No'}",
            title="Starting Trace"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"📡 Tracing {operation}...", total=duration)
            
            try:
                # Simulate progress updates
                for i in range(duration):
                    await asyncio.sleep(1)
                    progress.update(task, completed=i+1)
                
                result = await engine.execute_workflow("operation_trace", context)
                
                if result.success:
                    trace_data = result.final_data.get("trace_result", {})
                    progress.update(task, description="✅ Trace complete")
                    
                    display_trace_results(trace_data, operation)
                    
                    if save_traces:
                        trace_file = Path(f"trace_{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                        with open(trace_file, 'w') as f:
                            json.dump(trace_data, f, indent=2, default=str)
                        console.print(f"[green]Trace data saved to: {trace_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Trace failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Trace failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_trace())

@app.command("performance")
def debug_performance(
    ctx: typer.Context,
    profile: str = typer.Option("cpu", "--profile", "-p", help="Profile type: cpu, memory, io"),
    duration: int = typer.Option(60, "--duration", "-d", help="Profiling duration in seconds"),
    output_format: str = typer.Option("flamegraph", "--format", help="Output format: flamegraph, report, raw")
):
    """Profile system performance"""
    
    async def run_performance():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "profile_config": {
                "profile_type": profile,
                "duration_seconds": duration,
                "sampling_rate": 100,
                "include_children": True
            },
            "output_format": output_format,
            "cli_command": "debug performance"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"⚡ Profiling {profile}...", total=None)
            
            try:
                result = await engine.execute_workflow("performance_profile", context)
                
                if result.success:
                    profile_data = result.final_data.get("profile_result", {})
                    progress.update(task, description="✅ Profiling complete")
                    
                    display_performance_results(profile_data, profile, output_format)
                else:
                    progress.update(task, description="❌ Profiling failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Profiling failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_performance())

@app.command("lifecycle")
def debug_lifecycle(
    ctx: typer.Context,
    type: str = typer.Option(
        "semantic",
        "--type", "-t",
        help="Lifecycle type: semantic, bpmn, agent, validation, full"
    ),
    semantic_file: Optional[Path] = typer.Option(
        None,
        "--semantic", "-s",
        help="Semantic convention YAML file"
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow", "-w",
        help="Workflow name for BPMN lifecycle"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Generate lifecycle visualization diagrams"""
    
    lifecycle_gen = MermaidLifecycleGenerator()
    
    console.print(f"[bold]Generating {type} lifecycle diagram...[/bold]")
    
    try:
        diagram = None
        
        if type == "semantic":
            if not semantic_file:
                console.print("[red]Error: --semantic file required for semantic lifecycle[/red]")
                raise typer.Exit(1)
            diagram = lifecycle_gen.generate_semantic_to_runtime_lifecycle(semantic_file)
            
        elif type == "bpmn":
            workflow_name = workflow or "DefaultWorkflow"
            diagram = lifecycle_gen.generate_bpmn_lifecycle(workflow_name)
            
        elif type == "agent":
            diagram = lifecycle_gen.generate_agent_lifecycle()
            
        elif type == "validation":
            diagram = lifecycle_gen.generate_validation_lifecycle()
            
        elif type == "full":
            # Generate comprehensive system lifecycle
            visualizer = MermaidVisualizer()
            lifecycle_data = {
                "components": {
                    "semantic": [{"name": "Parse"}, {"name": "Validate"}, {"name": "Extract"}],
                    "generation": [{"name": "Weaver"}, {"name": "Templates"}, {"name": "Code"}],
                    "validation": [{"name": "Semantic"}, {"name": "Spans"}, {"name": "Integration"}],
                    "agents": [{"name": "Initialize"}, {"name": "Configure"}, {"name": "Communicate"}],
                    "runtime": [{"name": "Execute"}, {"name": "Telemetry"}, {"name": "Monitor"}]
                }
            }
            diagram = visualizer.generate_lifecycle_diagram(lifecycle_data)
            
        else:
            console.print(f"[red]Unknown lifecycle type: {type}[/red]")
            raise typer.Exit(1)
        
        if diagram:
            # Display diagram
            console.print(Panel(
                Syntax(diagram, "mermaid", theme="monokai"),
                title=f"[bold cyan]{type.title()} Lifecycle Diagram[/bold cyan]"
            ))
            
            if output:
                output.write_text(f"```mermaid\n{diagram}\n```")
                console.print(f"[green]Diagram saved to: {output}[/green]")
                
    except Exception as e:
        console.print(f"[red]Error generating lifecycle: {e}[/red]")
        raise typer.Exit(1)

# Display helper functions

def display_span_analysis_rich(data: Dict[str, Any]):
    """Display span analysis with Rich formatting"""
    # Summary table
    table = Table(title="Span Analysis Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    summary = data.get("summary", {})
    table.add_row("Total Spans", str(summary.get("total_spans", 0)))
    table.add_row("Error Spans", str(summary.get("error_spans", 0)))
    table.add_row("Average Duration", f"{summary.get('avg_duration_ms', 0):.2f} ms")
    table.add_row("Max Duration", f"{summary.get('max_duration_ms', 0):.2f} ms")
    table.add_row("Services", str(summary.get("service_count", 0)))
    
    console.print(table)
    
    # Top operations
    top_operations = data.get("top_operations", [])
    if top_operations:
        console.print("\n[bold]Top Operations by Duration:[/bold]")
        for i, op in enumerate(top_operations[:5], 1):
            console.print(f"  {i}. {op['name']} - {op['avg_duration_ms']:.2f} ms ({op['count']} calls)")
    
    # Error breakdown
    errors = data.get("errors", [])
    if errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in errors[:5]:
            console.print(f"  • {error['operation']}: {error['message']}")

def display_span_analysis_mermaid(data: Dict[str, Any]):
    """Display span analysis as Mermaid diagram"""
    visualizer = MermaidVisualizer()
    
    # Use the raw spans if available for sequence diagram
    raw_spans = data.get("spans", [])
    if raw_spans:
        diagram = visualizer.generate_span_trace_diagram(raw_spans)
        console.print("```mermaid")
        console.print(diagram)
        console.print("```")
        return
    
    # Fallback to tree view if no raw spans
    spans = data.get("span_tree", [])
    
    mermaid_lines = ["graph TD"]
    
    def add_span(span, parent_id=None, indent=4):
        span_id = span['span_id'][:8]
        duration = span.get('duration_ms', 0)
        status = "✅" if not span.get('error') else "❌"
        
        label = f"{span['operation_name']}\\n{duration:.1f}ms {status}"
        mermaid_lines.append(f"{' ' * indent}{span_id}[\"{label}\"]")
        
        if parent_id:
            mermaid_lines.append(f"{' ' * indent}{parent_id} --> {span_id}")
        
        for child in span.get('children', []):
            add_span(child, span_id, indent + 4)
    
    for root_span in spans[:3]:  # Limit to 3 root spans
        add_span(root_span)
    
    console.print("```mermaid")
    console.print("\n".join(mermaid_lines))
    console.print("```")

def display_health_status(data: Dict[str, Any], deep: bool):
    """Display system health status"""
    overall_health = data.get("overall_status", "unknown")
    health_score = data.get("health_score", 0)
    
    status_color = {
        "healthy": "green",
        "degraded": "yellow",
        "unhealthy": "red"
    }.get(overall_health, "white")
    
    console.print(Panel(
        f"[bold {status_color}]System Status: {overall_health.upper()}[/bold {status_color}]\n"
        f"Health Score: {health_score:.1%}",
        title="Overall Health"
    ))
    
    # Component health
    components = data.get("components", {})
    if components:
        table = Table(title="Component Health")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Health", style="green")
        table.add_column("Issues", style="red")
        
        for comp_name, comp_data in components.items():
            status_icon = "✅" if comp_data.get("healthy", False) else "❌"
            table.add_row(
                comp_name,
                f"{status_icon} {comp_data.get('status', 'unknown')}",
                f"{comp_data.get('health_score', 0):.0%}",
                str(comp_data.get('issue_count', 0))
            )
        
        console.print(table)
    
    if deep:
        # Show detailed issues
        issues = data.get("issues", [])
        if issues:
            console.print("\n[bold]Detected Issues:[/bold]")
            for issue in issues:
                severity_color = {
                    "critical": "red",
                    "warning": "yellow",
                    "info": "blue"
                }.get(issue['severity'], "white")
                console.print(f"  [{severity_color}]{issue['severity'].upper()}[/{severity_color}]: {issue['message']} ({issue['component']})")

def display_inspection_results(data: Dict[str, Any], component: str, show_internals: bool):
    """Display component inspection results"""
    tree = Tree(f"[bold cyan]{component.capitalize()} Inspection[/bold cyan]")
    
    # Basic info
    info_branch = tree.add("📋 Basic Information")
    for key, value in data.get("basic_info", {}).items():
        info_branch.add(f"{key}: {value}")
    
    # Metadata
    metadata = data.get("metadata", {})
    if metadata:
        meta_branch = tree.add("📊 Metadata")
        for key, value in metadata.items():
            meta_branch.add(f"{key}: {value}")
    
    # Relationships
    relationships = data.get("relationships", [])
    if relationships:
        rel_branch = tree.add("🔗 Relationships")
        for rel in relationships[:10]:
            rel_branch.add(f"{rel['type']}: {rel['target']}")
    
    if show_internals:
        internals = data.get("internals", {})
        if internals:
            int_branch = tree.add("⚙️ Internal Details")
            for key, value in internals.items():
                if isinstance(value, dict):
                    sub_branch = int_branch.add(key)
                    for k, v in value.items():
                        sub_branch.add(f"{k}: {v}")
                else:
                    int_branch.add(f"{key}: {value}")
    
    console.print(tree)

def display_trace_results(data: Dict[str, Any], operation: str):
    """Display operation trace results"""
    table = Table(title=f"Trace Results: {operation}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    metrics = data.get("metrics", {})
    table.add_row("Total Operations", str(metrics.get("total_operations", 0)))
    table.add_row("Success Rate", f"{metrics.get('success_rate', 0):.1%}")
    table.add_row("Average Latency", f"{metrics.get('avg_latency_ms', 0):.2f} ms")
    table.add_row("P95 Latency", f"{metrics.get('p95_latency_ms', 0):.2f} ms")
    table.add_row("Throughput", f"{metrics.get('throughput_ops_sec', 0):.1f} ops/s")
    
    console.print(table)
    
    # Operation breakdown
    operations = data.get("operation_breakdown", [])
    if operations:
        console.print("\n[bold]Operation Breakdown:[/bold]")
        for op in operations[:10]:
            console.print(f"  • {op['name']}: {op['count']} calls, {op['avg_duration_ms']:.2f} ms avg")

def display_performance_results(data: Dict[str, Any], profile_type: str, output_format: str):
    """Display performance profiling results"""
    if output_format == "flamegraph":
        console.print("[bold]Flamegraph Data:[/bold]")
        console.print("🔥 Flamegraph visualization would be displayed here")
        console.print(f"[dim]Profile data saved to: {data.get('flamegraph_file', 'profile.svg')}[/dim]")
    elif output_format == "report":
        # Performance report
        report = data.get("report", {})
        
        console.print(Panel(
            f"[bold]Performance Profile: {profile_type.upper()}[/bold]\n"
            f"Duration: {report.get('duration_seconds', 0)}s\n"
            f"Samples: {report.get('sample_count', 0)}",
            title="Profile Summary"
        ))
        
        # Top consumers
        top_consumers = report.get("top_consumers", [])
        if top_consumers:
            table = Table(title=f"Top {profile_type.capitalize()} Consumers")
            table.add_column("Function", style="cyan")
            table.add_column("Percentage", style="red")
            table.add_column("Cumulative", style="yellow")
            
            for consumer in top_consumers[:10]:
                table.add_row(
                    consumer['function'],
                    f"{consumer['percentage']:.1%}",
                    f"{consumer['cumulative']:.1%}"
                )
            
            console.print(table)
    else:
        # Raw data
        console.print_json(json.dumps(data, indent=2, default=str))

@app.command("lifecycle")
def debug_lifecycle(
    ctx: typer.Context,
    component: str = typer.Argument(help="Component lifecycle to visualize: semantic, bpmn, agent, validation, full"),
    semantic_file: Optional[Path] = typer.Option(None, "--semantic", "-s", help="Semantic convention file"),
    workflow: Optional[str] = typer.Option(None, "--workflow", "-w", help="Workflow name for BPMN lifecycle"),
    agents: int = typer.Option(3, "--agents", "-a", help="Number of agents for agent lifecycle"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save diagram to file"),
    format: str = typer.Option("mermaid", "--format", help="Output format: mermaid, svg, png")
):
    """Generate lifecycle diagrams for system components"""
    
    visualizer = MermaidVisualizer()
    lifecycle_gen = MermaidLifecycleGenerator(visualizer)
    
    console.print(f"[bold cyan]🔄 Generating {component} lifecycle diagram...[/bold cyan]")
    
    try:
        diagram = ""
        
        if component == "semantic":
            if not semantic_file:
                console.print("[red]Error: --semantic file required for semantic lifecycle[/red]")
                raise typer.Exit(1)
            diagram = lifecycle_gen.generate_semantic_to_runtime_lifecycle(semantic_file)
            
        elif component == "bpmn":
            workflow_name = workflow or "default_workflow"
            diagram = lifecycle_gen.generate_bpmn_lifecycle(workflow_name)
            
        elif component == "agent":
            diagram = lifecycle_gen.generate_agent_lifecycle(agents)
            
        elif component == "validation":
            diagram = lifecycle_gen.generate_validation_lifecycle()
            
        elif component == "full":
            # Generate comprehensive system lifecycle
            lines = ["graph TB"]
            lines.append("    %% Complete WeaverGen v2 Lifecycle")
            lines.append("    ")
            lines.append("    subgraph Input[Input Phase]")
            lines.append("        YAML[Semantic YAML]")
            lines.append("        BPMN[BPMN Workflows]")
            lines.append("    end")
            lines.append("    ")
            lines.append("    subgraph Processing[Processing Phase]")
            lines.append("        WF[Weaver Forge]")
            lines.append("        SPIFF[SpiffWorkflow Engine]")
            lines.append("        GEN[Code Generation]")
            lines.append("    end")
            lines.append("    ")
            lines.append("    subgraph Runtime[Runtime Phase]")
            lines.append("        AGENTS[AI Agents]")
            lines.append("        OTEL[OpenTelemetry]")
            lines.append("        EXEC[Execution]")
            lines.append("    end")
            lines.append("    ")
            lines.append("    subgraph Output[Output Phase]")
            lines.append("        SPANS[Telemetry Spans]")
            lines.append("        VALID[Validation Results]")
            lines.append("        REPORT[Health Reports]")
            lines.append("    end")
            lines.append("    ")
            lines.append("    YAML --> WF")
            lines.append("    BPMN --> SPIFF")
            lines.append("    WF --> GEN")
            lines.append("    SPIFF --> GEN")
            lines.append("    GEN --> AGENTS")
            lines.append("    AGENTS --> EXEC")
            lines.append("    EXEC --> OTEL")
            lines.append("    OTEL --> SPANS")
            lines.append("    SPANS --> VALID")
            lines.append("    VALID --> REPORT")
            
            diagram = "\n".join(lines)
        else:
            console.print(f"[red]Unknown component: {component}[/red]")
            console.print("[yellow]Valid components: semantic, bpmn, agent, validation, full[/yellow]")
            raise typer.Exit(1)
        
        # Display the diagram
        if format == "mermaid":
            console.print("\n[bold]Mermaid Diagram:[/bold]")
            console.print("```mermaid")
            console.print(diagram)
            console.print("```")
        else:
            console.print(f"[yellow]Note: {format} format export not yet implemented[/yellow]")
        
        # Save to file if requested
        if output:
            output.write_text(diagram)
            console.print(f"[green]✅ Diagram saved to: {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error generating lifecycle diagram: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()