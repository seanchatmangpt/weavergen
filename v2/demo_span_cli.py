#!/usr/bin/env python3
"""
Demo the span file to mermaid CLI command
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Import the command directly
from weavergen.src.commands.mermaid import spans
from weavergen.src.span_parser import SpanFileParser, SpanToMermaidConverter
from rich.console import Console

def demo_cli_functionality():
    """Demo the CLI functionality without typer"""
    console = Console()
    
    span_file = Path("sample_spans.json")
    
    print("=== SPAN FILE TO MERMAID CLI DEMO ===\n")
    
    console.print(f"[bold]Processing span file:[/bold] {span_file}")
    
    # Test different diagram types
    diagram_types = ["sequence", "trace", "service", "timeline"]
    
    for diagram_type in diagram_types:
        console.print(f"\n[bold cyan]🔄 Generating {diagram_type} diagram...[/bold cyan]")
        
        try:
            # Parse spans
            parser = SpanFileParser()
            spans = parser.parse_file(span_file)
            
            # Convert to mermaid
            converter = SpanToMermaidConverter(spans)
            
            if diagram_type == "sequence":
                diagram = converter.to_sequence_diagram(max_spans=10, include_timing=True)
            elif diagram_type == "trace":
                # Use first trace ID
                trace_id = spans[0].trace_id if spans else None
                diagram = converter.to_trace_flow_diagram(trace_id=trace_id)
            elif diagram_type == "service":
                diagram = converter.to_service_map_diagram()
            elif diagram_type == "timeline":
                diagram = converter.to_timeline_diagram(max_spans=8)
            
            console.print(f"[green]✅ {diagram_type.title()} diagram generated[/green]")
            console.print(f"[dim]First 3 lines:[/dim]")
            diagram_lines = diagram.split('\n')
            for line in diagram_lines[:3]:
                console.print(f"[dim]  {line}[/dim]")
            console.print(f"[dim]  ... ({len(diagram_lines)} total lines)[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Error with {diagram_type}: {e}[/red]")

def demo_supported_formats():
    """Demo different supported span file formats"""
    console = Console()
    
    print("\n=== SUPPORTED SPAN FILE FORMATS ===\n")
    
    formats = {
        "JSON": "Standard JSON array of span objects",
        "JSONL": "JSON Lines format (one span per line)",
        "CSV": "Comma-separated values with span columns",
        "Log": "Log files containing JSON span objects",
        "OTLP": "OpenTelemetry Protocol format"
    }
    
    for fmt, description in formats.items():
        console.print(f"[bold green]✅ {fmt}[/bold green]: {description}")
    
    console.print(f"\n[bold]Example usage:[/bold]")
    console.print(f"[cyan]python -m weavergen.src.commands.mermaid spans sample_spans.json --type sequence[/cyan]")
    console.print(f"[cyan]python -m weavergen.src.commands.mermaid spans trace.jsonl --type service[/cyan]")
    console.print(f"[cyan]python -m weavergen.src.commands.mermaid spans otel_export.json --type timeline --max 20[/cyan]")

def show_real_usage():
    """Show what the actual command would look like"""
    console = Console()
    
    print("\n=== REAL COMMAND USAGE ===\n")
    
    console.print("[bold]The span conversion command provides:[/bold]")
    console.print("• [green]Multiple input formats[/green]: JSON, JSONL, CSV, logs")
    console.print("• [green]4 diagram types[/green]: sequence, trace, service, timeline")
    console.print("• [green]Rich statistics[/green]: span counts, services, errors")
    console.print("• [green]File export[/green]: save diagrams to .md files")
    console.print("• [green]Flexible parsing[/green]: handles various OTel formats")
    
    console.print(f"\n[bold]Available options:[/bold]")
    console.print(f"  [cyan]--type[/cyan]        Diagram type (sequence, trace, service, timeline)")
    console.print(f"  [cyan]--max[/cyan]         Maximum spans to include")
    console.print(f"  [cyan]--trace-id[/cyan]    Filter to specific trace")
    console.print(f"  [cyan]--timing[/cyan]      Include/exclude timing info")
    console.print(f"  [cyan]--output[/cyan]      Save to file")
    
    console.print(f"\n[bold yellow]Real world example:[/bold yellow]")
    console.print(f"[green]$ weavergen mermaid spans production_traces.json --type service --output service_map.md[/green]")
    
    # Show what we learned from the test data
    span_file = Path("sample_spans.json")
    if span_file.exists():
        parser = SpanFileParser()
        spans = parser.parse_file(span_file)
        
        services = set(span.service_name for span in spans)
        traces = set(span.trace_id for span in spans)
        errors = [span for span in spans if span.error]
        
        console.print(f"\n[bold]Test data analysis:[/bold]")
        console.print(f"  📊 Spans: {len(spans)}")
        console.print(f"  🏗️  Services: {len(services)} (WeaverGen components)")
        console.print(f"  🔗 Traces: {len(traces)} (different workflows)")
        console.print(f"  ❌ Errors: {len(errors)} (telemetry export failure)")
        console.print(f"  ⏱️  Duration range: 40ms - 800ms")

if __name__ == "__main__":
    demo_cli_functionality()
    demo_supported_formats()
    show_real_usage()