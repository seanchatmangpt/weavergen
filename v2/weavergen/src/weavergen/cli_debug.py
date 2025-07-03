"""Debug subcommand for WeaverGen v2 - span visualization and debugging."""

import json
from typing import Optional
from datetime import datetime
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    ConsoleSpanExporter,
    BatchSpanProcessor
)

# Create debug subcommand app
debug_app = typer.Typer(help="Debug and visualize OpenTelemetry spans")
console = Console()

# In-memory span storage for debugging
SPAN_FILE = Path("/tmp/weavergen_spans.json")

class InMemorySpanExporter:
    """Simple in-memory span storage."""
    def __init__(self):
        self.spans = self._load_spans()
    
    def export(self, spans):
        for span in spans:
            self.spans.append(self._serialize_span(span))
        self._save_spans()
        return True
    
    def get_finished_spans(self):
        # Deserialize spans when retrieved
        return [self._deserialize_span(s) for s in self.spans]
    
    def clear(self):
        self.spans = []
        self._save_spans()

    def shutdown(self):
        self._save_spans()

    def _load_spans(self):
        if SPAN_FILE.exists():
            try:
                with open(SPAN_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_spans(self):
        with open(SPAN_FILE, 'w') as f:
            json.dump(self.spans, f, indent=2, default=str)

    def _serialize_span(self, span):
        return {
            "name": span.name,
            "context": {
                "trace_id": format(span.context.trace_id, "032x"),
                "span_id": format(span.context.span_id, "016x"),
                "is_remote": span.context.is_remote,
                "trace_flags": format(span.context.trace_flags, "02x"),
                "trace_state": dict(span.context.trace_state) if span.context.trace_state else None,
            },
            "parent_span_id": format(span.parent.span_id, "016x") if span.parent else None,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "attributes": dict(span.attributes),
            "events": [
                {
                    "name": event.name,
                    "timestamp": event.timestamp,
                    "attributes": dict(event.attributes),
                }
                for event in span.events
            ],
            "status": {
                "status_code": span.status.status_code.name,
                "description": span.status.description,
            },
            "kind": span.kind.name,
            "resource": {
                "attributes": dict(span.resource.attributes)
            }
        }

    def _deserialize_span(self, data):
        from opentelemetry.trace import SpanContext, TraceFlags, SpanKind, Status, StatusCode
        from opentelemetry.sdk.trace import ReadableSpan
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace.export import SpanLimits

        span_context = SpanContext(
            trace_id=int(data["context"]["trace_id"], 16),
            span_id=int(data["context"]["span_id"], 16),
            is_remote=data["context"]["is_remote"],
            trace_flags=TraceFlags(int(data["context"]["trace_flags"], 16)),
            trace_state=data["context"]["trace_state"],
        )

        parent = None
        if data["parent_span_id"]:
            parent = SpanContext(
                trace_id=span_context.trace_id,
                span_id=int(data["parent_span_id"], 16),
                is_remote=True, # Assuming parent is remote if not current
            )

        status_code = getattr(StatusCode, data["status"]["status_code"])
        status = Status(status_code, data["status"]["description"])
        kind = getattr(SpanKind, data["kind"])
        resource = Resource.create(data["resource"]["attributes"])

        # Create a dummy tracer provider and tracer for ReadableSpan constructor
        from opentelemetry.sdk.trace import TracerProvider
        provider = TracerProvider(resource=resource)
        tracer = provider.get_tracer("dummy_tracer")

        # Reconstruct ReadableSpan (some fields might be missing or simplified)
        span = ReadableSpan(
            name=data["name"],
            context=span_context,
            parent=parent,
            resource=resource,
            attributes=data["attributes"],
            events=[], # Events are handled separately
            links=[],
            kind=kind,
            status=status,
            start_time=data["start_time"],
            end_time=data["end_time"],
            tracer=tracer,
            span_limits=SpanLimits(), # Default limits
        )
        # Manually add events as ReadableSpan constructor doesn't take them directly
        for event_data in data["events"]:
            span.add_event(event_data["name"], event_data["attributes"], event_data["timestamp"])

        return span

_span_storage = InMemorySpanExporter()
_debug_enabled = False



def enable_span_capture():
    """Enable span capture for debugging."""
    global _debug_enabled
    if not _debug_enabled:
        provider = trace.get_tracer_provider()
        if isinstance(provider, TracerProvider):
            provider.add_span_processor(SimpleSpanProcessor(_span_storage))
            _debug_enabled = True
            console.print("[green]✓[/green] Span capture enabled")


@debug_app.command("spans")
def show_spans(
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, tree, json"),
    filter_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by weaver.type attribute"),
    live: bool = typer.Option(False, "--live", "-l", help="Live update mode"),
):
    """Show captured OpenTelemetry spans."""
    enable_span_capture()
    
    if live:
        # Live mode
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                spans = _span_storage.get_finished_spans()
                display = _format_spans(spans, format, filter_type)
                live.update(display)
                time.sleep(1)
    else:
        # One-time display
        spans = _span_storage.get_finished_spans()
        display = _format_spans(spans, format, filter_type)
        console.print(display)


def _format_spans(spans, format: str, filter_type: Optional[str]):
    """Format spans for display."""
    # Filter spans if needed
    if filter_type:
        spans = [s for s in spans if s.attributes.get("weaver.type") == filter_type]
    
    if format == "table":
        return _format_spans_table(spans)
    elif format == "tree":
        return _format_spans_tree(spans)
    elif format == "json":
        return _format_spans_json(spans)
    else:
        return f"[red]Unknown format: {format}[/red]"


def _format_spans_table(spans) -> Table:
    """Format spans as a table."""
    table = Table(title=f"[bold cyan]Captured Spans ({len(spans)} total)[/bold cyan]")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Duration (ms)", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Attributes", style="blue")
    
    for span in spans[-20:]:  # Show last 20 spans
        # Extract key info
        name = span.name
        span_type = span.attributes.get("weaver.type", "unknown")
        duration = (span.end_time - span.start_time) / 1e6 if span.end_time else 0
        status = "OK" if span.status.status_code.name == "OK" else "ERROR"
        
        # Key attributes
        key_attrs = []
        for k, v in span.attributes.items():
            if k not in ["weaver.type"] and not k.startswith("telemetry."):
                key_attrs.append(f"{k}={v}")
        attrs_str = ", ".join(key_attrs[:3])  # Show first 3 attributes
        
        table.add_row(name, span_type, f"{duration:.2f}", status, attrs_str)
    
    return table


def _format_spans_tree(spans) -> Tree:
    """Format spans as a tree."""
    tree = Tree("[bold cyan]Span Hierarchy[/bold cyan]")
    
    # Group by span type
    by_type = {}
    for span in spans:
        span_type = span.attributes.get("weaver.type", "unknown")
        if span_type not in by_type:
            by_type[span_type] = []
        by_type[span_type].append(span)
    
    for span_type, type_spans in by_type.items():
        type_branch = tree.add(f"[yellow]{span_type}[/yellow] ({len(type_spans)} spans)")
        
        for span in type_spans[-5:]:  # Show last 5 of each type
            duration = (span.end_time - span.start_time) / 1e6 if span.end_time else 0
            span_branch = type_branch.add(f"{span.name} [{duration:.2f}ms]")
            
            # Add key attributes
            for k, v in list(span.attributes.items())[:3]:
                if k != "weaver.type":
                    span_branch.add(f"[dim]{k}: {v}[/dim]")
    
    return tree


def _format_spans_json(spans) -> str:
    """Format spans as JSON."""
    span_data = []
    for span in spans[-10:]:  # Last 10 spans
        span_data.append({
            "name": span.name,
            "type": span.attributes.get("weaver.type", "unknown"),
            "start_time": span.start_time,
            "end_time": span.end_time,
            "duration_ms": (span.end_time - span.start_time) / 1e6 if span.end_time else 0,
            "status": span.status.status_code.name,
            "attributes": dict(span.attributes),
            "events": [
                {
                    "name": event.name,
                    "timestamp": event.timestamp,
                    "attributes": dict(event.attributes)
                }
                for event in span.events
            ]
        })
    
    return json.dumps(span_data, indent=2, default=str)


@debug_app.command("clear")
def clear_spans():
    """Clear captured spans."""
    _span_storage.clear()
    console.print("[green]✓[/green] Cleared all captured spans")


@debug_app.command("stats")
def span_stats():
    """Show span statistics."""
    enable_span_capture()
    spans = _span_storage.get_finished_spans()
    
    if not spans:
        console.print("[yellow]No spans captured yet[/yellow]")
        return
    
    # Calculate statistics
    stats = {
        "total_spans": len(spans),
        "by_type": {},
        "by_status": {"OK": 0, "ERROR": 0},
        "total_duration_ms": 0,
        "avg_duration_ms": 0,
    }
    
    for span in spans:
        # By type
        span_type = span.attributes.get("weaver.type", "unknown")
        stats["by_type"][span_type] = stats["by_type"].get(span_type, 0) + 1
        
        # By status
        if span.status.status_code.name == "OK":
            stats["by_status"]["OK"] += 1
        else:
            stats["by_status"]["ERROR"] += 1
        
        # Duration
        if span.end_time:
            duration = (span.end_time - span.start_time) / 1e6
            stats["total_duration_ms"] += duration
    
    stats["avg_duration_ms"] = stats["total_duration_ms"] / len(spans)
    
    # Display stats
    panel = Panel(
        f"""[bold]Span Statistics[/bold]

Total Spans: [cyan]{stats['total_spans']}[/cyan]
Success Rate: [green]{stats['by_status']['OK'] / stats['total_spans'] * 100:.1f}%[/green]
Total Duration: [yellow]{stats['total_duration_ms']:.2f}ms[/yellow]
Average Duration: [yellow]{stats['avg_duration_ms']:.2f}ms[/yellow]

[bold]By Type:[/bold]
{chr(10).join(f"  • {t}: {c}" for t, c in stats['by_type'].items())}

[bold]By Status:[/bold]
  • OK: [green]{stats['by_status']['OK']}[/green]
  • ERROR: [red]{stats['by_status']['ERROR']}[/red]
""",
        title="[cyan]OpenTelemetry Span Statistics[/cyan]",
        border_style="cyan"
    )
    console.print(panel)


@debug_app.command("trace")
def trace_workflow(
    spec_id: str = typer.Argument(help="Workflow specification ID to trace"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Initial workflow data as JSON"),
):
    """Trace a workflow execution with detailed span capture."""
    enable_span_capture()
    
    console.print(f"[cyan]Tracing workflow '{spec_id}'...[/cyan]")
    console.print("[dim]Note: This will run the workflow and capture all spans[/dim]\n")
    
    # Clear previous spans
    _span_storage.clear()
    
    # Import and run workflow
    from .engine.simple_engine import SimpleBpmnEngine
    from .engine.service_task import WeaverGenServiceEnvironment
    
    script_env = WeaverGenServiceEnvironment()
    engine = SimpleBpmnEngine(script_env)
    
    try:
        # Add the workflow if needed
        console.print("[yellow]Note: Workflow must be added first using 'workflow add'[/yellow]")
        
        # Get initial span count
        initial_count = len(_span_storage.get_finished_spans())
        
        # Run workflow
        instance = engine.start_workflow(spec_id)
        if data:
            instance.workflow.data.update(json.loads(data))
        
        instance.run_until_user_input_required()
        
        # Wait a bit for spans to be exported
        time.sleep(0.5)
        
        # Get new spans
        all_spans = _span_storage.get_finished_spans()
        new_spans = all_spans[initial_count:]
        
        console.print(f"\n[green]✓[/green] Captured {len(new_spans)} spans during execution\n")
        
        # Show span summary
        table = _format_spans_table(new_spans)
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ Error tracing workflow:[/red] {e}")
        raise typer.Exit(1)


@debug_app.command("export")
def export_spans(
    output: str = typer.Argument(help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format: json, csv"),
):
    """Export captured spans to a file."""
    enable_span_capture()
    spans = _span_storage.get_finished_spans()
    
    if not spans:
        console.print("[yellow]No spans to export[/yellow]")
        return
    
    if format == "json":
        data = _format_spans_json(spans)
        with open(output, "w") as f:
            f.write(data)
    elif format == "csv":
        # Simple CSV export
        import csv
        with open(output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "type", "duration_ms", "status", "start_time", "end_time"])
            for span in spans:
                writer.writerow([
                    span.name,
                    span.attributes.get("weaver.type", "unknown"),
                    (span.end_time - span.start_time) / 1e6 if span.end_time else 0,
                    span.status.status_code.name,
                    span.start_time,
                    span.end_time
                ])
    
    console.print(f"[green]✓[/green] Exported {len(spans)} spans to {output}")


if __name__ == "__main__":
    debug_app()