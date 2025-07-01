"""Demo: BPMN-driven Weaver Forge with comprehensive span validation"""

import asyncio
import json
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
import time

console = Console()

# Import our modules
from src.weavergen.span_validator import SpanValidator, SpanReportGenerator


def load_and_analyze_spans():
    """Load and analyze the test spans"""
    # Load spans
    span_file = Path("bpmn_validation/test_spans.json")
    with open(span_file) as f:
        spans = json.load(f)
    
    # Validate
    validator = SpanValidator()
    result = validator.validate_spans(spans)
    reporter = SpanReportGenerator()
    
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=8)
    )
    
    # Header
    header = Panel(
        "[bold cyan]BPMN-Driven Weaver Forge Span Analysis[/bold cyan]\n"
        "[yellow]Complete observability for code generation workflows[/yellow]",
        style="cyan"
    )
    layout["header"].update(header)
    
    # Main content - split into left and right
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    # Left side - Validation Report
    validation_table = reporter.generate_table_report(result)
    layout["left"].update(Panel(validation_table, title="Validation Results", border_style="green"))
    
    # Right side - Span Statistics
    stats_table = Table(title="Span Statistics", show_header=True)
    stats_table.add_column("Category", style="cyan")
    stats_table.add_column("Count", style="yellow")
    stats_table.add_column("Avg Duration", style="green")
    
    # Calculate statistics by category
    categories = {}
    for span in spans:
        name_parts = span["name"].split(".")
        category = name_parts[0] if name_parts else "unknown"
        
        if category not in categories:
            categories[category] = {"count": 0, "total_duration": 0}
        
        categories[category]["count"] += 1
        categories[category]["total_duration"] += span.get("duration_ns", 0) / 1_000_000
    
    for cat, stats in categories.items():
        avg_duration = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
        stats_table.add_row(cat, str(stats["count"]), f"{avg_duration:.1f}ms")
    
    layout["right"].update(Panel(stats_table, title="Performance Metrics", border_style="blue"))
    
    # Footer - Mermaid diagram
    mermaid = reporter.generate_mermaid_trace(spans[:8])  # First 8 spans
    mermaid_panel = Panel(
        mermaid,
        title="Execution Flow (Mermaid)",
        border_style="magenta"
    )
    layout["footer"].update(mermaid_panel)
    
    return layout, result


def create_improvement_suggestions(result):
    """Create improvement suggestions based on validation results"""
    suggestions = []
    
    if result.semantic_compliance < 0.8:
        suggestions.append({
            "issue": "Low Semantic Compliance",
            "current": f"{result.semantic_compliance:.1%}",
            "target": "80%+",
            "fix": "Add required BPMN task attributes (bpmn.task.type, bpmn.task.class)"
        })
    
    if result.coverage_score < 1.0:
        missing = []
        if result.coverage_score < 0.2:
            missing.append("weaver")
        suggestions.append({
            "issue": "Incomplete Coverage",
            "current": f"{result.coverage_score:.1%}",
            "target": "100%",
            "fix": f"Ensure all components generate spans: {', '.join(missing)}"
        })
    
    if not result.hierarchy_valid:
        suggestions.append({
            "issue": "Invalid Hierarchy",
            "current": "Broken parent-child links",
            "target": "Valid hierarchy",
            "fix": "Ensure all child spans reference valid parent IDs"
        })
    
    return suggestions


async def main():
    """Run the comprehensive span validation demo"""
    console.clear()
    
    # Show intro
    intro = Panel(
        "[bold green]🚀 BPMN-Driven Weaver Forge Span Validation Demo[/bold green]\n\n"
        "This demo shows how OpenTelemetry spans provide complete observability\n"
        "for BPMN-orchestrated code generation workflows.\n\n"
        "[cyan]Key Features:[/cyan]\n"
        "• Visual workflow execution traces\n"
        "• Semantic convention compliance checking\n"
        "• Performance analysis across all operations\n"
        "• Health scoring and recommendations",
        style="green"
    )
    console.print(intro)
    console.print()
    
    # Load and analyze
    layout, result = load_and_analyze_spans()
    
    # Show analysis
    with Live(layout, refresh_per_second=4, screen=False) as live:
        time.sleep(2)
    
    # Show improvements
    console.print("\n[bold yellow]📋 Improvement Suggestions:[/bold yellow]")
    suggestions = create_improvement_suggestions(result)
    
    for i, suggestion in enumerate(suggestions, 1):
        console.print(f"\n[cyan]{i}. {suggestion['issue']}[/cyan]")
        console.print(f"   Current: [red]{suggestion['current']}[/red]")
        console.print(f"   Target:  [green]{suggestion['target']}[/green]")
        console.print(f"   Fix:     {suggestion['fix']}")
    
    # Show span examples
    console.print("\n[bold magenta]📊 Example Span Structure:[/bold magenta]")
    
    example_span = {
        "name": "bpmn.execute.WeaverForgeOrchestration",
        "attributes": {
            "bpmn.task.type": "orchestration",
            "bpmn.task.class": "WeaverForgeOrchestrationTask",
            "bpmn.workflow.name": "WeaverForgeOrchestration",
            "bpmn.workflow.type": "weaver_forge",
            "weaver.registry": "semantic_conventions/weavergen_system.yaml",
            "generation.language": "python"
        },
        "children": [
            "weaver.initialize",
            "weaver.load_registry",
            "weaver.validate_registry",
            "bpmn.execute.PythonForgeGeneration"
        ]
    }
    
    console.print(json.dumps(example_span, indent=2))
    
    # Summary
    summary = Panel(
        f"[bold]Validation Summary:[/bold]\n\n"
        f"• Total Spans: {result.total_spans}\n"
        f"• Valid Spans: {result.valid_spans}\n"
        f"• Health Score: [{'green' if result.health_score >= 0.8 else 'yellow'}]{result.health_score:.1%}[/]\n"
        f"• Status: {'✅ PASSED' if result.health_score >= 0.8 else '⚠️ NEEDS IMPROVEMENT'}\n\n"
        "[dim]The BPMN-driven approach provides complete visibility into every\n"
        "step of the code generation process through OpenTelemetry spans.[/dim]",
        title="Results",
        border_style="cyan"
    )
    console.print(summary)


if __name__ == "__main__":
    asyncio.run(main())