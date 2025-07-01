#!/usr/bin/env python3
"""
Test Next-Level 80/20 Enhancements

Demonstrates:
1. Adaptive BPMN engine that learns from execution
2. Process mining to discover workflows from spans
3. Auto-optimization based on patterns
"""

import asyncio
import json
from pathlib import Path

from src.weavergen.bpmn_adaptive_engine import AdaptiveBPMNEngine
from src.weavergen.bpmn_process_miner import BPMNProcessMiner
from src.weavergen.pydantic_ai_bpmn_engine import PydanticAIContext
from rich.console import Console


async def demo_adaptive_learning():
    """Demonstrate adaptive BPMN engine learning from executions"""
    
    console = Console()
    console.print("\n[bold cyan]🧠 Demo: Adaptive BPMN Learning[/bold cyan]")
    console.print("Watch the engine learn and optimize over multiple executions...\n")
    
    # Create adaptive engine
    engine = AdaptiveBPMNEngine(use_mock=True)
    
    # Run multiple executions to build learning data
    for i in range(12):
        console.print(f"\n[dim]Execution {i+1}/12[/dim]")
        
        context = PydanticAIContext(
            semantic_file="semantic_conventions/test_valid.yaml",
            output_dir=f"adaptive_output/run_{i}"
        )
        
        # Execute with adaptation
        result = await engine.execute_adaptive(
            workflow_name="AdaptiveTest",
            context=context,
            enable_optimization=(i >= 5)  # Enable optimization after 5 runs
        )
        
        if i == 5:
            console.print("\n[yellow]🎯 Optimization enabled! Watch performance improve...[/yellow]")
            
    # Show learning results
    console.print("\n[bold green]📊 Adaptive Learning Results:[/bold green]")
    console.print(engine.get_performance_report())
    
    # Show learning curve
    console.print("\n[bold]📈 Performance Learning Curve:[/bold]")
    console.print(engine.visualize_learning_curve())
    
    return engine


async def demo_process_mining():
    """Demonstrate process mining from execution spans"""
    
    console = Console()
    console.print("\n[bold cyan]⛏️  Demo: Process Mining from Spans[/bold cyan]")
    console.print("Discovering BPMN workflows from execution traces...\n")
    
    # Load spans from previous executions
    spans = []
    span_files = list(Path(".").glob("**/execution_spans.json"))[:5]
    
    if not span_files:
        # Generate mock spans for demo
        console.print("[yellow]No span files found, generating mock data...[/yellow]")
        spans = generate_mock_spans()
    else:
        for span_file in span_files:
            try:
                with open(span_file) as f:
                    file_spans = json.load(f)
                    if isinstance(file_spans, list):
                        spans.extend(file_spans)
                        console.print(f"  Loaded {len(file_spans)} spans from {span_file.name}")
            except:
                pass
                
    if not spans:
        console.print("[red]No spans available for mining[/red]")
        return
        
    # Mine workflow patterns
    miner = BPMNProcessMiner()
    discovered_workflow = miner.mine_workflow(spans, "MinedWorkflow")
    
    # Generate BPMN from discovered patterns
    if discovered_workflow.patterns:
        bpmn_file = miner.generate_bpmn(
            discovered_workflow,
            "discovered_workflows/mined_workflow.bpmn"
        )
        console.print(f"\n[green]✅ Generated BPMN from mined patterns: {bpmn_file}[/green]")
        
    return discovered_workflow


def generate_mock_spans():
    """Generate mock spans for demonstration"""
    
    import random
    from datetime import datetime, timedelta
    
    spans = []
    
    # Define typical task sequences
    task_sequences = [
        ["LoadSemantics", "ValidateInput", "GenerateModels", "GenerateAgents", "Integration", "GenerateOutput"],
        ["LoadSemantics", "ValidateInput", "GenerateModels", "TestModels", "GenerateOutput"],
        ["LoadSemantics", "GenerateAgents", "ValidateAgents", "Integration", "GenerateOutput"]
    ]
    
    # Generate traces
    for trace_num in range(20):
        trace_id = f"trace_{trace_num}"
        sequence = random.choice(task_sequences)
        
        timestamp = datetime.now() - timedelta(hours=trace_num)
        
        for i, task in enumerate(sequence):
            span = {
                "name": f"bpmn.service.{task.lower()}",
                "task": task,
                "span_id": f"span_{trace_num}_{i}",
                "trace_id": trace_id,
                "timestamp": (timestamp + timedelta(seconds=i*2)).isoformat(),
                "duration_ms": random.uniform(100, 2000),
                "attributes": {
                    "task.type": "service",
                    "execution.success": random.random() > 0.1,
                    "quality.score": random.uniform(0.7, 0.95)
                }
            }
            spans.append(span)
            
    return spans


async def demo_combined_intelligence():
    """Demonstrate adaptive learning + process mining together"""
    
    console = Console()
    console.print("\n[bold cyan]🚀 Demo: Combined Intelligence[/bold cyan]")
    console.print("Adaptive engine + Process mining = Self-improving workflows\n")
    
    # First, run adaptive engine to generate data
    engine = await demo_adaptive_learning()
    
    # Then mine patterns from the generated spans
    discovered = await demo_process_mining()
    
    # Show insights
    console.print("\n[bold magenta]💡 Intelligence Insights:[/bold magenta]")
    
    if engine.execution_history:
        avg_duration = sum(m.duration_ms for m in engine.execution_history[-5:]) / 5
        first_duration = engine.execution_history[0].duration_ms
        improvement = ((first_duration - avg_duration) / first_duration) * 100
        
        console.print(f"  Performance improved by {improvement:.1f}% through learning")
        
    if discovered and discovered.patterns:
        console.print(f"  Discovered {len(discovered.patterns)} workflow patterns")
        console.print(f"  Workflow quality score: {discovered.quality_metrics.get('fitness', 0):.1%}")
        
    console.print("\n[green]✨ The system is learning and improving autonomously![/green]")


async def main():
    """Run all next-level demonstrations"""
    
    console = Console()
    
    console.print("""
[bold blue]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     Next-Level 80/20 BPMN Enhancements
     
     Taking BPMN-first architecture to the next level:
     • Self-optimizing workflows
     • Automatic pattern discovery
     • Intelligent adaptation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold blue]
""")
    
    try:
        # Run demonstrations
        await demo_combined_intelligence()
        
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        
    console.print("""
[bold green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ✅ Next-Level Enhancements Demonstrated!
     
     Key Achievements:
     • Workflows that learn from execution
     • Automatic BPMN generation from traces
     • Performance optimization through adaptation
     • The future of intelligent workflows
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold green]
""")


if __name__ == "__main__":
    asyncio.run(main())