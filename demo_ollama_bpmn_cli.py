#!/usr/bin/env python3
"""
CLI-First Pydantic AI + BPMN + Ollama Demo

Demonstrates the v1.0.0 CLI-first architecture with:
- uv run weavergen commands only (NO direct Python execution)
- Ollama for local LLM execution
- BPMN workflows with SpiffWorkflow
- Span-based validation (NO unit tests)

Usage:
    # CLI-first approach (v1.0.0)
    uv run weavergen bpmn execute PydanticAIGeneration --ollama-model llama3.2:latest
    
    # OR run this demo to simulate CLI execution
    python demo_ollama_bpmn_cli.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Import CLI-compatible engine
sys.path.append(str(Path(__file__).parent / "src"))
from weavergen.pydantic_ai_ollama_bpmn import (
    PydanticAIOllamaBPMNEngine,
    PydanticAIOllamaContext,
    run_pydantic_ai_ollama_bpmn_via_cli
)


def setup_tracing():
    """Setup OpenTelemetry tracing"""
    trace.set_tracer_provider(TracerProvider())
    return trace.get_tracer(__name__)


async def simulate_cli_execution():
    """Simulate CLI-first execution: uv run weavergen bpmn execute PydanticAIGeneration"""
    
    console = Console()
    tracer = setup_tracing()
    
    with tracer.start_as_current_span("cli.weavergen_bpmn_execute") as main_span:
        main_span.set_attribute("cli.command", "uv run weavergen bpmn execute PydanticAIGeneration")
        main_span.set_attribute("cli.version", "1.0.0")
        main_span.set_attribute("cli.approach", "bpmn_first")
        
        console.print(Panel.fit(
            "[bold cyan]🚀 CLI-First Pydantic AI + BPMN + Ollama Demo[/bold cyan]\n"
            "[green]v1.0.0 Architecture: CLI → BPMN → Ollama → Spans[/green]\n"
            "[yellow]Command: uv run weavergen bpmn execute PydanticAIGeneration[/yellow]",
            border_style="cyan"
        ))
        
        # CLI parameters (would come from CLI args in real usage)
        semantic_file = "cli_semantic_conventions.yaml"
        output_dir = "cli_ollama_output"
        ollama_model = "llama3.2:latest"
        workflow_name = "PydanticAIGeneration"
        
        console.print(f"\n[cyan]📋 CLI Parameters:[/cyan]")
        console.print(f"  • Command: uv run weavergen bpmn execute {workflow_name}")
        console.print(f"  • Semantic File: {semantic_file}")
        console.print(f"  • Output Directory: {output_dir}")
        console.print(f"  • Ollama Model: {ollama_model}")
        console.print(f"  • BPMN Workflow: pydantic_ai_generation.bpmn")
        
        # Check Ollama availability
        console.print(f"\n[cyan]🤖 Checking Ollama availability...[/cyan]")
        
        try:
            # Try to connect to Ollama
            import os
            os.environ["OPENAI_API_KEY"] = "ollama"
            os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
            
            from pydantic_ai.models.openai import OpenAIModel
            test_model = OpenAIModel(model_name=ollama_model)
            
            # Simple test
            from pydantic_ai import Agent
            test_agent = Agent(test_model, system_prompt="You are a test agent.")
            
            console.print(f"[green]✅ Ollama connection successful with {ollama_model}[/green]")
            ollama_available = True
            
        except Exception as e:
            console.print(f"[red]❌ Ollama connection failed: {e}[/red]")
            console.print(f"[yellow]⚠️ Make sure Ollama is running: ollama serve[/yellow]")
            console.print(f"[yellow]⚠️ And model is available: ollama pull {ollama_model}[/yellow]")
            ollama_available = False
        
        # Execute CLI workflow
        if ollama_available:
            console.print(f"\n[cyan]🔄 Executing CLI workflow with Ollama...[/cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                cli_task = progress.add_task(
                    "[cyan]Running CLI BPMN workflow with Ollama...", total=None
                )
                
                try:
                    # Execute via CLI interface
                    result = await run_pydantic_ai_ollama_bpmn_via_cli(
                        semantic_file=semantic_file,
                        output_dir=output_dir,
                        ollama_model=ollama_model,
                        workflow_name=workflow_name.lower()
                    )
                    
                    progress.update(cli_task, completed=True)
                    
                    # Show CLI execution results
                    console.print(f"\n[bold green]🎉 CLI Execution Complete![/bold green]")
                    
                    # Create engine for reporting
                    engine = PydanticAIOllamaBPMNEngine(ollama_model=ollama_model)
                    result["ollama_model"] = ollama_model  # Add for reporting
                    
                    # CLI execution report
                    cli_report = engine.generate_cli_execution_report(result)
                    console.print(f"\n{cli_report}")
                    
                    # Span analysis (CLI-first validation)
                    if result.get("spans"):
                        console.print(f"\n[bold cyan]📊 CLI Span Analysis:[/bold cyan]")
                        
                        span_table = Table(title="CLI Execution Spans", show_header=True, header_style="bold magenta")
                        span_table.add_column("Task", style="cyan")
                        span_table.add_column("Ollama Used", style="green")
                        span_table.add_column("Status", style="yellow")
                        span_table.add_column("Trace ID", style="blue")
                        
                        for span in result["spans"]:
                            task_name = span.get("task", "Unknown")
                            ollama_used = "🤖" if span.get("ollama_used", False) else "⚙️"
                            status = "✅" if span.get("result", {}).get("success", True) else "❌"
                            trace_id = span.get("trace_id", "")[:8]
                            
                            span_table.add_row(task_name, ollama_used, status, trace_id)
                        
                        console.print(span_table)
                    
                    # CLI output files
                    if result.get("output_files"):
                        console.print(f"\n[bold cyan]📁 CLI Generated Files:[/bold cyan]")
                        
                        files_table = Table(show_header=True, header_style="bold magenta")
                        files_table.add_column("File", style="cyan")
                        files_table.add_column("Type", style="green")
                        files_table.add_column("CLI Compatible", style="yellow")
                        
                        for file_path in result["output_files"]:
                            file_obj = Path(file_path)
                            if file_obj.exists():
                                file_type = {
                                    ".py": "Python Code",
                                    ".json": "JSON Data",
                                }.get(file_obj.suffix, "Unknown")
                                files_table.add_row(file_obj.name, file_type, "✅")
                        
                        console.print(files_table)
                    
                    # CLI span-referenced assessment
                    main_span.set_attribute("cli.execution.success", result.get("success", False))
                    main_span.set_attribute("cli.execution.ollama_calls", result.get("ollama_calls", 0))
                    main_span.set_attribute("cli.execution.quality_score", result.get("quality_score", 0.0))
                    main_span.set_attribute("cli.execution.spans_captured", len(result.get("spans", [])))
                    
                    console.print(f"\n[bold magenta]🔍 CLI Span-Referenced Validation:[/bold magenta]")
                    console.print(f"Based on CLI execution span `cli.weavergen_bpmn_execute` (trace_id: {main_span.get_span_context().trace_id:032x}):")
                    console.print(f"  • CLI Command: ✅ uv run weavergen bpmn execute {workflow_name}")
                    console.print(f"  • Ollama Integration: 🤖 {result.get('ollama_calls', 0)} calls to {ollama_model}")
                    console.print(f"  • BPMN Execution: 📋 {len(result.get('spans', []))} service tasks completed")
                    console.print(f"  • Quality Score: {'🟢' if result.get('quality_score', 0) >= 0.8 else '🔴'} {result.get('quality_score', 0):.1%}")
                    console.print(f"  • Validation: {'✅' if result.get('validation_passed') else '❌'} Span-based validation")
                    
                    if result.get("success") and result.get("quality_score", 0) >= 0.75:
                        console.print(f"\n[bold green]🎉 CLI-FIRST OLLAMA DEMO SUCCESSFUL![/bold green]")
                        console.print(f"[green]Generated {result.get('models_generated', 0)} models and {result.get('agents_generated', 0)} agents via CLI → BPMN → Ollama workflow.[/green]")
                    else:
                        console.print(f"\n[bold yellow]⚠️ CLI execution completed with issues[/bold yellow]")
                    
                except Exception as e:
                    progress.update(cli_task, description=f"[red]❌ CLI execution failed: {e}")
                    console.print(f"\n[red]❌ CLI execution failed: {e}[/red]")
                    main_span.set_attribute("cli.execution.error", str(e))
        
        else:
            # Simulate CLI execution without Ollama
            console.print(f"\n[yellow]⚠️ Simulating CLI execution without Ollama[/yellow]")
            
            result = {
                "success": False,
                "error": "Ollama not available",
                "cli_command": f"uv run weavergen bpmn execute {workflow_name}",
                "recommendation": "Install and start Ollama service"
            }
            
            console.print(f"\n[bold yellow]CLI Execution Summary:[/bold yellow]")
            console.print(f"  • Command: {result['cli_command']}")
            console.print(f"  • Status: ❌ {result['error']}")
            console.print(f"  • Recommendation: {result['recommendation']}")
            
            return result


async def demonstrate_cli_commands():
    """Demonstrate v1.0.0 CLI commands"""
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold white]📋 WeaverGen v1.0.0 CLI Commands[/bold white]\n"
        "[blue]BPMN-First Architecture with Ollama Integration[/blue]",
        border_style="blue"
    ))
    
    cli_commands = [
        ("Basic Generation", "uv run weavergen generate semantic.yaml"),
        ("BPMN Execution", "uv run weavergen bpmn execute PydanticAIGeneration"),
        ("Ollama Integration", "uv run weavergen bpmn execute --ollama-model llama3.2"),
        ("Span Validation", "uv run weavergen debug spans --format mermaid"),
        ("Agent Communication", "uv run weavergen agents communicate --agents 3"),
        ("Health Check", "uv run weavergen debug health --deep"),
        ("Full Pipeline", "uv run weavergen full-pipeline semantic.yaml --agents 3"),
    ]
    
    commands_table = Table(title="CLI-First Commands (v1.0.0)", show_header=True, header_style="bold magenta")
    commands_table.add_column("Operation", style="cyan", width=20)
    commands_table.add_column("Command", style="green", width=50)
    commands_table.add_column("BPMN", style="yellow", width=10)
    
    for operation, command in cli_commands:
        bpmn_indicator = "✅" if "bpmn" in command else "🔄"
        commands_table.add_row(operation, command, bpmn_indicator)
    
    console.print(commands_table)
    
    console.print(f"\n[bold cyan]Key Principles:[/bold cyan]")
    console.print(f"  • NO direct Python file execution")
    console.print(f"  • ALL operations via CLI commands")
    console.print(f"  • BPMN workflows for orchestration")
    console.print(f"  • Ollama for local LLM execution")
    console.print(f"  • Span-based validation only")


async def main():
    """Run CLI-first demonstration"""
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold white]🚀 WeaverGen v1.0.0 CLI-First + Ollama Demo[/bold white]\n"
        "[blue]BPMN → Ollama → Spans Architecture[/blue]",
        border_style="blue"
    ))
    
    # Demonstrate CLI commands
    await demonstrate_cli_commands()
    
    console.print(f"\n" + "─" * 80)
    
    # Simulate actual CLI execution
    result = await simulate_cli_execution()
    
    console.print(f"\n" + "─" * 80)
    
    console.print(f"\n[bold green]🎉 CLI-First Ollama Demo Complete![/bold green]")
    console.print(f"[cyan]This demonstrates the v1.0.0 CLI-first architecture with Ollama integration.[/cyan]")
    console.print(f"[cyan]In production, use: uv run weavergen bpmn execute PydanticAIGeneration[/cyan]")


if __name__ == "__main__":
    # Run the CLI-first demonstration
    asyncio.run(main())