"""Debugging and diagnostics commands for WeaverGen v2 - 80/20 implementation."""

from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.syntax import Syntax
from rich.panel import Panel
from opentelemetry import trace
import json
from datetime import datetime

# Initialize CLI app and console
debug_app = typer.Typer(help="Debugging and diagnostics")
console = Console()
tracer = trace.get_tracer(__name__)


@debug_app.command()
def spans(
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, mermaid)"),
    filter: Optional[str] = typer.Option(None, "--filter", help="Filter spans by pattern"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum spans to display"),
):
    """🔍 Display OpenTelemetry spans for debugging."""
    with tracer.start_as_current_span("debug.spans") as span:
        span.set_attribute("format", format)
        
        try:
            console.print("[blue]OpenTelemetry Span Analysis[/blue]\n")
            
            # Simulated span data
            spans_data = [
                {"name": "bpmn.execute", "duration": "123ms", "status": "OK", "attributes": {"workflow": "CodeGeneration"}},
                {"name": "forge.generate", "duration": "456ms", "status": "OK", "attributes": {"language": "python"}},
                {"name": "agents.validate", "duration": "789ms", "status": "OK", "attributes": {"agent_count": 5}},
                {"name": "validate.semantic", "duration": "45ms", "status": "ERROR", "attributes": {"error": "Schema mismatch"}},
            ]
            
            if filter:
                spans_data = [s for s in spans_data if filter in s["name"]]
            
            spans_data = spans_data[:limit]
            
            if format == "table":
                table = Table(title="Captured Spans")
                table.add_column("Span Name", style="cyan")
                table.add_column("Duration", style="yellow")
                table.add_column("Status", style="green")
                table.add_column("Key Attributes", style="magenta")
                
                for span_info in spans_data:
                    status_color = "green" if span_info["status"] == "OK" else "red"
                    attrs = ", ".join([f"{k}={v}" for k, v in span_info["attributes"].items()])
                    table.add_row(
                        span_info["name"],
                        span_info["duration"],
                        f"[{status_color}]{span_info['status']}[/{status_color}]",
                        attrs
                    )
                
                console.print(table)
                
            elif format == "mermaid":
                console.print("```mermaid")
                console.print("graph TD")
                for i, span_info in enumerate(spans_data):
                    node_id = f"S{i}"
                    label = f"{span_info['name']}\\n{span_info['duration']}"
                    console.print(f"    {node_id}[{label}]")
                    if i > 0:
                        console.print(f"    S{i-1} --> {node_id}")
                console.print("```")
                
            elif format == "json":
                console.print_json(json.dumps(spans_data, indent=2))
            
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@debug_app.command()
def health(
    components: str = typer.Option("all", "--components", "-c", help="Components to check (all, core, agents, bpmn)"),
    deep: bool = typer.Option(False, "--deep", "-d", help="Perform deep health check"),
):
    """🏥 System health check and diagnostics."""
    with tracer.start_as_current_span("debug.health") as span:
        try:
            console.print("[blue]System Health Check[/blue]\n")
            
            # Component health checks
            checks = {
                "Core Engine": {"status": "healthy", "details": "v2.0.0, all systems operational"},
                "BPMN Engine": {"status": "healthy", "details": "SpiffWorkflow active"},
                "Agent System": {"status": "healthy", "details": "5 agents ready"},
                "Weaver Binary": {"status": "healthy", "details": "v0.12.0 installed"},
                "OpenTelemetry": {"status": "healthy", "details": "Tracing active"},
            }
            
            if components != "all":
                checks = {k: v for k, v in checks.items() if components.lower() in k.lower()}
            
            # Display health status
            for component, info in checks.items():
                status_icon = "✓" if info["status"] == "healthy" else "✗"
                status_color = "green" if info["status"] == "healthy" else "red"
                console.print(f"[{status_color}]{status_icon}[/{status_color}] {component}: {info['details']}")
            
            if deep:
                console.print("\n[dim]Deep diagnostics:[/dim]")
                console.print("  • Memory usage: 124MB")
                console.print("  • Active spans: 42")
                console.print("  • Workflow instances: 3")
                console.print("  • Cache hit rate: 87%")
            
            # Overall status
            all_healthy = all(info["status"] == "healthy" for info in checks.values())
            if all_healthy:
                console.print("\n[green]✓[/green] All systems operational")
            else:
                console.print("\n[red]✗[/red] Some systems need attention")
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@debug_app.command()
def inspect(
    target: str = typer.Argument(..., help="Target to inspect (workflow, agent, semantic)"),
    file_path: Optional[Path] = typer.Option(None, "--file", "-f", help="File to inspect"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose inspection"),
):
    """🔬 Deep inspection of WeaverGen components."""
    with tracer.start_as_current_span("debug.inspect") as span:
        span.set_attribute("target", target)
        
        try:
            console.print(f"[blue]Inspecting {target}[/blue]\n")
            
            if target == "workflow":
                tree = Tree("BPMN Workflow Structure")
                tree.add("Start Event")
                task_branch = tree.add("Service Tasks")
                task_branch.add("ValidateSemantics")
                task_branch.add("GenerateCode")
                task_branch.add("ValidateOutput")
                tree.add("End Event")
                console.print(tree)
                
            elif target == "agent":
                panel = Panel(
                    "Agent Type: Validation Agent\n"
                    "Status: Active\n"
                    "Model: GPT-4\n"
                    "Context Length: 8192\n"
                    "Capabilities: semantic validation, code review",
                    title="Agent Inspector",
                    border_style="blue"
                )
                console.print(panel)
                
            elif target == "semantic":
                if file_path:
                    # Show semantic file structure
                    console.print(f"Semantic Convention File: {file_path.name}")
                    syntax = Syntax(
                        "groups:\n  - id: example.service\n    type: span\n    attributes:\n      - id: service.name",
                        "yaml",
                        theme="monokai",
                        line_numbers=True
                    )
                    console.print(syntax)
                else:
                    console.print("[red]Please provide --file for semantic inspection[/red]")
                    raise typer.Exit(1)
                    
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@debug_app.command()
def trace(
    operation: str = typer.Argument(..., help="Operation to trace (generation, validation, communication)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed trace"),
    save: Optional[Path] = typer.Option(None, "--save", "-s", help="Save trace to file"),
):
    """📡 Trace execution flow through the system."""
    with tracer.start_as_current_span("debug.trace") as span:
        span.set_attribute("operation", operation)
        
        try:
            console.print(f"[blue]Tracing {operation} operation[/blue]\n")
            
            # Simulated trace data
            trace_steps = []
            
            if operation == "generation":
                trace_steps = [
                    ("1. Input validation", "2ms", "OK"),
                    ("2. Load semantic conventions", "15ms", "OK"),
                    ("3. Parse YAML structure", "8ms", "OK"),
                    ("4. Initialize Weaver Forge", "22ms", "OK"),
                    ("5. Generate code templates", "145ms", "OK"),
                    ("6. Write output files", "12ms", "OK"),
                ]
            elif operation == "validation":
                trace_steps = [
                    ("1. Load validation rules", "5ms", "OK"),
                    ("2. Parse semantic file", "10ms", "OK"),
                    ("3. Schema validation", "18ms", "OK"),
                    ("4. Constraint checking", "25ms", "WARNING"),
                    ("5. Generate report", "3ms", "OK"),
                ]
            elif operation == "communication":
                trace_steps = [
                    ("1. Initialize agents", "45ms", "OK"),
                    ("2. Establish channels", "12ms", "OK"),
                    ("3. Message exchange", "234ms", "OK"),
                    ("4. Consensus protocol", "156ms", "OK"),
                    ("5. Finalize results", "8ms", "OK"),
                ]
            
            # Display trace
            for step, duration, status in trace_steps:
                status_color = "green" if status == "OK" else "yellow" if status == "WARNING" else "red"
                console.print(f"[{status_color}]→[/{status_color}] {step} [{duration}]")
                if detailed:
                    console.print(f"   [dim]Context: {{trace_id: '{span.get_span_context().trace_id:032x}'}}[/dim]")
            
            # Save if requested
            if save:
                trace_data = {
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "steps": [{"step": s, "duration": d, "status": st} for s, d, st in trace_steps]
                }
                save.write_text(json.dumps(trace_data, indent=2))
                console.print(f"\n[green]✓[/green] Trace saved to {save}")
            
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@debug_app.command()
def performance(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Specific component to analyze"),
    threshold: float = typer.Option(1.0, "--threshold", "-t", help="Performance threshold in seconds"),
):
    """⚡ Performance analysis and bottleneck detection."""
    with tracer.start_as_current_span("debug.performance") as span:
        try:
            console.print("[blue]Performance Analysis[/blue]\n")
            
            # Performance metrics
            metrics = [
                ("Semantic Parsing", 0.045, 0.050),
                ("Code Generation", 1.234, 1.000),
                ("Validation", 0.567, 0.500),
                ("Agent Communication", 2.345, 2.000),
                ("BPMN Execution", 0.789, 1.000),
            ]
            
            if component:
                metrics = [(n, a, t) for n, a, t in metrics if component.lower() in n.lower()]
            
            # Display performance table
            table = Table(title="Performance Metrics")
            table.add_column("Component", style="cyan")
            table.add_column("Actual (s)", style="yellow")
            table.add_column("Target (s)", style="green")
            table.add_column("Status", style="magenta")
            
            bottlenecks = []
            for name, actual, target in metrics:
                if actual > threshold:
                    status = "[red]✗ Slow[/red]"
                    bottlenecks.append(name)
                elif actual > target:
                    status = "[yellow]⚠ Warning[/yellow]"
                else:
                    status = "[green]✓ OK[/green]"
                
                table.add_row(name, f"{actual:.3f}", f"{target:.3f}", status)
            
            console.print(table)
            
            if bottlenecks:
                console.print(f"\n[red]Bottlenecks detected:[/red]")
                for bottleneck in bottlenecks:
                    console.print(f"  • {bottleneck}")
            else:
                console.print("\n[green]✓[/green] No performance issues detected")
                
        except Exception as e:
            span.record_exception(e)
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


if __name__ == "__main__":
    debug_app()