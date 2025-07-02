"""
WeaverGen v2 BPMN Commands
BPMN-first workflow execution and orchestration
"""

import typer
import asyncio
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

from ...core.engine.spiff_engine import WeaverGenV2Engine
from ...weavergen.src.visualizers.mermaid import MermaidVisualizer, MermaidLifecycleGenerator
from rich.syntax import Syntax

app = typer.Typer(
    name="bpmn",
    help="BPMN-first workflow execution and management",
    rich_markup_mode="rich"
)

console = Console()

@app.command("execute")
def bpmn_execute(
    ctx: typer.Context,
    workflow: str = typer.Argument(help="BPMN workflow name to execute"),
    context_file: Optional[Path] = typer.Option(None, "--context", "-c", help="Context data JSON file"),
    trace: bool = typer.Option(False, "--trace", help="Enable execution tracing"),
    save_trace: bool = typer.Option(True, "--save-trace/--no-trace", help="Save execution trace"),
    output_dir: Path = typer.Option(Path("./bpmn_output"), "--output", "-o")
):
    """Execute a BPMN workflow with SpiffWorkflow engine"""
    
    async def run_execute():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        # Load context data if provided
        workflow_context = {}
        if context_file and context_file.exists():
            with open(context_file) as f:
                workflow_context = json.load(f)
        
        workflow_context.update({
            "workflow_name": workflow,
            "enable_trace": trace,
            "output_dir": str(output_dir),
            "cli_command": "bpmn execute"
        })
        
        console.print(Panel(
            f"[bold blue]BPMN Workflow Execution[/bold blue]\n"
            f"Workflow: {workflow}\n"
            f"Tracing: {'Enabled' if trace else 'Disabled'}\n"
            f"Output: {output_dir}",
            title="Execution Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"⚙️ Executing {workflow} workflow...", total=None)
            
            try:
                result = await engine.execute_workflow(workflow, workflow_context)
                
                if result.success:
                    execution_result = result.final_data
                    progress.update(task, description="✅ Workflow execution complete")
                    
                    display_execution_results(execution_result, workflow)
                    
                    if save_trace and result.trace:
                        trace_file = output_dir / f"{workflow}_trace.json"
                        output_dir.mkdir(exist_ok=True)
                        with open(trace_file, 'w') as f:
                            json.dump(result.trace, f, indent=2, default=str)
                        console.print(f"[green]Execution trace saved to: {trace_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Workflow execution failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Workflow execution failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_execute())

@app.command("orchestrate")
def bpmn_orchestrate(
    ctx: typer.Context,
    test: bool = typer.Option(False, "--test", help="Run test orchestration"),
    production: bool = typer.Option(False, "--production", help="Run production orchestration"),
    workflows: List[str] = typer.Option([], "--workflow", "-w", help="Specific workflows to orchestrate"),
    parallel: bool = typer.Option(False, "--parallel", help="Run workflows in parallel")
):
    """Orchestrate multiple BPMN workflows"""
    
    async def run_orchestrate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        # Determine orchestration mode
        mode = "test" if test else "production" if production else "development"
        
        context = {
            "orchestration_mode": mode,
            "workflows": workflows or ["default"],
            "parallel_execution": parallel,
            "enable_monitoring": True,
            "cli_command": "bpmn orchestrate"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🎭 Orchestrating BPMN workflows...", total=None)
            
            try:
                result = await engine.execute_workflow("bpmn_orchestration", context)
                
                if result.success:
                    orchestration_result = result.final_data.get("orchestration_result", {})
                    progress.update(task, description="✅ Orchestration complete")
                    
                    display_orchestration_results(orchestration_result, mode)
                else:
                    progress.update(task, description="❌ Orchestration failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Orchestration failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_orchestrate())

@app.command("list")
def bpmn_list(
    ctx: typer.Context,
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed workflow information"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category")
):
    """List available BPMN workflows"""
    
    async def run_list():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "list_config": {
                "detailed": detailed,
                "category_filter": category,
                "include_metadata": True
            },
            "cli_command": "bpmn list"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📋 Loading BPMN workflows...", total=None)
            
            try:
                result = await engine.execute_workflow("list_workflows", context)
                
                if result.success:
                    workflows = result.final_data.get("workflows", [])
                    progress.update(task, description="✅ Workflows loaded")
                    
                    display_workflow_list(workflows, detailed)
                else:
                    progress.update(task, description="❌ Failed to load workflows")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Failed to load workflows")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_list())

@app.command("validate")
def bpmn_validate(
    ctx: typer.Context,
    workflow_file: Path = typer.Argument(help="BPMN workflow file to validate"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict validation"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues")
):
    """Validate BPMN workflow definitions"""
    
    async def run_validate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "workflow_file": str(workflow_file),
            "validation_config": {
                "strict_mode": strict,
                "auto_fix": fix,
                "check_syntax": True,
                "check_semantics": True,
                "check_executability": True
            },
            "cli_command": "bpmn validate"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Validating BPMN workflow...", total=None)
            
            try:
                result = await engine.execute_workflow("validate_bpmn", context)
                
                if result.success:
                    validation_result = result.final_data.get("validation_result", {})
                    progress.update(task, description="✅ Validation complete")
                    
                    display_bpmn_validation_results(validation_result, workflow_file)
                else:
                    progress.update(task, description="❌ Validation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Validation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_validate())

@app.command("monitor")
def bpmn_monitor(
    ctx: typer.Context,
    workflow_id: Optional[str] = typer.Option(None, "--workflow", "-w", help="Monitor specific workflow"),
    live: bool = typer.Option(False, "--live", help="Live monitoring mode"),
    metrics: bool = typer.Option(True, "--metrics/--no-metrics", help="Show performance metrics")
):
    """Monitor BPMN workflow execution"""
    
    async def run_monitor():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "monitor_config": {
                "workflow_id": workflow_id,
                "live_mode": live,
                "include_metrics": metrics,
                "include_traces": True
            },
            "cli_command": "bpmn monitor"
        }
        
        if live:
            console.print("[yellow]Live monitoring mode - Press Ctrl+C to exit[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📊 Monitoring workflows...", total=None)
            
            try:
                result = await engine.execute_workflow("monitor_workflows", context)
                
                if result.success:
                    monitoring_data = result.final_data.get("monitoring_data", {})
                    progress.update(task, description="✅ Monitoring data collected")
                    
                    display_monitoring_results(monitoring_data, metrics)
                else:
                    progress.update(task, description="❌ Monitoring failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Monitoring failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_monitor())

@app.command("visualize")
def bpmn_visualize(
    ctx: typer.Context,
    workflow_file: Optional[Path] = typer.Option(
        None,
        "--file", "-f",
        help="BPMN workflow file to visualize"
    ),
    style: str = typer.Option(
        "flow",
        "--style", "-s",
        help="Visualization style: flow, sequence, lifecycle"
    ),
    include_data: bool = typer.Option(
        False,
        "--data", "-d",
        help="Include data flow in visualization"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Visualize BPMN workflows as mermaid diagrams"""
    
    visualizer = MermaidVisualizer()
    lifecycle_gen = MermaidLifecycleGenerator()
    
    console.print(f"[bold]Generating {style} visualization...[/bold]")
    
    try:
        diagram = None
        
        if style == "flow":
            # Generate flow diagram
            workflow_data = {
                "tasks": [
                    {"name": "Initialize", "type": "service"},
                    {"name": "Validate Input", "type": "service"},
                    {"name": "Process Data", "type": "service"},
                    {"name": "Generate Output", "type": "service"},
                    {"name": "Review", "type": "user"}
                ],
                "gateways": [
                    {"type": "exclusive", "name": "Validation Check"},
                    {"type": "parallel", "name": "Multi-Processing"}
                ],
                "connections": [
                    {"from": "Start", "to": "T0"},
                    {"from": "T0", "to": "T1"},
                    {"from": "T1", "to": "G0"},
                    {"from": "G0", "to": "T2", "label": "Valid"},
                    {"from": "G0", "to": "End", "label": "Invalid"},
                    {"from": "T2", "to": "G1"},
                    {"from": "G1", "to": "T3"},
                    {"from": "T3", "to": "T4"},
                    {"from": "T4", "to": "End"}
                ]
            }
            
            if include_data:
                workflow_data["data_objects"] = [
                    {"name": "Input Data", "connections": ["T0", "T1"]},
                    {"name": "Processed Data", "connections": ["T2", "T3"]},
                    {"name": "Output Data", "connections": ["T3", "T4"]}
                ]
            
            diagram = visualizer.generate_workflow_visualization(workflow_data)
            
        elif style == "sequence":
            # Generate sequence diagram
            lines = ["sequenceDiagram"]
            lines.append("    participant User")
            lines.append("    participant Engine as BPMN Engine")
            lines.append("    participant Service as Service Tasks")
            lines.append("    participant Agents as AI Agents")
            
            lines.append("    User->>Engine: Start Workflow")
            lines.append("    Engine->>Service: Initialize")
            lines.append("    Service-->>Engine: Ready")
            lines.append("    Engine->>Service: Validate Input")
            lines.append("    Service->>Agents: Request Validation")
            lines.append("    Agents-->>Service: Validation Result")
            lines.append("    Service-->>Engine: Validation Complete")
            lines.append("    Engine->>Service: Process Data")
            lines.append("    Service-->>Engine: Processing Complete")
            lines.append("    Engine->>User: Workflow Complete")
            
            diagram = "\n".join(lines)
            
        elif style == "lifecycle":
            # Use lifecycle generator
            workflow_name = workflow_file.stem if workflow_file else "DefaultWorkflow"
            diagram = lifecycle_gen.generate_bpmn_lifecycle(workflow_name)
            
        else:
            console.print(f"[red]Unknown visualization style: {style}[/red]")
            raise typer.Exit(1)
        
        if diagram:
            # Display diagram
            console.print(Panel(
                Syntax(diagram, "mermaid", theme="monokai"),
                title=f"[bold cyan]BPMN {style.title()} Visualization[/bold cyan]"
            ))
            
            if output:
                output.write_text(f"```mermaid\n{diagram}\n```")
                console.print(f"[green]Diagram saved to: {output}[/green]")
                
    except Exception as e:
        console.print(f"[red]Error generating visualization: {e}[/red]")
        raise typer.Exit(1)

@app.command("debug")
def bpmn_debug(
    ctx: typer.Context,
    workflow: str = typer.Argument(help="Workflow to debug"),
    breakpoint: Optional[str] = typer.Option(None, "--breakpoint", "-b", help="Task ID for breakpoint"),
    step: bool = typer.Option(False, "--step", help="Enable step-by-step execution"),
    inspect_data: bool = typer.Option(True, "--data/--no-data", help="Inspect workflow data")
):
    """Debug BPMN workflow execution"""
    
    async def run_debug():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "workflow_name": workflow,
            "debug_config": {
                "breakpoint_task": breakpoint,
                "step_mode": step,
                "inspect_data": inspect_data,
                "capture_state": True
            },
            "cli_command": "bpmn debug"
        }
        
        console.print(Panel(
            f"[bold yellow]Debug Mode[/bold yellow]\n"
            f"Workflow: {workflow}\n"
            f"Breakpoint: {breakpoint or 'None'}\n"
            f"Step Mode: {'Enabled' if step else 'Disabled'}",
            title="Debug Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🐛 Debugging workflow...", total=None)
            
            try:
                result = await engine.execute_workflow("debug_workflow", context)
                
                if result.success:
                    debug_result = result.final_data.get("debug_result", {})
                    progress.update(task, description="✅ Debug session complete")
                    
                    display_debug_results(debug_result)
                else:
                    progress.update(task, description="❌ Debug session failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Debug session failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_debug())

# Display helper functions

def display_execution_results(result: Dict[str, Any], workflow: str):
    """Display workflow execution results"""
    duration = result.get("execution_time", 0)
    tasks_completed = result.get("tasks_completed", 0)
    status = result.get("status", "unknown")
    
    console.print(Panel(
        f"[bold]Workflow: {workflow}[/bold]\n"
        f"Status: {'✅ Success' if status == 'completed' else '❌ Failed'}\n"
        f"Duration: {duration:.2f}s\n"
        f"Tasks Completed: {tasks_completed}",
        title="Execution Summary"
    ))
    
    # Show task execution order
    task_order = result.get("task_execution_order", [])
    if task_order:
        console.print("\n[bold]Task Execution Order:[/bold]")
        for i, task in enumerate(task_order[:10], 1):
            console.print(f"  {i}. {task}")

def display_orchestration_results(result: Dict[str, Any], mode: str):
    """Display orchestration results"""
    table = Table(title=f"Orchestration Results ({mode} mode)")
    table.add_column("Workflow", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Duration", style="green")
    table.add_column("Tasks", style="yellow")
    
    workflows = result.get("workflow_results", [])
    for wf in workflows:
        status_icon = "✅" if wf["status"] == "completed" else "❌"
        table.add_row(
            wf["name"],
            f"{status_icon} {wf['status']}",
            f"{wf.get('duration', 0):.2f}s",
            str(wf.get('task_count', 0))
        )
    
    console.print(table)
    
    # Overall summary
    total_duration = result.get("total_duration", 0)
    success_rate = result.get("success_rate", 0)
    
    console.print(f"\n[bold]Total Duration:[/bold] {total_duration:.2f}s")
    console.print(f"[bold]Success Rate:[/bold] {success_rate:.1%}")

def display_workflow_list(workflows: List[Dict[str, Any]], detailed: bool):
    """Display list of available workflows"""
    if detailed:
        for workflow in workflows:
            tree = Tree(f"[bold cyan]{workflow['name']}[/bold cyan]")
            tree.add(f"Category: {workflow.get('category', 'uncategorized')}")
            tree.add(f"Description: {workflow.get('description', 'No description')}")
            tree.add(f"Tasks: {workflow.get('task_count', 0)}")
            tree.add(f"Version: {workflow.get('version', '1.0.0')}")
            
            if workflow.get('inputs'):
                inputs_branch = tree.add("Inputs:")
                for input_name in workflow['inputs']:
                    inputs_branch.add(input_name)
            
            console.print(tree)
            console.print("")
    else:
        table = Table(title="Available BPMN Workflows")
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Tasks", style="green")
        table.add_column("Version", style="yellow")
        
        for workflow in workflows:
            table.add_row(
                workflow['name'],
                workflow.get('category', 'uncategorized'),
                str(workflow.get('task_count', 0)),
                workflow.get('version', '1.0.0')
            )
        
        console.print(table)

def display_bpmn_validation_results(result: Dict[str, Any], workflow_file: Path):
    """Display BPMN validation results"""
    valid = result.get("valid", False)
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    
    console.print(Panel(
        f"[bold]{'✅ VALID' if valid else '❌ INVALID'}[/bold]\n"
        f"File: {workflow_file.name}\n"
        f"Errors: {len(errors)}\n"
        f"Warnings: {len(warnings)}",
        title="Validation Result"
    ))
    
    if errors:
        console.print("\n[red]Errors:[/red]")
        for error in errors[:5]:
            console.print(f"  ❌ {error['message']} (Line {error.get('line', '?')})")
    
    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings[:5]:
            console.print(f"  ⚠️  {warning['message']} (Line {warning.get('line', '?')})")

def display_monitoring_results(data: Dict[str, Any], show_metrics: bool):
    """Display workflow monitoring results"""
    active_workflows = data.get("active_workflows", [])
    
    if active_workflows:
        table = Table(title="Active Workflows")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Progress", style="green")
        table.add_column("Status", style="yellow")
        
        for wf in active_workflows:
            progress = wf.get("progress", 0)
            table.add_row(
                wf['id'][:8],
                wf['name'],
                f"{progress:.0%}",
                wf['status']
            )
        
        console.print(table)
    else:
        console.print("[yellow]No active workflows[/yellow]")
    
    if show_metrics:
        metrics = data.get("performance_metrics", {})
        if metrics:
            console.print("\n[bold]Performance Metrics:[/bold]")
            console.print(f"  Average Duration: {metrics.get('avg_duration', 0):.2f}s")
            console.print(f"  Success Rate: {metrics.get('success_rate', 0):.1%}")
            console.print(f"  Throughput: {metrics.get('throughput', 0):.1f} workflows/min")

def display_debug_results(result: Dict[str, Any]):
    """Display debug session results"""
    execution_path = result.get("execution_path", [])
    breakpoint_data = result.get("breakpoint_data", {})
    
    if execution_path:
        console.print("[bold]Execution Path:[/bold]")
        for i, step in enumerate(execution_path, 1):
            icon = "🔵" if step.get("current") else "✅"
            console.print(f"  {icon} {i}. {step['task_name']} ({step['status']})")
    
    if breakpoint_data:
        console.print(f"\n[bold]Breakpoint Data at {breakpoint_data.get('task_id')}:[/bold]")
        console.print_json(json.dumps(breakpoint_data.get('context', {}), indent=2))

@app.command("visualize")
def bpmn_visualize(
    ctx: typer.Context,
    workflow: str = typer.Argument(help="BPMN workflow to visualize"),
    style: str = typer.Option("flow", "--style", "-s", help="Visualization style: flow, sequence, lifecycle"),
    include_data: bool = typer.Option(False, "--data", help="Include data flow in visualization"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save diagram to file"),
    format: str = typer.Option("mermaid", "--format", help="Output format: mermaid, svg, png")
):
    """Generate visual representation of BPMN workflows"""
    
    visualizer = MermaidVisualizer()
    lifecycle_gen = MermaidLifecycleGenerator(visualizer)
    
    console.print(f"[bold cyan]📊 Visualizing workflow: {workflow}[/bold cyan]")
    
    try:
        diagram = ""
        
        if style == "flow":
            # Generate flow diagram
            workflow_data = {
                "tasks": [
                    {"name": "Load Semantic YAML", "type": "service"},
                    {"name": "Validate Schema", "type": "service"},
                    {"name": "Generate Code", "type": "service"},
                    {"name": "Create Agents", "type": "service"},
                    {"name": "Execute Runtime", "type": "service"}
                ],
                "gateways": [
                    {"type": "exclusive", "name": "Validation Check"}
                ],
                "connections": [
                    {"from": "Start", "to": "T0"},
                    {"from": "T0", "to": "T1"},
                    {"from": "T1", "to": "G0"},
                    {"from": "G0", "to": "T2", "label": "Valid"},
                    {"from": "G0", "to": "End", "label": "Invalid"},
                    {"from": "T2", "to": "T3"},
                    {"from": "T3", "to": "T4"},
                    {"from": "T4", "to": "End"}
                ]
            }
            diagram = visualizer.generate_workflow_visualization(workflow_data)
            
        elif style == "sequence":
            # Generate sequence diagram
            lines = ["sequenceDiagram"]
            lines.append("    participant User")
            lines.append("    participant Engine as BPMN Engine")
            lines.append("    participant Task as Service Tasks")
            lines.append("    participant OTel as OpenTelemetry")
            lines.append("")
            lines.append("    User->>Engine: Execute Workflow")
            lines.append("    Engine->>Task: Initialize Tasks")
            lines.append("    Task->>OTel: Start Span")
            lines.append("    Task->>Task: Execute Logic")
            lines.append("    Task->>OTel: End Span")
            lines.append("    Task-->>Engine: Task Complete")
            lines.append("    Engine-->>User: Workflow Result")
            
            diagram = "\n".join(lines)
            
        elif style == "lifecycle":
            # Use lifecycle generator
            diagram = lifecycle_gen.generate_bpmn_lifecycle(workflow)
            
        else:
            console.print(f"[red]Unknown style: {style}[/red]")
            console.print("[yellow]Valid styles: flow, sequence, lifecycle[/yellow]")
            raise typer.Exit(1)
        
        # Display the diagram
        if format == "mermaid":
            console.print("\n[bold]Mermaid Diagram:[/bold]")
            console.print("```mermaid")
            console.print(diagram)
            console.print("```")
            
            console.print("\n[dim]💡 Tip: Copy this diagram to any Mermaid viewer or Markdown file[/dim]")
        else:
            console.print(f"[yellow]Note: {format} format export not yet implemented[/yellow]")
        
        # Save to file if requested
        if output:
            output.write_text(diagram)
            console.print(f"[green]✅ Diagram saved to: {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error generating visualization: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()