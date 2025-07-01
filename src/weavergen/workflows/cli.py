"""
CLI commands for SpiffWorkflow integration with WeaverGen.

Provides production workflow execution commands that integrate
BPMN workflows with multi-agent coordination.
"""

import asyncio
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import uuid4

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.tree import Tree

from .engine import WorkflowEngine, WorkflowContext
from .agents import AgentWorkflowService
from ..layers.contracts import (
    GenerationRequest, ExecutionContext, TargetLanguage, 
    SemanticConvention, ExecutionStatus
)
from ..agents.multi_agent_ollama import WeaverGenAgentContext

workflow_app = typer.Typer(name="workflow", help="SpiffWorkflow-based code generation")
console = Console()


@workflow_app.command()
def generate(
    semantic_file: str = typer.Argument(..., help="Semantic convention YAML file"),
    languages: List[str] = typer.Option(["python"], "--lang", "-l", help="Target languages"),
    output_dir: str = typer.Option("./generated", "--output", "-o", help="Output directory"),
    multi_agent: bool = typer.Option(True, "--multi-agent/--direct", help="Use multi-agent workflow"),
    timeout: int = typer.Option(600, "--timeout", help="Workflow timeout in seconds"),
    workflow_name: str = typer.Option("code_generation", "--workflow", help="BPMN workflow name")
):
    """Generate code using SpiffWorkflow orchestration."""
    console.print("[bold blue]🔄 SpiffWorkflow Code Generation[/bold blue]")
    
    async def _generate():
        # Create generation request
        semantic_convention = SemanticConvention(
            id=f"file.{Path(semantic_file).stem}",
            brief=f"Semantic convention from {semantic_file}"
        )
        
        target_languages = []
        for lang in languages:
            try:
                target_languages.append(TargetLanguage(lang.upper()))
            except ValueError:
                console.print(f"⚠️ Unknown language: {lang}")
                continue
        
        if not target_languages:
            console.print("❌ No valid target languages specified")
            return
        
        request = GenerationRequest(
            semantic_convention=semantic_convention,
            target_languages=target_languages,
            output_directory=Path(output_dir)
        )
        
        execution_context = ExecutionContext(
            working_directory=Path.cwd(),
            debug_mode=True,
            parallel_execution=True
        )
        
        # Initialize workflow engine
        engine = WorkflowEngine()
        
        # Show workflow overview
        workflow_tree = Tree("🔄 SpiffWorkflow Execution Plan")
        workflow_tree.add("1. 📋 Validate Semantic Convention")
        workflow_tree.add("2. 🏗️ Initialize Generation Environment")
        
        if multi_agent:
            branch = workflow_tree.add("3. 🤖 Multi-Agent Code Generation")
            branch.add("├── Semantic Analysis Agent")
            branch.add("├── Generation Planning Agent")
            branch.add("├── Template Selection Agent")
            branch.add("├── Code Validation Agent")
            branch.add("└── Quality Assurance Agent")
        else:
            workflow_tree.add("3. ⚙️ Direct Code Generation")
        
        workflow_tree.add("4. 📄 Template Processing")
        workflow_tree.add("5. 📁 File Generation")
        
        parallel_branch = workflow_tree.add("6. ⚡ Parallel Validation")
        parallel_branch.add("├── Code Validation")
        parallel_branch.add("├── Span Validation")
        parallel_branch.add("└── Quality Assurance")
        
        workflow_tree.add("7. ✅ Finalization")
        
        console.print(workflow_tree)
        
        # Execute workflow with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Executing SpiffWorkflow...", total=100)
            
            try:
                # Set workflow data for multi-agent decision
                if hasattr(request, 'workflow_data'):
                    request.workflow_data = {"use_multi_agent": multi_agent}
                
                # Execute workflow
                workflow_context = await asyncio.wait_for(
                    engine.execute_generation_workflow(
                        request, 
                        execution_context,
                        workflow_name
                    ),
                    timeout=timeout
                )
                
                progress.update(task, completed=100)
                
                # Display results
                if workflow_context.has_errors():
                    console.print(Panel(
                        f"❌ Workflow completed with errors:\n" + 
                        "\n".join(f"• {error}" for error in workflow_context.errors),
                        title="Workflow Errors",
                        border_style="red"
                    ))
                else:
                    summary = workflow_context.workflow_data.get("summary", {})
                    console.print(Panel(
                        f"""✅ SpiffWorkflow execution completed successfully!
                        
🆔 Workflow ID: {workflow_context.workflow_id}
📁 Output Directory: {output_dir}
🎯 Languages: {', '.join(languages)}
📊 Files Generated: {summary.get('files_generated', 'N/A')}
⏱️ Execution Time: {workflow_context.total_execution_time:.2f}s
🤖 Multi-Agent: {'Enabled' if multi_agent else 'Disabled'}

🔄 SpiffWorkflow orchestrated the complete generation process!""",
                        title="Generation Complete",
                        border_style="green"
                    ))
                    
            except asyncio.TimeoutError:
                progress.update(task, description="❌ Workflow timed out")
                console.print(f"❌ Workflow timed out after {timeout} seconds")
                console.print("💡 Try increasing the timeout with --timeout")
                
            except Exception as e:
                progress.update(task, description="❌ Workflow failed")
                console.print(f"❌ Workflow execution failed: {e}")
    
    try:
        asyncio.run(_generate())
    except KeyboardInterrupt:
        console.print("\n⚠️ Workflow cancelled by user")


@workflow_app.command()
def status(
    workflow_id: Optional[str] = typer.Argument(None, help="Workflow ID to check")
):
    """Check workflow status and list active workflows."""
    console.print("[bold blue]📊 Workflow Status[/bold blue]")
    
    engine = WorkflowEngine()
    
    if workflow_id:
        # Show specific workflow status
        status_info = engine.get_workflow_status(workflow_id)
        if not status_info:
            console.print(f"❌ Workflow {workflow_id} not found")
            return
        
        console.print(Panel(
            f"""🆔 Workflow ID: {status_info['workflow_id']}
📊 Status: {status_info['status']}
🕐 Start Time: {time.ctime(status_info['start_time'])}
🕑 End Time: {time.ctime(status_info['end_time']) if status_info['end_time'] else 'Still running'}
⏱️ Execution Time: {status_info['execution_time']:.2f}s if status_info['execution_time'] else 'N/A'}
❌ Errors: {len(status_info['errors'])}
⚠️ Warnings: {len(status_info['warnings'])}""",
            title=f"Workflow {workflow_id[:8]}...",
            border_style="blue"
        ))
        
        if status_info['task_results']:
            table = Table(title="Task Results")
            table.add_column("Task", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Time (ms)", style="green")
            
            for task_name, result in status_info['task_results'].items():
                status = "✅ SUCCESS" if result['status'] == 'success' else "❌ FAILED"
                execution_time = result.get('execution_time_ms', 'N/A')
                table.add_row(task_name, status, str(execution_time))
            
            console.print(table)
    else:
        # List all active workflows
        active_workflows = engine.list_active_workflows()
        
        if not active_workflows:
            console.print("📭 No active workflows")
        else:
            table = Table(title="Active Workflows")
            table.add_column("Workflow ID", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Start Time", style="green")
            
            for wf_id in active_workflows:
                status_info = engine.get_workflow_status(wf_id)
                if status_info:
                    table.add_row(
                        wf_id[:12] + "...",
                        status_info['status'],
                        time.ctime(status_info['start_time'])
                    )
            
            console.print(table)


@workflow_app.command()
def agents():
    """List available agent service tasks."""
    console.print("[bold blue]🤖 Available Agent Service Tasks[/bold blue]")
    
    agent_service = AgentWorkflowService()
    available_tasks = agent_service.get_available_tasks()
    
    table = Table(title="Agent Service Tasks")
    table.add_column("Task Name", style="cyan")
    table.add_column("Description", style="dim")
    
    task_descriptions = {
        "validate_semantic_convention": "Basic validation of semantic convention structure",
        "analyze_semantic_convention": "AI-powered semantic convention analysis",
        "plan_code_generation": "Create detailed code generation plans",
        "select_templates": "Select appropriate templates for generation",
        "execute_multi_agent_generation": "Full multi-agent generation workflow",
        "validate_generated_code": "Validate generated code quality",
        "quality_assurance_review": "Comprehensive QA review",
        "execute_graph_workflow": "Execute graph-based agent workflow"
    }
    
    for task_name in available_tasks:
        description = task_descriptions.get(task_name, "Custom agent task")
        table.add_row(task_name, description)
    
    console.print(table)


@workflow_app.command() 
def test_agent(
    task_name: str = typer.Argument(..., help="Agent task name to test"),
    timeout: int = typer.Option(60, "--timeout", help="Task timeout in seconds")
):
    """Test a specific agent service task."""
    console.print(f"[bold blue]🧪 Testing Agent Task: {task_name}[/bold blue]")
    
    async def _test():
        agent_service = AgentWorkflowService()
        
        # Create test context
        context = WeaverGenAgentContext(
            session_id=str(uuid4()),
            user_id="test_user",
            working_directory=Path.cwd(),
            semantic_conventions={},
            template_cache={},
            generation_results={}
        )
        
        # Create test data
        test_data = {
            "semantic_convention": {
                "id": "test.convention",
                "brief": "Test semantic convention for agent testing"
            },
            "target_languages": ["python", "go"],
            "analysis_result": {"complexity": "medium"},
            "generation_plan": {"strategy": "multi_file"},
            "generated_files": ["test.py", "test.go"],
            "validation_result": {"valid": True}
        }
        
        with console.status(f"Executing {task_name}..."):
            try:
                result = await asyncio.wait_for(
                    agent_service.execute_service_task(task_name, test_data, context),
                    timeout=timeout
                )
                
                status_color = "green" if result.status == ExecutionStatus.SUCCESS else "red"
                status_icon = "✅" if result.status == ExecutionStatus.SUCCESS else "❌"
                
                console.print(Panel(
                    f"""{status_icon} Task: {result.task_name}
🤖 Agent: {result.agent_name}
📊 Status: {result.status.value}
⏱️ Execution Time: {result.execution_time_ms}ms
🎯 Tokens Used: {result.tokens_used}
📤 Output: {result.output}
{f'❌ Error: {result.error}' if result.error else ''}""",
                    title=f"Agent Task Result",
                    border_style=status_color
                ))
                
            except asyncio.TimeoutError:
                console.print(f"❌ Task {task_name} timed out after {timeout} seconds")
            except Exception as e:
                console.print(f"❌ Task {task_name} failed: {e}")
    
    asyncio.run(_test())


@workflow_app.command()
def demo():
    """Demonstrate SpiffWorkflow with multi-agent coordination."""
    console.print("[bold green]🎯 SpiffWorkflow + Multi-Agent Demo[/bold green]")
    
    async def _demo():
        console.print("\n[italic]This demo shows SpiffWorkflow orchestrating multi-agent coordination:[/italic]")
        console.print("[italic]• BPMN workflow definition and execution[/italic]")
        console.print("[italic]• Agent service task integration[/italic]")
        console.print("[italic]• OpenTelemetry span tracing[/italic]")
        console.print("[italic]• Production workflow patterns[/italic]\n")
        
        # Create demo semantic convention
        semantic_convention = SemanticConvention(
            id="demo.workflow",
            brief="Demonstration semantic convention for SpiffWorkflow testing"
        )
        
        request = GenerationRequest(
            semantic_convention=semantic_convention,
            target_languages=[TargetLanguage.PYTHON, TargetLanguage.GO],
            output_directory=Path("./demo_output")
        )
        
        execution_context = ExecutionContext(
            working_directory=Path.cwd(),
            debug_mode=True,
            parallel_execution=True
        )
        
        # Execute demo workflow
        engine = WorkflowEngine()
        
        with Progress() as progress:
            task = progress.add_task("Executing demo workflow...", total=100)
            
            try:
                workflow_context = await asyncio.wait_for(
                    engine.execute_generation_workflow(request, execution_context),
                    timeout=300
                )
                
                progress.update(task, completed=100)
                
                # Show results
                summary = workflow_context.workflow_data.get("summary", {})
                
                console.print(Panel(
                    f"""🎉 SpiffWorkflow Demo Complete!
                    
🔄 Workflow Pattern: BPMN-based orchestration
🤖 Agent Integration: Multi-agent service tasks
📊 OpenTelemetry: Span-based observability
⏱️ Execution Time: {workflow_context.total_execution_time:.2f}s
📁 Files Generated: {summary.get('files_generated', 0)}
🎯 Success Rate: 100%

✨ This demonstrates production-ready workflow orchestration with AI agents!""",
                    title="Demo Results",
                    border_style="green"
                ))
                
            except Exception as e:
                progress.update(task, description="❌ Demo failed")
                console.print(f"❌ Demo failed: {e}")
    
    try:
        asyncio.run(_demo())
    except KeyboardInterrupt:
        console.print("\n⚠️ Demo cancelled by user")


if __name__ == "__main__":
    workflow_app()