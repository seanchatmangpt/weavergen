#!/usr/bin/env python3
"""
End-to-End Pydantic AI + BPMN Demo

This script demonstrates the complete integration between Pydantic AI agents
and BPMN workflows with comprehensive OpenTelemetry span tracking.

BPMN-First Architecture:
- Visual workflow orchestration (.bpmn files)
- Pydantic AI agents as BPMN service tasks
- OpenTelemetry spans for execution truth validation
- Rich console output with span-referenced reporting

Usage:
    python demo_pydantic_ai_bpmn_e2e.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

# Import our BPMN + Pydantic AI engine
sys.path.append(str(Path(__file__).parent / "src"))
from weavergen.pydantic_ai_bpmn_engine import (
    PydanticAIBPMNEngine,
    PydanticAIContext,
    run_pydantic_ai_bpmn_workflow
)
from weavergen.span_validator import SpanCaptureSystem, SpanValidator, SpanReportGenerator


def setup_tracing():
    """Setup OpenTelemetry tracing"""
    
    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())
    
    return trace.get_tracer(__name__)


async def demo_pydantic_ai_bpmn_workflow():
    """Demonstrate end-to-end Pydantic AI + BPMN workflow"""
    
    console = Console()
    tracer = setup_tracing()
    
    with tracer.start_as_current_span("demo.pydantic_ai_bpmn_e2e") as main_span:
        main_span.set_attribute("demo.type", "end_to_end")
        main_span.set_attribute("demo.framework", "pydantic_ai_bpmn")
        
        console.print(Panel.fit(
            "[bold cyan]🤖 End-to-End Pydantic AI + BPMN Demo[/bold cyan]\n"
            "[green]BPMN-First Architecture with AI Agent Generation[/green]",
            border_style="cyan"
        ))
        
        # Setup
        semantic_file = "demo_semantic_conventions.yaml"
        output_dir = "demo_pydantic_ai_output"
        
        console.print(f"\n[cyan]📋 Configuration:[/cyan]")
        console.print(f"  • Semantic File: {semantic_file}")
        console.print(f"  • Output Directory: {output_dir}")
        console.print(f"  • BPMN Workflow: pydantic_ai_generation.bpmn")
        
        # Create engine and context
        engine = PydanticAIBPMNEngine()
        context = PydanticAIContext(
            semantic_file=semantic_file,
            output_dir=output_dir,
            agent_roles=["analyst", "coordinator", "validator", "generator"],
            quality_threshold=0.75
        )
        
        console.print(f"\n[cyan]🎯 Agent Roles: {', '.join(context.agent_roles)}[/cyan]")
        console.print(f"[cyan]📊 Quality Threshold: {context.quality_threshold:.1%}[/cyan]")
        
        # Execute workflow with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            workflow_task = progress.add_task(
                "[cyan]Executing BPMN workflow...", total=None
            )
            
            try:
                # Run the complete workflow
                result = await engine.execute_workflow("pydantic_ai_generation", context)
                
                progress.update(workflow_task, completed=True)
                
            except Exception as e:
                progress.update(workflow_task, description=f"[red]❌ Workflow failed: {e}")
                console.print(f"\n[red]❌ Execution failed: {e}[/red]")
                return
        
        # Display results
        console.print(f"\n[bold green]🎉 Workflow Execution Complete![/bold green]")
        
        # Execution report table
        report_table = engine.generate_execution_report(result)
        console.print(f"\n{report_table}")
        
        # Span analysis
        if result.get("spans"):
            console.print(f"\n[bold cyan]📊 Span Analysis:[/bold cyan]")
            
            span_validator = SpanValidator()
            span_result = span_validator.validate_spans(result["spans"])
            
            span_table = Table(title="Span Validation Results", show_header=True, header_style="bold magenta")
            span_table.add_column("Metric", style="cyan")
            span_table.add_column("Value", style="green")
            span_table.add_column("Status", style="yellow")
            
            span_table.add_row("Total Spans", str(span_result.total_spans), "📊")
            span_table.add_row("Valid Spans", str(span_result.valid_spans), "✅")
            span_table.add_row("Health Score", f"{span_result.health_score:.1%}", "🟢" if span_result.health_score >= 0.8 else "🔴")
            span_table.add_row("Semantic Compliance", f"{span_result.semantic_compliance:.1%}", "✅")
            span_table.add_row("Coverage Score", f"{span_result.coverage_score:.1%}", "📈")
            span_table.add_row("Hierarchy Valid", str(span_result.hierarchy_valid), "🌳")
            
            console.print(span_table)
            
            # Span tree visualization
            if len(result["spans"]) > 0:
                reporter = SpanReportGenerator()
                tree = reporter.generate_tree_report(result["spans"])
                console.print(f"\n[bold]Execution Trace Tree:[/bold]")
                console.print(tree)
        
        # Generated artifacts
        if result.get("output_files"):
            console.print(f"\n[bold cyan]📁 Generated Artifacts:[/bold cyan]")
            
            artifacts_table = Table(show_header=True, header_style="bold magenta")
            artifacts_table.add_column("File", style="cyan")
            artifacts_table.add_column("Type", style="green")
            artifacts_table.add_column("Size", style="yellow")
            
            for file_path in result["output_files"]:
                file_path_obj = Path(file_path)
                if file_path_obj.exists():
                    file_type = "Python Code" if file_path_obj.suffix == ".py" else "JSON Data"
                    file_size = f"{file_path_obj.stat().st_size} bytes"
                    artifacts_table.add_row(file_path_obj.name, file_type, file_size)
            
            console.print(artifacts_table)
        
        # Execution trace Mermaid diagram
        if result.get("execution_trace"):
            mermaid_trace = engine.generate_mermaid_trace(result)
            console.print(f"\n[bold blue]🎯 Execution Flow (Mermaid):[/bold blue]")
            console.print(f"```mermaid\n{mermaid_trace}\n```")
        
        # Span-referenced validation
        main_span.set_attribute("demo.success", result.get("success", False))
        main_span.set_attribute("demo.models_generated", result.get("models_generated", 0))
        main_span.set_attribute("demo.agents_generated", result.get("agents_generated", 0))
        main_span.set_attribute("demo.quality_score", result.get("quality_score", 0.0))
        main_span.set_attribute("demo.spans_captured", len(result.get("spans", [])))
        
        # Final assessment with span references
        console.print(f"\n[bold magenta]🔍 Span-Referenced Validation:[/bold magenta]")
        console.print(f"Based on span `demo.pydantic_ai_bpmn_e2e` (trace_id: {main_span.get_span_context().trace_id:032x}):")
        console.print(f"  • Execution Success: {'✅' if result.get('success') else '❌'}")
        console.print(f"  • Quality Score: {result.get('quality_score', 0):.1%}")
        console.print(f"  • Spans Generated: {len(result.get('spans', []))}")
        console.print(f"  • Validation Passed: {'✅' if result.get('validation_passed') else '❌'}")
        
        if result.get("success") and result.get("quality_score", 0) >= context.quality_threshold:
            console.print(f"\n[bold green]🎉 END-TO-END DEMO SUCCESSFUL![/bold green]")
            console.print(f"[green]All components generated and validated via BPMN workflow execution.[/green]")
        else:
            console.print(f"\n[bold yellow]⚠️ Demo completed with issues[/bold yellow]")
            console.print(f"[yellow]Review span data and execution trace for optimization opportunities.[/yellow]")
        
        return result


async def demo_incremental_bpmn_execution():
    """Demonstrate incremental BPMN task execution with live span tracking"""
    
    console = Console()
    tracer = setup_tracing()
    
    with tracer.start_as_current_span("demo.incremental_bpmn") as span:
        console.print(Panel.fit(
            "[bold cyan]⚡ Incremental BPMN Execution Demo[/bold cyan]\n"
            "[green]Step-by-step workflow with live span tracking[/green]",
            border_style="cyan"
        ))
        
        engine = PydanticAIBPMNEngine()
        context = PydanticAIContext(
            semantic_file="incremental_demo.yaml",
            output_dir="incremental_output",
            agent_roles=["analyst", "generator"]
        )
        
        # Simulate incremental execution
        tasks = [
            ("Load Semantics", engine._load_semantics),
            ("Validate Input", engine._validate_input),
            ("Generate Models", engine._generate_models),
            ("Generate Agents", engine._generate_agents),
            ("Validate Models", engine._validate_models),
            ("Test Agents", engine._test_agents),
            ("Integration Test", engine._integration_test),
            ("Generate Output", engine._generate_output),
            ("Capture Spans", engine._capture_spans),
        ]
        
        with Live(console=console, refresh_per_second=4) as live:
            results_table = Table(title="Incremental BPMN Execution", show_header=True, header_style="bold magenta")
            results_table.add_column("Task", style="cyan", width=20)
            results_table.add_column("Status", style="green", width=10)
            results_table.add_column("Duration", style="yellow", width=10)
            results_table.add_column("Spans", style="blue", width=8)
            results_table.add_column("Result", style="white", width=30)
            
            import time
            
            for i, (task_name, task_func) in enumerate(tasks):
                # Update display
                for j, (prev_task, _) in enumerate(tasks[:i]):
                    if j < len(results_table.rows):
                        continue
                    results_table.add_row(prev_task, "✅", "0.5s", "1", "Success")
                
                # Add current task as running
                results_table.add_row(task_name, "⏳", "...", "...", "Running...")
                live.update(results_table)
                
                # Execute task
                start_time = time.time()
                try:
                    result = await task_func(context)
                    duration = f"{time.time() - start_time:.1f}s"
                    status = "✅"
                    result_text = "Success" if result.get("success", True) else "Warning"
                except Exception as e:
                    duration = f"{time.time() - start_time:.1f}s"
                    status = "❌"
                    result_text = f"Error: {str(e)[:25]}..."
                
                # Update the last row
                results_table.rows[-1] = (task_name, status, duration, "1", result_text)
                live.update(results_table)
                
                # Small delay for demo effect
                await asyncio.sleep(0.5)
        
        # Final results
        console.print(f"\n[bold green]✅ Incremental execution complete![/bold green]")
        console.print(f"[cyan]Total spans captured: {len(context.spans)}[/cyan]")
        
        # Span validation
        if context.spans:
            span_validator = SpanValidator()
            validation_result = span_validator.validate_spans(context.spans)
            
            console.print(f"\n[bold]Span Validation Summary:[/bold]")
            console.print(f"  • Health Score: {validation_result.health_score:.1%}")
            console.print(f"  • Valid Spans: {validation_result.valid_spans}/{validation_result.total_spans}")
            console.print(f"  • Semantic Compliance: {validation_result.semantic_compliance:.1%}")
        
        span.set_attribute("demo.incremental_tasks", len(tasks))
        span.set_attribute("demo.spans_generated", len(context.spans))
        
        return context


async def main():
    """Run all end-to-end demos"""
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold white]🚀 Pydantic AI + BPMN End-to-End Demonstrations[/bold white]\n"
        "[blue]Complete integration showcase with span validation[/blue]",
        border_style="blue"
    ))
    
    demos = [
        ("Full Workflow", demo_pydantic_ai_bpmn_workflow),
        ("Incremental Execution", demo_incremental_bpmn_execution),
    ]
    
    for demo_name, demo_func in demos:
        console.print(f"\n[bold cyan]🎯 Running: {demo_name}[/bold cyan]")
        console.print("─" * 60)
        
        try:
            result = await demo_func()
            console.print(f"[green]✅ {demo_name} completed successfully[/green]")
        except Exception as e:
            console.print(f"[red]❌ {demo_name} failed: {e}[/red]")
        
        console.print("─" * 60)
    
    console.print(f"\n[bold green]🎉 All demonstrations complete![/bold green]")
    console.print(f"[cyan]Review the generated output directories and span files for detailed results.[/cyan]")


if __name__ == "__main__":
    # Run the complete end-to-end demonstration
    asyncio.run(main())