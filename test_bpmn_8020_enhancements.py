#!/usr/bin/env python3
"""
Test the BPMN 80/20 Enhancements

Demonstrates:
1. Live workflow monitoring in the terminal
2. Error boundaries with automatic retry
3. Compensation flows on failure
4. Enhanced observability
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weavergen.bpmn_8020_enhanced import run_enhanced_pydantic_ai_workflow
from weavergen.bpmn_live_monitor import BPMNLiveMonitor, monitor_bpmn_workflow
from rich.console import Console


async def demo_live_monitoring():
    """Demonstrate live BPMN monitoring"""
    
    console = Console()
    console.print("\n[bold cyan]🔍 Demo 1: Live Workflow Monitoring[/bold cyan]")
    console.print("Watch the workflow execute in real-time...\n")
    
    # Run with live monitoring enabled
    result = await run_enhanced_pydantic_ai_workflow(
        semantic_file="semantic_conventions/test_valid.yaml",
        output_dir="demo_8020_output",
        enable_monitoring=True,
        use_mock=True
    )
    
    console.print(f"\n📊 Results:")
    console.print(f"  - Success: {result['success']}")
    console.print(f"  - Agents Generated: {result['agents_generated']}")
    console.print(f"  - Quality Score: {result['quality_score']:.1%}")
    
    return result


async def demo_error_recovery():
    """Demonstrate error boundaries and recovery"""
    
    console = Console()
    console.print("\n[bold cyan]🛡️ Demo 2: Error Recovery & Retry[/bold cyan]")
    console.print("Simulating failures and automatic recovery...\n")
    
    # Create a workflow that will encounter errors
    from weavergen.bpmn_error_boundaries import BPMNErrorBoundary, ErrorSeverity
    
    boundary = BPMNErrorBoundary()
    
    # Simulate task with transient failure
    retry_count = 0
    
    async def flaky_task(context):
        nonlocal retry_count
        retry_count += 1
        if retry_count < 3:
            raise ConnectionError(f"Network timeout (attempt {retry_count})")
        return {"success": True, "attempts": retry_count}
    
    # Execute with boundary
    result = await boundary.execute_with_boundary(
        task_name="FlakeyNetworkTask",
        task_func=flaky_task,
        context={}
    )
    
    console.print(f"✅ Task succeeded after {result.get('attempts', 0)} attempts")
    
    return result


async def demo_compensation_flow():
    """Demonstrate compensation when workflow fails"""
    
    console = Console()
    console.print("\n[bold cyan]↩️  Demo 3: Compensation Flow[/bold cyan]")
    console.print("Showing automatic rollback on failure...\n")
    
    from weavergen.bpmn_error_boundaries import BPMNCompensationFlow
    
    compensation = BPMNCompensationFlow()
    
    # Register compensation handlers
    async def compensate_step1(ctx, error):
        console.print("  [yellow]↩️  Rolling back Step 1[/yellow]")
        return {"rolled_back": "step1"}
    
    async def compensate_step2(ctx, error):
        console.print("  [yellow]↩️  Rolling back Step 2[/yellow]")
        return {"rolled_back": "step2"}
    
    compensation.register("step1", compensate_step1)
    compensation.register("step2", compensate_step2)
    
    # Mark tasks as completed
    compensation.mark_completed("step1")
    compensation.mark_completed("step2")
    
    # Trigger compensation
    console.print("[red]❌ Workflow failed at Step 3[/red]")
    results = await compensation.compensate_all({}, None)
    
    console.print(f"\n✅ Compensation complete: {len(results)} tasks rolled back")
    
    return results


async def demo_simple_monitoring():
    """Demonstrate simple workflow visualization"""
    
    console = Console()
    console.print("\n[bold cyan]📊 Demo 4: Simple Workflow Visualization[/bold cyan]")
    console.print("Minimal monitoring with maximum clarity...\n")
    
    monitor = BPMNLiveMonitor("SimpleWorkflow")
    
    # Register simple tasks
    tasks = [
        ("load", "Load YAML"),
        ("validate", "Validate"),
        ("generate", "Generate"),
        ("save", "Save Files")
    ]
    
    for task_id, name in tasks:
        monitor.register_task(task_id, name)
    
    # Show initial state
    console.print(monitor.create_workflow_diagram())
    
    # Simulate execution
    for task_id, name in tasks:
        monitor.task_started(task_id)
        await asyncio.sleep(0.5)
        monitor.task_completed(task_id, {"success": True})
        
    # Show final state
    console.print("\n[green]Final State:[/green]")
    console.print(monitor.create_task_table())
    
    return {"demo": "complete"}


async def main():
    """Run all demonstrations"""
    
    console = Console()
    
    console.print("""
[bold magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     BPMN 80/20 Enhancements Demonstration
     
     Showing the power of focused improvements:
     • Live monitoring without external tools
     • Automatic error recovery  
     • Compensation flows
     • Simple, effective, powerful
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold magenta]
""")
    
    # Run demonstrations
    demos = [
        ("Live Monitoring", demo_live_monitoring),
        ("Error Recovery", demo_error_recovery),
        ("Compensation Flow", demo_compensation_flow),
        ("Simple Visualization", demo_simple_monitoring)
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
            await asyncio.sleep(1)  # Pause between demos
        except Exception as e:
            console.print(f"\n[red]Demo '{name}' error: {e}[/red]")
            
    console.print("""
[bold green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ✅ All 80/20 Enhancements Demonstrated!
     
     Key Takeaways:
     • 20% effort (error boundaries + monitoring)
     • 80% value (reliability + visibility)
     • No external dependencies
     • Production-ready patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold green]
""")


if __name__ == "__main__":
    asyncio.run(main())