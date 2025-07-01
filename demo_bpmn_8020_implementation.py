#!/usr/bin/env python3
"""
80/20 BPMN-First Implementation Demo

This script demonstrates the core 80/20 BPMN features:
1. BPMN workflow execution with service tasks
2. Span-based observability 
3. CLI integration
4. Service task registry
5. Mermaid report generation

The 20% effort that delivers 80% of the value.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import the 80/20 BPMN components
try:
    from src.weavergen.bpmn_first_engine import (
        BPMNFirstEngine, 
        BPMNExecutionContext,
        run_bpmn_first_generation
    )
    from src.weavergen.bpmn_weaver_forge import WeaverBPMNEngine
except ImportError:
    print("❌ Core BPMN modules not found - make sure you're in the weavergen directory")
    exit(1)

console = Console()


async def demo_core_bpmn_execution():
    """Demo the core BPMN execution engine"""
    console.print("\n[bold cyan]🎯 Demo 1: Core BPMN Execution Engine[/bold cyan]")
    
    # Create engine
    engine = BPMNFirstEngine()
    
    # Create context with semantic file
    context = BPMNExecutionContext()
    context.set("semantic_file", "semantic_conventions/weavergen_system.yaml")
    context.set("output_dir", "demo_bpmn_output")
    
    # Execute workflow
    console.print("[cyan]⚡ Executing WeaverGenOrchestration workflow...[/cyan]")
    
    try:
        result = await engine.execute_workflow("WeaverGenOrchestration", context)
        
        # Show results
        spans_generated = len(result.spans)
        console.print(f"[green]✅ Workflow completed successfully[/green]")
        console.print(f"[cyan]📊 Spans generated: {spans_generated}[/cyan]")
        console.print(f"[cyan]📦 Context variables: {len(result.variables)}[/cyan]")
        
        # Show execution report
        report = engine.generate_execution_report(result)
        console.print("\n[bold yellow]📋 Execution Report:[/bold yellow]")
        console.print(report)
        
        return result
        
    except Exception as e:
        console.print(f"[red]❌ Workflow failed: {e}[/red]")
        return None


async def demo_weaver_bpmn_integration():
    """Demo the Weaver Forge BPMN integration"""
    console.print("\n[bold cyan]🔨 Demo 2: Weaver Forge BPMN Integration[/bold cyan]")
    
    # Create Weaver BPMN engine
    engine = WeaverBPMNEngine()
    
    # Create context
    context = {
        "registry_url": "semantic_conventions/weavergen_system.yaml",
        "language": "python",
        "output_dir": "demo_weaver_output"
    }
    
    console.print("[cyan]⚡ Executing WeaverForgeOrchestration workflow...[/cyan]")
    
    try:
        result = await engine.execute_weaver_workflow("WeaverForgeOrchestration", context)
        
        # Show results
        console.print(f"[green]✅ Weaver workflow completed[/green]")
        console.print(f"[cyan]📊 Validation score: {result.get('validation_score', 0):.2%}[/cyan]")
        console.print(f"[cyan]📊 Generated components: {len([k for k in result.keys() if 'generated' in k])}[/cyan]")
        
        return result
        
    except Exception as e:
        console.print(f"[red]❌ Weaver workflow failed: {e}[/red]")
        return None


def demo_span_collection(bpmn_result):
    """Demo span collection and analysis"""
    console.print("\n[bold cyan]📊 Demo 3: Span Collection & Analysis[/bold cyan]")
    
    if not bpmn_result or not bpmn_result.spans:
        console.print("[red]❌ No spans to analyze[/red]")
        return
    
    # Create spans table
    table = Table(title="Captured BPMN Spans", show_header=True)
    table.add_column("Span Name", style="cyan")
    table.add_column("Timestamp", style="green")
    table.add_column("Task Type", style="yellow")
    table.add_column("Success", style="magenta")
    
    for span in bpmn_result.spans:
        name = span.get("name", "unknown")
        timestamp = span.get("timestamp", "unknown")
        task_type = span.get("attributes", {}).get("bpmn.task.type", "unknown")
        success = "✅" if "error" not in span else "❌"
        
        table.add_row(name, timestamp, task_type, success)
    
    console.print(table)
    
    # Save spans to file
    spans_file = Path("demo_captured_spans.json")
    with open(spans_file, 'w') as f:
        json.dump(bpmn_result.spans, f, indent=2)
    
    console.print(f"[cyan]💾 Spans saved to: {spans_file}[/cyan]")


def demo_mermaid_generation(bpmn_result):
    """Demo Mermaid diagram generation"""
    console.print("\n[bold cyan]🎨 Demo 4: Mermaid Diagram Generation[/bold cyan]")
    
    if not bpmn_result:
        console.print("[red]❌ No BPMN result to generate diagram[/red]")
        return
    
    # Create engine to generate Mermaid
    engine = BPMNFirstEngine()
    mermaid = engine.generate_mermaid_trace(bpmn_result)
    
    console.print("[cyan]📊 Generated Mermaid Sequence Diagram:[/cyan]")
    console.print(Panel(mermaid, title="BPMN Execution Trace", border_style="blue"))
    
    # Save Mermaid to file
    mermaid_file = Path("demo_bpmn_trace.mmd")
    with open(mermaid_file, 'w') as f:
        f.write(mermaid)
    
    console.print(f"[cyan]💾 Mermaid saved to: {mermaid_file}[/cyan]")


async def demo_full_pipeline():
    """Demo the complete 80/20 BPMN pipeline"""
    console.print("\n[bold cyan]🚀 Demo 5: Full BPMN Pipeline[/bold cyan]")
    
    semantic_file = Path("semantic_conventions/weavergen_system.yaml")
    output_dir = Path("demo_full_pipeline")
    
    # Create semantic file if it doesn't exist
    if not semantic_file.exists():
        semantic_file.parent.mkdir(parents=True, exist_ok=True)
        minimal_semantics = {
            "file_format": "1.1.0",
            "schema_url": "https://opentelemetry.io/schemas/1.21.0",
            "groups": [
                {
                    "id": "weavergen.system",
                    "prefix": "weavergen",
                    "type": "attribute_group",
                    "brief": "WeaverGen system attributes",
                    "attributes": [
                        {
                            "id": "system.name",
                            "type": "string",
                            "brief": "System name"
                        }
                    ]
                }
            ]
        }
        
        with open(semantic_file, 'w') as f:
            import yaml
            yaml.dump(minimal_semantics, f)
        
        console.print(f"[cyan]📄 Created minimal semantic file: {semantic_file}[/cyan]")
    
    console.print("[cyan]⚡ Running full BPMN-first generation pipeline...[/cyan]")
    
    try:
        result = await run_bpmn_first_generation(semantic_file, output_dir)
        
        if result.get("success"):
            console.print(f"[green]✅ Full pipeline completed successfully[/green]")
            console.print(f"[cyan]📊 Spans generated: {result.get('spans_generated', 0)}[/cyan]")
            console.print(f"[cyan]📁 Output directory: {output_dir}[/cyan]")
            
            # Show Mermaid if available
            if "mermaid" in result:
                console.print("\n[cyan]📊 Pipeline Mermaid Diagram:[/cyan]")
                console.print(Panel(result["mermaid"], title="Pipeline Execution", border_style="green"))
        else:
            console.print("[red]❌ Full pipeline failed[/red]")
            
        return result
        
    except Exception as e:
        console.print(f"[red]❌ Full pipeline error: {e}[/red]")
        return None


def demo_service_task_registry():
    """Demo the service task registry"""
    console.print("\n[bold cyan]🔧 Demo 6: Service Task Registry[/bold cyan]")
    
    # Show BPMN engine service tasks
    engine = BPMNFirstEngine()
    
    table = Table(title="BPMN Service Task Registry", show_header=True)
    table.add_column("Task Name", style="cyan")
    table.add_column("Task Class", style="green")
    table.add_column("Category", style="yellow")
    
    for task_name, task_class in engine.service_tasks.items():
        category = "Semantic" if "Semantic" in task_name else \
                  "Agent" if "Agent" in task_name else \
                  "Validation" if "Validation" in task_name else \
                  "Generation" if "Generation" in task_name else "Core"
        
        table.add_row(task_name, task_class.__name__, category)
    
    console.print(table)
    console.print(f"[cyan]📊 Total service tasks: {len(engine.service_tasks)}[/cyan]")
    
    # Show Weaver BPMN engine tasks
    weaver_engine = WeaverBPMNEngine()
    
    table2 = Table(title="Weaver BPMN Service Task Registry", show_header=True)
    table2.add_column("Task Name", style="cyan")
    table2.add_column("Task Class", style="green")
    table2.add_column("Purpose", style="yellow")
    
    for task_name, task_class in weaver_engine.service_tasks.items():
        purpose = "Initialize" if "Initialize" in task_name else \
                 "Load" if "Load" in task_name else \
                 "Validate" if "Validate" in task_name else \
                 "Generate" if "Generate" in task_name else \
                 "Report" if "Report" in task_name else "Process"
        
        table2.add_row(task_name, task_class.__name__, purpose)
    
    console.print(table2)
    console.print(f"[cyan]📊 Total Weaver tasks: {len(weaver_engine.service_tasks)}[/cyan]")


async def main():
    """Run all 80/20 BPMN demonstrations"""
    console.print(Panel.fit(
        "🎯 [bold cyan]80/20 BPMN-First Implementation Demo[/bold cyan]\n\n"
        "Demonstrating the 20% of BPMN features that deliver 80% of the value:\n"
        "• BPMN workflow execution with service tasks\n"
        "• Span-based observability\n"
        "• CLI integration\n"
        "• Service task registry\n"
        "• Mermaid report generation",
        title="WeaverGen BPMN Demo",
        border_style="bold green"
    ))
    
    # Run all demos
    demos = [
        ("Core BPMN Execution", demo_core_bpmn_execution()),
        ("Weaver BPMN Integration", demo_weaver_bpmn_integration()),
        ("Full Pipeline", demo_full_pipeline()),
    ]
    
    results = {}
    
    for demo_name, demo_coro in demos:
        console.print(f"\n[bold blue]🔄 Running {demo_name}...[/bold blue]")
        try:
            result = await demo_coro
            results[demo_name] = result
        except Exception as e:
            console.print(f"[red]❌ {demo_name} failed: {e}[/red]")
            results[demo_name] = None
    
    # Run sync demos
    console.print(f"\n[bold blue]🔄 Running Span Collection Demo...[/bold blue]")
    demo_span_collection(results.get("Core BPMN Execution"))
    
    console.print(f"\n[bold blue]🔄 Running Mermaid Generation Demo...[/bold blue]")
    demo_mermaid_generation(results.get("Core BPMN Execution"))
    
    console.print(f"\n[bold blue]🔄 Running Service Task Registry Demo...[/bold blue]")
    demo_service_task_registry()
    
    # Final summary
    console.print("\n" + "="*60)
    console.print("[bold green]🎉 80/20 BPMN Implementation Demo Complete![/bold green]")
    
    success_count = sum(1 for r in results.values() if r is not None)
    console.print(f"[cyan]📊 Successful demos: {success_count}/{len(results)}[/cyan]")
    
    if success_count >= len(results) * 0.8:
        console.print("[bold green]✅ 80/20 BPMN system is operational![/bold green]")
    else:
        console.print("[yellow]⚠️ Some demos failed - check implementation[/yellow]")
    
    console.print("\n[bold cyan]🎯 Key Achievements:[/bold cyan]")
    console.print("• BPMN workflows execute Python service tasks")
    console.print("• Every task generates OpenTelemetry spans")
    console.print("• Visual Mermaid traces of execution")
    console.print("• CLI commands for workflow execution")
    console.print("• Service task registry for extensibility")
    
    console.print("\n[bold yellow]CLI Commands to Try:[/bold yellow]")
    console.print("• uv run src/weavergen/cli.py bpmn list")
    console.print("• uv run src/weavergen/cli.py bpmn execute WeaverGenOrchestration")
    console.print("• uv run src/weavergen/cli.py bpmn orchestrate")
    console.print("• uv run src/weavergen/cli.py bpmn weaver")


if __name__ == "__main__":
    asyncio.run(main())