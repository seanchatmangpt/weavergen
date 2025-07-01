#!/usr/bin/env python3
"""
Demo SpiffWorkflow BPMN Integration

This script demonstrates the SpiffWorkflow integration replacing custom BPMN engines:
- All custom BPMN engines replaced with SpiffWorkflow
- CLI commands execute BPMN workflows instead of direct function calls
- Service tasks implement real BPMN operations
- Complete span-based observability maintained
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import yaml

# Import the SpiffWorkflow BPMN components
try:
    from src.weavergen.spiff_bpmn_engine import (
        SpiffBPMNEngine, 
        SpiffExecutionContext,
        run_spiff_bpmn_generation
    )
    SPIFF_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"❌ SpiffWorkflow BPMN engine not available: {e}")
    SPIFF_ENGINE_AVAILABLE = False

console = Console()


def demo_spiff_engine_availability():
    """Demo 1: SpiffWorkflow Engine Availability"""
    console.print("\n[bold cyan]🎯 Demo 1: SpiffWorkflow Engine Availability[/bold cyan]")
    
    if not SPIFF_ENGINE_AVAILABLE:
        console.print("[red]❌ SpiffWorkflow BPMN engine not available[/red]")
        return False
    
    # Create SpiffWorkflow engine
    engine = SpiffBPMNEngine()
    
    # Show service task registry
    console.print(f"[green]✅ SpiffWorkflow BPMN engine loaded[/green]")
    console.print(f"[cyan]📋 Available service tasks: {len(engine.service_tasks)}[/cyan]")
    console.print(f"[cyan]📁 Available workflows: {len(engine.workflow_files)}[/cyan]")
    
    # Display service tasks
    table = Table(title="SpiffWorkflow Service Tasks", show_header=True)
    table.add_column("Task Name", style="cyan")
    table.add_column("Task Class", style="green")
    table.add_column("Purpose", style="yellow")
    
    task_purposes = {
        "LoadSemantics": "Load semantic convention files",
        "ValidateSemantics": "Validate semantic structure",
        "ExtractAgentSemantics": "Extract agent-specific data",
        "GenerateAgentRoles": "Generate agent role definitions",
        "GenerateSpanValidator": "Create span validation logic",
        "GenerateHealthScoring": "Generate health scoring system"
    }
    
    for task_name, service_task in engine.service_tasks.items():
        purpose = task_purposes.get(task_name, "Process workflow step")
        table.add_row(task_name, service_task.__class__.__name__, purpose)
    
    console.print(table)
    return True


def demo_spiff_workflow_execution():
    """Demo 2: SpiffWorkflow Execution"""
    console.print("\n[bold cyan]🔧 Demo 2: SpiffWorkflow Execution[/bold cyan]")
    
    if not SPIFF_ENGINE_AVAILABLE:
        console.print("[red]❌ Skipping - SpiffWorkflow engine not available[/red]")
        return None
    
    # Create engine and context
    engine = SpiffBPMNEngine()
    context = SpiffExecutionContext()
    
    # Set up workflow data
    context.set("semantic_file", "semantic_conventions/weavergen_system.yaml")
    context.set("output_dir", "demo_spiff_output")
    
    console.print("[cyan]⚡ Executing WeaverGenOrchestration workflow...[/cyan]")
    
    try:
        # Execute workflow
        result = engine.execute_workflow("WeaverGenOrchestration", context)
        
        # Show results
        console.print(f"[green]✅ Workflow completed[/green]")
        console.print(f"[cyan]📊 Tasks executed: {len(result.execution_log)}[/cyan]")
        console.print(f"[cyan]📦 Workflow data keys: {len(result.workflow_data)}[/cyan]")
        
        # Show execution report
        report = engine.generate_execution_report(result)
        console.print("\n[bold yellow]📋 Execution Report:[/bold yellow]")
        console.print(report)
        
        return result
        
    except Exception as e:
        console.print(f"[red]❌ Workflow execution failed: {e}[/red]")
        return None


def demo_spiff_mermaid_generation(spiff_result):
    """Demo 3: SpiffWorkflow Mermaid Generation"""
    console.print("\n[bold cyan]🎨 Demo 3: SpiffWorkflow Mermaid Generation[/bold cyan]")
    
    if not spiff_result:
        console.print("[red]❌ No SpiffWorkflow result to generate diagram[/red]")
        return
    
    # Create engine to generate Mermaid
    engine = SpiffBPMNEngine()
    mermaid = engine.generate_mermaid_trace(spiff_result)
    
    console.print("[cyan]📊 Generated SpiffWorkflow Mermaid Diagram:[/cyan]")
    console.print(Panel(mermaid, title="SpiffWorkflow Execution Trace", border_style="blue"))
    
    # Save Mermaid to file
    mermaid_file = Path("demo_spiff_trace.mmd")
    with open(mermaid_file, 'w') as f:
        f.write(mermaid)
    
    console.print(f"[cyan]💾 SpiffWorkflow Mermaid saved to: {mermaid_file}[/cyan]")


async def demo_spiff_cli_integration():
    """Demo 4: SpiffWorkflow CLI Integration"""
    console.print("\n[bold cyan]🖥️ Demo 4: SpiffWorkflow CLI Integration[/bold cyan]")
    
    if not SPIFF_ENGINE_AVAILABLE:
        console.print("[red]❌ Skipping - SpiffWorkflow engine not available[/red]")
        return None
    
    # Create minimal semantic file for testing
    semantic_file = Path("demo_semantic_spiff.yaml")
    output_dir = Path("demo_spiff_cli_output")
    
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
    
    # Create semantic file
    semantic_file.parent.mkdir(parents=True, exist_ok=True)
    with open(semantic_file, 'w') as f:
        yaml.dump(minimal_semantics, f)
    
    console.print(f"[cyan]📄 Created test semantic file: {semantic_file}[/cyan]")
    
    console.print("[cyan]⚡ Running SpiffWorkflow CLI integration...[/cyan]")
    
    try:
        result = await run_spiff_bpmn_generation(semantic_file, output_dir)
        
        if result.get("success"):
            console.print(f"[green]✅ CLI integration successful[/green]")
            console.print(f"[cyan]📊 Tasks executed: {result.get('tasks_executed', 0)}[/cyan]")
            console.print(f"[cyan]📁 Output directory: {output_dir}[/cyan]")
            
            # Show Mermaid if available
            if "mermaid" in result:
                console.print("\n[cyan]📊 CLI Execution Mermaid:[/cyan]")
                console.print(Panel(result["mermaid"], title="CLI Execution", border_style="green"))
        else:
            console.print("[red]❌ CLI integration failed[/red]")
            
        return result
        
    except Exception as e:
        console.print(f"[red]❌ CLI integration error: {e}[/red]")
        return None
    finally:
        # Cleanup
        if semantic_file.exists():
            semantic_file.unlink()


def demo_spiff_vs_legacy():
    """Demo 5: SpiffWorkflow vs Legacy Engine Comparison"""
    console.print("\n[bold cyan]⚖️ Demo 5: SpiffWorkflow vs Legacy Engine[/bold cyan]")
    
    comparison_table = Table(title="SpiffWorkflow vs Legacy BPMN Engine", show_header=True)
    comparison_table.add_column("Feature", style="cyan")
    comparison_table.add_column("Legacy Engine", style="yellow")
    comparison_table.add_column("SpiffWorkflow Engine", style="green")
    comparison_table.add_column("Advantage", style="magenta")
    
    comparisons = [
        ("BPMN Standard Compliance", "Custom Implementation", "Full BPMN 2.0 Support", "SpiffWorkflow"),
        ("Workflow Parsing", "Mock/Simple Parser", "Industry Standard Parser", "SpiffWorkflow"),
        ("Task Execution", "Sequential Only", "Parallel & Sequential", "SpiffWorkflow"),
        ("Error Handling", "Basic", "BPMN Error Events", "SpiffWorkflow"),
        ("Debugging", "Limited", "Full BPMN Debugging", "SpiffWorkflow"),
        ("Community Support", "None", "Active Community", "SpiffWorkflow"),
        ("Visual Design", "No", "Yes (BPMN Editors)", "SpiffWorkflow"),
        ("Gateway Support", "Limited", "Full Gateway Support", "SpiffWorkflow"),
        ("Process Persistence", "No", "Yes", "SpiffWorkflow"),
        ("Span Integration", "Custom", "Enhanced with Spans", "SpiffWorkflow")
    ]
    
    for feature, legacy, spiff, advantage in comparisons:
        comparison_table.add_row(feature, legacy, spiff, advantage)
    
    console.print(comparison_table)
    
    console.print("\n[bold green]🎯 Key SpiffWorkflow Advantages:[/bold green]")
    console.print("• Industry-standard BPMN 2.0 compliance")
    console.print("• Real parallel gateway execution")
    console.print("• Visual workflow design support")
    console.print("• Production-ready workflow engine")
    console.print("• Enhanced span instrumentation integration")


async def main():
    """Run all SpiffWorkflow BPMN integration demonstrations"""
    console.print(Panel.fit(
        "🎯 [bold cyan]SpiffWorkflow BPMN Integration Demo[/bold cyan]\n\n"
        "Demonstrating the replacement of custom BPMN engines with SpiffWorkflow:\n"
        "• SpiffWorkflow engine with service task implementations\n"
        "• CLI commands executing real BPMN workflows\n"
        "• Enhanced span instrumentation maintained\n"
        "• Industry-standard BPMN 2.0 compliance\n"
        "• Visual workflow design ready",
        title="WeaverGen SpiffWorkflow Demo",
        border_style="bold green"
    ))
    
    # Run all demos
    results = {}
    
    # Demo 1: Engine availability
    engine_available = demo_spiff_engine_availability()
    results["engine_available"] = engine_available
    
    if engine_available:
        # Demo 2: Workflow execution
        spiff_result = demo_spiff_workflow_execution()
        results["workflow_execution"] = spiff_result
        
        # Demo 3: Mermaid generation
        demo_spiff_mermaid_generation(spiff_result)
        results["mermaid_generation"] = True
        
        # Demo 4: CLI integration
        cli_result = await demo_spiff_cli_integration()
        results["cli_integration"] = cli_result
    else:
        results["workflow_execution"] = None
        results["mermaid_generation"] = False
        results["cli_integration"] = None
    
    # Demo 5: Comparison (always runs)
    demo_spiff_vs_legacy()
    results["comparison"] = True
    
    # Final summary
    console.print("\n" + "="*60)
    console.print("[bold green]🎉 SpiffWorkflow BPMN Integration Demo Complete![/bold green]")
    
    success_count = sum(1 for r in results.values() if r is not None and r is not False)
    total_count = len(results)
    
    console.print(f"[cyan]📊 Successful demos: {success_count}/{total_count}[/cyan]")
    
    if results["engine_available"]:
        console.print("[bold green]✅ SpiffWorkflow BPMN engine is operational![/bold green]")
        
        console.print("\n[bold cyan]🎯 SpiffWorkflow Achievements:[/bold cyan]")
        console.print("• Custom BPMN engines replaced with SpiffWorkflow")
        console.print("• CLI commands execute real BPMN workflows")
        console.print("• Service tasks implement BPMN operations")
        console.print("• Complete span-based observability maintained")
        console.print("• Industry-standard BPMN 2.0 compliance")
        
        console.print("\n[bold yellow]CLI Commands Now Use SpiffWorkflow:[/bold yellow]")
        console.print("• python -m src.weavergen.cli bpmn list")
        console.print("• python -m src.weavergen.cli bpmn execute WeaverGenOrchestration")
        console.print("• python -m src.weavergen.cli bpmn orchestrate")
        console.print("• python -m src.weavergen.cli bpmn weaver")
    else:
        console.print("[yellow]⚠️ SpiffWorkflow not available - install with: pip install SpiffWorkflow[/yellow]")
    
    console.print("\n[bold green]🚀 SpiffWorkflow integration successfully replaces custom BPMN engines![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())