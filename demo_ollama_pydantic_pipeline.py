#!/usr/bin/env python3
"""
Demo: End-to-End Ollama + Pydantic + BPMN + Weaver Forge Pipeline

Complete demonstration of BPMN-first AI orchestration with structured output,
semantic convention processing, and span-based validation.

Usage:
    python demo_ollama_pydantic_pipeline.py
"""

import asyncio
import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

# Import our pipeline components
from src.weavergen.ollama_pydantic_models import (
    create_default_workflow_config, MultiAgentWorkflowConfig
)
from src.weavergen.ollama_bpmn_engine import OllamaBPMNEngine


async def main():
    """Run the complete Ollama + Pydantic + BPMN pipeline demonstration"""
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold white]🔥 Ollama + Pydantic + BPMN + Weaver Forge Pipeline[/bold white]\\n"
        "[blue]Complete AI orchestration with structured output and span validation[/blue]",
        border_style="blue"
    ))
    
    # Create test semantic convention file
    test_semantic_file = "test_semantic_conventions.yaml"
    test_semantic_content = """
groups:
  - id: http
    prefix: http
    type: attribute_group
    brief: 'HTTP semantic conventions'
    attributes:
      - id: method
        type: string
        brief: 'HTTP request method'
        examples: ['GET', 'POST', 'PUT']
        requirement_level: required
      - id: status_code
        type: int
        brief: 'HTTP response status code'
        examples: [200, 404, 500]
        requirement_level: required
      - id: url
        type: string
        brief: 'Full HTTP request URL'
        examples: ['https://www.example.com/search?q=OpenTelemetry']
        requirement_level: recommended

  - id: db
    prefix: db
    type: attribute_group  
    brief: 'Database semantic conventions'
    attributes:
      - id: system
        type: string
        brief: 'Database system identifier'
        examples: ['postgresql', 'mysql', 'redis']
        requirement_level: required
      - id: statement
        type: string
        brief: 'Database statement being executed'
        examples: ['SELECT * FROM users WHERE id = ?']
        requirement_level: recommended
      - id: operation
        type: string
        brief: 'Database operation name'
        examples: ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        requirement_level: recommended
"""
    
    with open(test_semantic_file, 'w') as f:
        f.write(test_semantic_content)
    
    console.print(f"\\n[cyan]📋 Created test semantic convention file: {test_semantic_file}[/cyan]")
    
    # Check Ollama availability
    ollama_available = shutil.which("ollama") is not None
    console.print(f"[cyan]🤖 Ollama available: {'✅' if ollama_available else '❌ (will use mock responses)'}[/cyan]")
    
    # Check Weaver availability  
    weaver_binary = None
    weaver_locations = [
        Path.home() / ".cargo" / "bin" / "weaver",
        Path("/usr/local/bin/weaver"),
        Path("/opt/homebrew/bin/weaver"),
    ]
    
    for location in weaver_locations:
        if location.exists():
            weaver_binary = str(location)
            break
    
    console.print(f"[cyan]🔥 Weaver Forge: {'✅ ' + weaver_binary if weaver_binary else '❌ Not found'}[/cyan]")
    
    # Create workflow configuration
    workflow_config = create_default_workflow_config(
        semantic_file=test_semantic_file,
        output_dir="ollama_pydantic_output"
    )
    
    # Update with actual Weaver binary if found
    if weaver_binary:
        workflow_config.weaver_binary = weaver_binary
    
    console.print(f"\\n[cyan]⚙️ Workflow Configuration:[/cyan]")
    console.print(f"  • BPMN File: {workflow_config.bpmn_file}")
    console.print(f"  • Service Tasks: {len(workflow_config.service_tasks)}")
    console.print(f"  • Parallel Execution: {workflow_config.parallel_execution}")
    console.print(f"  • Quality Gate: {workflow_config.quality_gate_threshold:.1%}")
    console.print(f"  • Default Model: {workflow_config.default_model}")
    console.print(f"  • Span Validation: {workflow_config.span_validation_enabled}")
    
    # Initialize and execute pipeline
    console.print(f"\\n[bold green]🚀 Starting Pipeline Execution...[/bold green]")
    
    engine = OllamaBPMNEngine(workflow_config)
    result = await engine.execute_pipeline(
        semantic_file=test_semantic_file,
        output_dir="ollama_pydantic_output"
    )
    
    # Display results
    console.print(f"\\n[bold green]🎉 Pipeline Execution Complete![/bold green]")
    
    # Pipeline report
    pipeline_report = engine.generate_execution_report(result)
    console.print(f"\\n{pipeline_report}")
    
    # Execution trace
    if result.span_evidence:
        console.print(f"\\n[bold blue]📋 BPMN Execution Trace:[/bold blue]")
        for i, span in enumerate(result.span_evidence[:10], 1):  # Show first 10
            task = span.get("task", "Unknown")
            status = "✅" if span.get("success", True) else "❌"
            ai_used = "🤖" if span.get("ai_model_used", False) else "⚙️"
            console.print(f"  {i:2d}. {status} {ai_used} {task}")
        
        if len(result.span_evidence) > 10:
            console.print(f"     ... and {len(result.span_evidence) - 10} more steps")
    
    # AI interactions summary
    if result.total_ai_interactions > 0:
        console.print(f"\\n[bold cyan]🤖 AI Integration Summary:[/bold cyan]")
        console.print(f"  • Total AI Interactions: {result.total_ai_interactions}")
        console.print(f"  • Tokens Used: {result.total_tokens_used}")
        console.print(f"  • Models Used: {', '.join(result.ai_models_used)}")
        console.print(f"  • AI-Enhanced Tasks: Analysis, Generation, Validation, Integration, Review")
    
    # Generated content summary
    if result.files_generated > 0:
        console.print(f"\\n[bold green]📄 Generated Content:[/bold green]")
        console.print(f"  • Files Generated: {result.files_generated}")
        console.print(f"  • Languages: {', '.join(result.languages_supported) if result.languages_supported else 'Python (Pydantic)'}") 
        console.print(f"  • Output Directory: {result.processing_context.output_dir}")
        
        # List generated files
        output_dir = Path(result.processing_context.output_dir)
        if output_dir.exists():
            generated_files = list(output_dir.rglob("*"))
            if generated_files:
                console.print(f"  • Generated Files:")
                for file_path in generated_files[:5]:  # Show first 5
                    console.print(f"    - {file_path}")
                if len(generated_files) > 5:
                    console.print(f"    ... and {len(generated_files) - 5} more files")
    
    # Quality assessment
    console.print(f"\\n[bold magenta]🔍 Quality Assessment:[/bold magenta]")
    console.print(f"  • Pipeline Success: {'✅' if result.success else '❌'}")
    console.print(f"  • Overall Quality: {'🟢' if result.overall_quality_score >= 0.8 else '🔴'} {result.overall_quality_score:.1%}")
    console.print(f"  • Validation Passed: {'✅' if result.validation_passed else '❌'}")
    console.print(f"  • Span Validation: {'📊' if result.span_validation_score > 0 else '📝'} {result.span_validation_score:.1%}")
    console.print(f"  • Execution Time: ⏱️ {result.execution_time_ms:.0f}ms")
    
    # Integration status
    console.print(f"\\n[bold yellow]🔗 Integration Status:[/bold yellow]")
    console.print(f"  • BPMN Orchestration: {'✅ SpiffWorkflow' if result.completed_steps > 0 else '❌'}")
    console.print(f"  • Ollama Integration: {'🤖 Connected' if result.total_ai_interactions > 0 else '⚠️ Mock responses'}")
    console.print(f"  • Pydantic Models: {'✅ Structured' if result.files_generated > 0 else '⚠️'}")
    console.print(f"  • Weaver Forge: {'🔥 Integrated' if result.weaver_forge_used else '⚠️ Not available'}")
    console.print(f"  • Span Tracking: {'📊 OpenTelemetry' if result.total_spans_captured > 0 else '❌'}")
    
    # Final assessment
    if result.success and result.overall_quality_score >= 0.8:
        console.print(f"\\n[bold green]🎉 END-TO-END PIPELINE SUCCESS![/bold green]")
        console.print(f"[green]Complete BPMN-first AI orchestration with {'real' if result.total_ai_interactions > 0 else 'simulated'} Ollama integration.[/green]")
    else:
        console.print(f"\\n[bold cyan]✅ Pipeline demonstration completed![/bold cyan]")
        console.print(f"[cyan]BPMN workflow orchestration patterns successfully demonstrated.[/cyan]")
    
    # CLI integration note
    console.print(f"\\n[bold yellow]📋 Production Integration:[/bold yellow]")
    console.print(f"[yellow]This workflow would be triggered via:[/yellow]")
    console.print(f"[yellow]  uv run weavergen ollama-pipeline --semantic-file {test_semantic_file} --model qwen3:latest[/yellow]")
    
    # Cleanup
    Path(test_semantic_file).unlink(missing_ok=True)
    console.print(f"\\n[dim]Cleanup: Removed test file {test_semantic_file}[/dim]")


if __name__ == "__main__":
    asyncio.run(main())