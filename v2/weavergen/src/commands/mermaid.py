"""
WeaverGen v2 Mermaid Command Module
80/20 port of mermaid lifecycle commands with enhanced visualization
"""

import typer
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
from datetime import datetime

from ..visualizers.mermaid import MermaidVisualizer, MermaidLifecycleGenerator
from ..engine.contracts import ExecutionContext
from ..engine.operations import OperationsLayer
from ..engine.runtime import RuntimeEngine

app = typer.Typer(help="Mermaid diagram generation commands")
console = Console()

# Initialize visualizers
visualizer = MermaidVisualizer()
lifecycle_generator = MermaidLifecycleGenerator(visualizer)


@app.command()
def lifecycle(
    type: str = typer.Argument(
        "semantic",
        help="Type of lifecycle to visualize: semantic, bpmn, agent, validation, full"
    ),
    semantic_file: Optional[Path] = typer.Option(
        None,
        "--semantic", "-s",
        help="Semantic convention YAML file (for semantic lifecycle)"
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow", "-w",
        help="Workflow name (for BPMN lifecycle)"
    ),
    agents: int = typer.Option(
        3,
        "--agents", "-a",
        help="Number of agents (for agent lifecycle)"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
    include_data: bool = typer.Option(
        False,
        "--include-data", "-d",
        help="Include data flow in lifecycle"
    ),
):
    """Generate lifecycle diagrams showing system flow from start to finish"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating lifecycle diagram...", total=None)
        
        try:
            diagram = None
            
            if type == "semantic":
                if not semantic_file:
                    console.print("[red]Error: --semantic file required for semantic lifecycle[/red]")
                    raise typer.Exit(1)
                diagram = lifecycle_generator.generate_semantic_to_runtime_lifecycle(semantic_file)
                
            elif type == "bpmn":
                workflow_name = workflow or "DefaultWorkflow"
                diagram = lifecycle_generator.generate_bpmn_lifecycle(workflow_name)
                
            elif type == "agent":
                diagram = lifecycle_generator.generate_agent_lifecycle(agents)
                
            elif type == "validation":
                diagram = lifecycle_generator.generate_validation_lifecycle()
                
            elif type == "full":
                # Generate comprehensive system lifecycle
                diagram = _generate_full_lifecycle(semantic_file, workflow, agents, include_data)
                
            else:
                console.print(f"[red]Unknown lifecycle type: {type}[/red]")
                raise typer.Exit(1)
            
            progress.update(task, completed=True)
            
            # Display diagram
            if diagram:
                _display_diagram(diagram, f"{type.title()} Lifecycle", output)
                
        except Exception as e:
            console.print(f"[red]Error generating lifecycle: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def spans(
    span_file: Path = typer.Argument(help="OpenTelemetry span file (JSON, JSONL, CSV, or log format)"),
    diagram_type: str = typer.Option(
        "sequence",
        "--type", "-t",
        help="Diagram type: sequence, trace, service, timeline"
    ),
    max_spans: int = typer.Option(
        50,
        "--max", "-m",
        help="Maximum number of spans to visualize"
    ),
    trace_id: Optional[str] = typer.Option(
        None,
        "--trace-id",
        help="Specific trace ID to visualize (for trace diagrams)"
    ),
    include_timing: bool = typer.Option(
        True,
        "--timing/--no-timing",
        help="Include timing information in diagrams"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Convert OpenTelemetry span files to mermaid diagrams"""
    
    from ..span_parser import convert_span_file_to_mermaid, SpanFileParser, SpanToMermaidConverter
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔄 Processing span file...", total=None)
        
        try:
            if not span_file.exists():
                console.print(f"[red]Error: Span file not found: {span_file}[/red]")
                raise typer.Exit(1)
            
            progress.update(task, description="📁 Parsing span file...")
            
            # Parse span file
            parser = SpanFileParser()
            spans = parser.parse_file(span_file)
            
            if not spans:
                console.print("[yellow]No spans found in file[/yellow]")
                progress.update(task, description="⚠️ No spans found")
                return
            
            progress.update(task, description=f"📊 Generating {diagram_type} diagram...")
            
            # Convert to mermaid
            converter = SpanToMermaidConverter(spans)
            
            if diagram_type == "sequence":
                diagram = converter.to_sequence_diagram(max_spans=max_spans, include_timing=include_timing)
            elif diagram_type == "trace":
                diagram = converter.to_trace_flow_diagram(trace_id=trace_id)
            elif diagram_type == "service":
                diagram = converter.to_service_map_diagram()
            elif diagram_type == "timeline":
                diagram = converter.to_timeline_diagram(max_spans=max_spans)
            else:
                console.print(f"[red]Unknown diagram type: {diagram_type}[/red]")
                console.print("[dim]Available types: sequence, trace, service, timeline[/dim]")
                raise typer.Exit(1)
            
            progress.update(task, description="✅ Diagram generation complete")
            
            # Display results
            console.print(f"\n[bold green]✅ Processed {len(spans)} spans from {span_file.name}[/bold green]")
            
            # Show span statistics
            services = set(span.service_name for span in spans)
            traces = set(span.trace_id for span in spans)
            errors = len([span for span in spans if span.error])
            
            stats_table = Table(title="Span File Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            
            stats_table.add_row("Total Spans", str(len(spans)))
            stats_table.add_row("Services", str(len(services)))
            stats_table.add_row("Traces", str(len(traces)))
            stats_table.add_row("Error Spans", str(errors))
            stats_table.add_row("Diagram Type", diagram_type.title())
            
            console.print(stats_table)
            
            _display_diagram(diagram, f"Span {diagram_type.title()} Visualization", output)
            
        except Exception as e:
            progress.update(task, description="❌ Processing failed")
            console.print(f"[red]Error processing span file: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def architecture(
    style: str = typer.Option(
        "full",
        "--style", "-s",
        help="Architecture style: full, core, layers, external"
    ),
    include_flows: bool = typer.Option(
        False,
        "--flows", "-f",
        help="Include data flows"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Generate system architecture diagrams"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating architecture diagram...", total=None)
        
        try:
            arch_data = _build_architecture_data(style, include_flows)
            diagram = visualizer.generate_system_architecture_diagram(arch_data)
            progress.update(task, completed=True)
            
            _display_diagram(diagram, f"{style.title()} Architecture", output)
            
        except Exception as e:
            console.print(f"[red]Error generating architecture: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def workflow(
    workflow_file: Optional[Path] = typer.Option(
        None,
        "--file", "-f",
        help="BPMN workflow file to visualize"
    ),
    style: str = typer.Option(
        "flow",
        "--style", "-s",
        help="Visualization style: flow, sequence, state"
    ),
    include_data: bool = typer.Option(
        False,
        "--data", "-d",
        help="Include data objects"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Generate workflow visualization from BPMN files"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing workflow...", total=None)
        
        try:
            # Build workflow data
            workflow_data = _parse_workflow_file(workflow_file) if workflow_file else _get_sample_workflow()
            
            if style == "flow":
                diagram = visualizer.generate_workflow_visualization(workflow_data)
            elif style == "sequence":
                # Convert to sequence diagram format
                diagram = _workflow_to_sequence(workflow_data)
            elif style == "state":
                # Convert to state diagram
                diagram = _workflow_to_state(workflow_data)
            else:
                console.print(f"[red]Unknown style: {style}[/red]")
                raise typer.Exit(1)
            
            progress.update(task, completed=True)
            
            _display_diagram(diagram, "Workflow Visualization", output)
            
        except Exception as e:
            console.print(f"[red]Error visualizing workflow: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def performance(
    metrics_file: Optional[Path] = typer.Option(
        None,
        "--metrics", "-m",
        help="Performance metrics file (JSON)"
    ),
    compare: Optional[Path] = typer.Option(
        None,
        "--compare", "-c",
        help="Compare with baseline metrics"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Generate performance visualization diagrams"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing performance metrics...", total=None)
        
        try:
            # Load metrics
            if metrics_file and metrics_file.exists():
                with open(metrics_file) as f:
                    perf_data = json.load(f)
            else:
                # Use sample data
                perf_data = _get_sample_performance_data()
            
            # Generate diagram
            diagram = visualizer.generate_performance_diagram(perf_data)
            
            if compare and compare.exists():
                # Add comparison overlay
                with open(compare) as f:
                    baseline = json.load(f)
                diagram = _add_performance_comparison(diagram, perf_data, baseline)
            
            progress.update(task, completed=True)
            
            _display_diagram(diagram, "Performance Metrics", output)
            
        except Exception as e:
            console.print(f"[red]Error generating performance diagram: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def communication(
    agents: int = typer.Option(
        3,
        "--agents", "-a",
        help="Number of agents to simulate"
    ),
    scenario: str = typer.Option(
        "decision",
        "--scenario", "-s",
        help="Communication scenario: decision, collaboration, hierarchical"
    ),
    include_spans: bool = typer.Option(
        True,
        "--spans",
        help="Include OTel span annotations"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Generate agent communication diagrams"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Building communication flow...", total=None)
        
        try:
            # Build communication data based on scenario
            comm_data = _build_communication_scenario(agents, scenario, include_spans)
            
            # Generate diagram
            diagram = visualizer.generate_agent_communication_diagram(comm_data)
            
            progress.update(task, completed=True)
            
            _display_diagram(diagram, f"Agent Communication - {scenario.title()}", output)
            
        except Exception as e:
            console.print(f"[red]Error generating communication diagram: {e}[/red]")
            raise typer.Exit(1)


# Helper functions

def _display_diagram(diagram: str, title: str, output_path: Optional[Path] = None):
    """Display or save mermaid diagram"""
    
    # Wrap in mermaid code block
    full_diagram = f"```mermaid\n{diagram}\n```"
    
    if output_path:
        # Save to file
        output_path.write_text(full_diagram)
        console.print(f"[green]✓ Diagram saved to {output_path}[/green]")
    
    # Display in console
    panel = Panel(
        Syntax(diagram, "mermaid", theme="monokai"),
        title=f"[bold cyan]{title}[/bold cyan]",
        expand=False
    )
    console.print(panel)
    
    console.print("\n[dim]Copy the diagram above and paste into any Mermaid viewer[/dim]")


def _generate_full_lifecycle(
    semantic_file: Optional[Path],
    workflow: Optional[str],
    agents: int,
    include_data: bool
) -> str:
    """Generate comprehensive system lifecycle diagram"""
    
    lines = ["graph TB"]
    lines.append("    %% Complete WeaverGen v2 Lifecycle")
    
    # Main flow
    lines.append("    Start([Start]) --> Input[Input: Semantic Conventions]")
    lines.append("    Input --> Parse[Parse YAML]")
    lines.append("    Parse --> Validate[Validate Schema]")
    lines.append("    Validate --> Generate[Generate Code<br/>via Weaver Forge]")
    lines.append("    Generate --> BPMN[Execute BPMN Workflows]")
    lines.append("    BPMN --> Agents[Initialize Agent System]")
    lines.append("    Agents --> Runtime[Runtime Execution]")
    lines.append("    Runtime --> Telemetry[Capture OTel Spans]")
    lines.append("    Telemetry --> Monitor[Monitor & Validate]")
    lines.append("    Monitor --> End([End])")
    
    if include_data:
        lines.append("    %% Data Flow")
        lines.append("    Input -.->|YAML| DataStore[(Data Store)]")
        lines.append("    Generate -.->|Generated Code| DataStore")
        lines.append("    Telemetry -.->|Spans| DataStore")
    
    # Add styling
    lines.append("    classDef input fill:#e1f5e1,stroke:#4caf50")
    lines.append("    classDef process fill:#e3f2fd,stroke:#2196f3")
    lines.append("    classDef output fill:#fff3e0,stroke:#ff9800")
    
    lines.append("    class Input,Parse,Validate input")
    lines.append("    class Generate,BPMN,Agents,Runtime process")
    lines.append("    class Telemetry,Monitor output")
    
    return "\n".join(lines)


def _build_architecture_data(style: str, include_flows: bool) -> dict:
    """Build architecture data for visualization"""
    
    return {
        "style": style,
        "include_flows": include_flows,
        "components": {
            "core": ["SpiffWorkflow", "Weaver Forge", "AI Agents"],
            "layers": ["Commands", "Operations", "Runtime", "Contracts"],
            "external": ["OpenTelemetry", "LLM Provider", "File System"]
        }
    }


def _parse_workflow_file(workflow_file: Path) -> dict:
    """Parse BPMN workflow file (placeholder)"""
    
    # TODO: Implement actual BPMN parsing
    return _get_sample_workflow()


def _get_sample_workflow() -> dict:
    """Get sample workflow data"""
    
    return {
        "tasks": [
            {"name": "Load Semantic Conventions", "type": "service"},
            {"name": "Validate Input", "type": "service"},
            {"name": "Generate Code", "type": "service"},
            {"name": "Run Tests", "type": "service"},
            {"name": "Deploy", "type": "user"}
        ],
        "gateways": [
            {"type": "exclusive", "name": "Validation Check"},
            {"type": "parallel", "name": "Multi-Language Generation"}
        ],
        "connections": [
            {"from": "Start", "to": "T0"},
            {"from": "T0", "to": "T1"},
            {"from": "T1", "to": "G0"},
            {"from": "G0", "to": "T2", "label": "Valid"},
            {"from": "G0", "to": "End", "label": "Invalid"},
            {"from": "T2", "to": "G1"},
            {"from": "G1", "to": "T3"},
            {"from": "T3", "to": "T4"},
            {"from": "T4", "to": "End"}
        ]
    }


def _workflow_to_sequence(workflow_data: dict) -> str:
    """Convert workflow to sequence diagram"""
    
    lines = ["sequenceDiagram"]
    lines.append("    participant User")
    lines.append("    participant Engine as Workflow Engine")
    lines.append("    participant Service as Service Tasks")
    
    for task in workflow_data.get("tasks", []):
        if task["type"] == "user":
            lines.append(f"    User->>Engine: {task['name']}")
        else:
            lines.append(f"    Engine->>Service: {task['name']}")
            lines.append(f"    Service-->>Engine: Complete")
    
    return "\n".join(lines)


def _workflow_to_state(workflow_data: dict) -> str:
    """Convert workflow to state diagram"""
    
    lines = ["stateDiagram-v2"]
    lines.append("    [*] --> Initialize")
    
    for i, task in enumerate(workflow_data.get("tasks", [])):
        state_name = task["name"].replace(" ", "_")
        if i == 0:
            lines.append(f"    Initialize --> {state_name}")
        else:
            prev_state = workflow_data["tasks"][i-1]["name"].replace(" ", "_")
            lines.append(f"    {prev_state} --> {state_name}")
    
    if workflow_data.get("tasks"):
        last_state = workflow_data["tasks"][-1]["name"].replace(" ", "_")
        lines.append(f"    {last_state} --> [*]")
    
    return "\n".join(lines)


def _get_sample_performance_data() -> dict:
    """Get sample performance metrics"""
    
    return {
        "metrics": {
            "avg_latency_ms": 42.5,
            "throughput_ops_sec": 1250.3,
            "memory_mb": 512.8,
            "cpu_percent": 35.2,
            "error_rate": 0.02,
            "p99_latency_ms": 98.7
        },
        "timestamp": datetime.utcnow().isoformat()
    }


def _add_performance_comparison(diagram: str, current: dict, baseline: dict) -> str:
    """Add performance comparison to diagram"""
    
    lines = diagram.split("\n")
    
    # Insert comparison data
    comparison_lines = [
        "",
        "    subgraph Comparison[vs Baseline]",
        f"        CLAT[Current Latency<br/>{current['metrics']['avg_latency_ms']:.1f}ms]",
        f"        BLAT[Baseline Latency<br/>{baseline['metrics']['avg_latency_ms']:.1f}ms]",
        f"        DIFF[Difference<br/>{current['metrics']['avg_latency_ms'] - baseline['metrics']['avg_latency_ms']:+.1f}ms]",
        "    end"
    ]
    
    # Find insertion point (before closing)
    insert_idx = len(lines) - 1
    for i, line in enumerate(lines):
        if "end" in line.lower():
            insert_idx = i
            break
    
    # Insert comparison
    lines[insert_idx:insert_idx] = comparison_lines
    
    return "\n".join(lines)


def _build_communication_scenario(agents: int, scenario: str, include_spans: bool) -> dict:
    """Build agent communication scenario data"""
    
    agent_list = []
    messages = []
    
    # Create agents
    for i in range(agents):
        agent_list.append({
            "id": f"agent{i}",
            "name": f"Agent_{i}"
        })
    
    # Build scenario
    if scenario == "decision":
        # Decision making scenario
        messages.extend([
            {"from": "agent0", "to": "agent1", "type": "request", "content": "Need approval"},
            {"from": "agent1", "to": "agent0", "type": "decision", "content": "Approved", "duration_ms": 150},
            {"from": "agent0", "to": "agent2", "type": "notify", "content": "Decision made"}
        ])
    
    elif scenario == "collaboration":
        # Collaborative scenario
        for i in range(agents - 1):
            messages.append({
                "from": f"agent{i}",
                "to": f"agent{i+1}",
                "type": "collaborate",
                "content": f"Task part {i+1}",
                "duration_ms": 100 + i * 50
            })
    
    elif scenario == "hierarchical":
        # Hierarchical communication
        messages.append({"from": "agent0", "to": "OTel", "type": "broadcast", "content": "New directive"})
        for i in range(1, agents):
            messages.append({
                "from": f"agent{i}",
                "to": "agent0",
                "type": "response",
                "content": f"Acknowledged by Agent_{i}",
                "duration_ms": 50 + i * 25
            })
    
    return {
        "agents": agent_list,
        "messages": messages,
        "include_spans": include_spans
    }


if __name__ == "__main__":
    app()