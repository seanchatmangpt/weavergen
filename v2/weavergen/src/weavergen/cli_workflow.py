"""Workflow subcommand for WeaverGen v2 with span support."""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.syntax import Syntax

from .engine.simple_engine import SimpleBpmnEngine
from .engine.service_task import WeaverGenServiceEnvironment
from .enhanced_instrumentation import cli_command_span, add_span_event

# Create workflow subcommand app
workflow_app = typer.Typer(help="Manage BPMN workflows")
console = Console()

# Initialize engine (singleton pattern for demo)
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        script_env = WeaverGenServiceEnvironment()
        _engine = SimpleBpmnEngine(script_env)
    return _engine


@workflow_app.command("add")
def add_workflow(
    process_id: str = typer.Argument(help="The BPMN Process ID"),
    bpmn_files: List[str] = typer.Option(..., "--bpmn", "-b", help="BPMN files to load"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Display name for the workflow"),
):
    """Add a new workflow specification from BPMN files."""
    with cli_command_span("workflow.add", {
        "process_id": process_id,
        "bpmn_files": ",".join(bpmn_files),
        "name": name
    }) as span:
        engine = get_engine()
        
        try:
            add_span_event("add_workflow.start", {"process_id": process_id})
            
            spec_id = engine.add_spec(process_id, bpmn_files)
            console.print(f"[green]✓[/green] Added workflow '{process_id}' with ID: {spec_id}")
            
            span.set_attribute("spec_id", spec_id)
            span.set_attribute("bpmn_file_count", len(bpmn_files))
            
            # Show workflow info
            panel = Panel(
                f"[bold]Process ID:[/bold] {process_id}\n"
                f"[bold]Spec ID:[/bold] {spec_id}\n"
                f"[bold]BPMN Files:[/bold] {', '.join(bpmn_files)}\n"
                f"[bold]Name:[/bold] {name or process_id}",
                title="[cyan]Workflow Added[/cyan]",
                border_style="cyan"
            )
            console.print(panel)
            
            add_span_event("add_workflow.complete", {"spec_id": spec_id})
            
        except Exception as e:
            console.print(f"[red]✗ Error adding workflow:[/red] {e}")
            raise typer.Exit(1)


@workflow_app.command("list")
def list_workflows(
    show_instances: bool = typer.Option(False, "--instances", "-i", help="Also show workflow instances"),
):
    """List all workflow specifications and optionally their instances."""
    engine = get_engine()
    
    # List specifications
    specs = engine.list_specs()
    if not specs:
        console.print("[yellow]No workflow specifications found[/yellow]")
    else:
        spec_table = Table(title="[bold cyan]Workflow Specifications[/bold cyan]")
        spec_table.add_column("ID", style="cyan", no_wrap=True)
        spec_table.add_column("Name", style="magenta")
        spec_table.add_column("File", style="green")
        
        for spec_id, name, filename in specs:
            spec_table.add_row(spec_id, name, filename)
        
        console.print(spec_table)
    
    # List instances if requested
    if show_instances:
        console.print()  # Add spacing
        instances = engine.list_workflows(include_completed=True)
        
        if not instances:
            console.print("[yellow]No workflow instances found[/yellow]")
        else:
            instance_table = Table(title="[bold cyan]Workflow Instances[/bold cyan]")
            instance_table.add_column("ID", style="cyan", no_wrap=True)
            instance_table.add_column("Spec", style="magenta")
            instance_table.add_column("Status", style="green")
            instance_table.add_column("Started", style="blue")
            
            for wf_id, name, _, active, started, _ in instances:
                status = "[green]Active[/green]" if active else "[red]Completed[/red]"
                instance_table.add_row(wf_id, name, status, started)
            
            console.print(instance_table)


@workflow_app.command("run")
def run_workflow(
    spec_id: str = typer.Argument(help="The workflow specification ID to run"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Initial workflow data as JSON"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Run in interactive mode"),
    show_trace: bool = typer.Option(False, "--trace", "-t", help="Show execution trace"),
):
    """Execute a workflow specification."""
    with cli_command_span("workflow.run", {
        "spec_id": spec_id,
        "interactive": interactive,
        "show_trace": show_trace,
        "has_data": data is not None
    }) as span:
        engine = get_engine()
        
        try:
            # Start the workflow
            console.print(f"[cyan]Starting workflow '{spec_id}'...[/cyan]")
            add_span_event("workflow.start", {"spec_id": spec_id})
            
            instance = engine.start_workflow(spec_id)
            span.set_attribute("instance_id", instance.wf_id)
            
            # Set initial data if provided
            if data:
                initial_data = json.loads(data)
                instance.workflow.data.update(initial_data)
                console.print(f"[green]✓[/green] Initial data loaded")
                span.set_attribute("initial_data_size", len(data))
                add_span_event("workflow.data_loaded", {"data_keys": list(initial_data.keys())})
            
            # Run the workflow
            if show_trace:
                console.print("\n[bold]Execution Trace:[/bold]")
            
            add_span_event("workflow.execution_start")
            instance.run_until_user_input_required()
            instance.save()
            add_span_event("workflow.execution_complete")
            
            # Track completion status
            is_completed = instance.workflow.is_completed()
            span.set_attribute("workflow.completed", is_completed)
            span.set_attribute("workflow.task_count", len(instance.workflow.get_tasks()))
            
            # Show results
            if is_completed:
                console.print(f"\n[green]✓ Workflow completed successfully![/green]")
                add_span_event("workflow.completed")
            else:
                console.print(f"\n[yellow]⚠ Workflow paused - user input required[/yellow]")
                
                # Show waiting tasks
                waiting_tasks = [t for t in instance.workflow.get_tasks() if t.state.is_waiting()]
                span.set_attribute("workflow.waiting_tasks", len(waiting_tasks))
                
                if waiting_tasks:
                    console.print("\n[bold]Waiting Tasks:[/bold]")
                    for task in waiting_tasks:
                        console.print(f"  • {task.task_spec.name} ({task.id})")
                    
                    add_span_event("workflow.paused", {
                        "waiting_task_names": [t.task_spec.name for t in waiting_tasks]
                    })
            
            # Show workflow data
            console.print("\n[bold]Workflow Data:[/bold]")
            workflow_data = instance.data
            span.set_attribute("workflow.data_size", len(json.dumps(workflow_data)))
            
            syntax = Syntax(json.dumps(workflow_data, indent=2), "json", theme="monokai")
            console.print(syntax)
            
            # Return the instance ID
            console.print(f"\n[dim]Instance ID: {instance.wf_id}[/dim]")
            
        except Exception as e:
            console.print(f"[red]✗ Error running workflow:[/red] {e}")
            raise typer.Exit(1)


@workflow_app.command("show")
def show_workflow(
    spec_id: str = typer.Argument(help="The workflow specification ID to inspect"),
    format: str = typer.Option("tree", "--format", "-f", help="Output format: tree, json, bpmn"),
):
    """Show detailed information about a workflow specification."""
    engine = get_engine()
    
    # Check if spec exists
    specs = dict((s[0], s) for s in engine.list_specs())
    if spec_id not in specs:
        console.print(f"[red]✗ Workflow specification '{spec_id}' not found[/red]")
        raise typer.Exit(1)
    
    spec_info = specs[spec_id]
    spec = engine.specs[spec_id]
    
    if format == "tree":
        # Display as tree
        tree = Tree(f"[bold cyan]{spec_id}[/bold cyan] ({spec.name})")
        
        # Add spec info
        info_branch = tree.add("[yellow]Specification Info[/yellow]")
        info_branch.add(f"Name: {spec.name}")
        info_branch.add(f"ID: {spec_id}")
        info_branch.add(f"File: {spec_info[2]}")
        
        # Add task specs
        tasks_branch = tree.add("[yellow]Tasks[/yellow]")
        for task_name, task_spec in spec.task_specs.items():
            task_node = tasks_branch.add(f"{task_name} ({task_spec.__class__.__name__})")
            if hasattr(task_spec, 'outputs') and task_spec.outputs:
                for output in task_spec.outputs:
                    task_node.add(f"→ {output}")
        
        console.print(tree)
        
    elif format == "json":
        # Export as JSON
        spec_data = {
            "id": spec_id,
            "name": spec.name,
            "tasks": {
                name: {
                    "type": task.__class__.__name__,
                    "outputs": getattr(task, 'outputs', [])
                }
                for name, task in spec.task_specs.items()
            }
        }
        syntax = Syntax(json.dumps(spec_data, indent=2), "json", theme="monokai")
        console.print(syntax)
        
    elif format == "bpmn":
        # Show original BPMN (simplified)
        console.print(f"[yellow]BPMN format not yet implemented[/yellow]")
    else:
        console.print(f"[red]✗ Unknown format: {format}[/red]")
        raise typer.Exit(1)


@workflow_app.command("status")
def workflow_status(
    instance_id: str = typer.Argument(help="The workflow instance ID"),
    show_data: bool = typer.Option(False, "--data", "-d", help="Show workflow data"),
):
    """Check the status of a workflow instance."""
    engine = get_engine()
    
    try:
        instance = engine.get_workflow(instance_id)
        workflow = instance.workflow
        
        # Create status panel
        status = "Completed" if workflow.is_completed() else "Active"
        status_color = "green" if workflow.is_completed() else "yellow"
        
        status_info = f"""[bold]Instance ID:[/bold] {instance_id}
[bold]Specification:[/bold] {workflow.spec.name}
[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]
[bold]Tasks:[/bold] {len(workflow.get_tasks())} total"""
        
        panel = Panel(
            status_info,
            title=f"[cyan]Workflow Status[/cyan]",
            border_style="cyan"
        )
        console.print(panel)
        
        # Show task states
        console.print("\n[bold]Task States:[/bold]")
        task_table = Table()
        task_table.add_column("Task", style="cyan")
        task_table.add_column("Type", style="magenta")
        task_table.add_column("State", style="green")
        
        for task in workflow.get_tasks():
            state_str = task.state.name
            if task.state.is_completed():
                state_str = f"[green]{state_str}[/green]"
            elif task.state.is_waiting():
                state_str = f"[yellow]{state_str}[/yellow]"
            else:
                state_str = f"[blue]{state_str}[/blue]"
            
            task_table.add_row(
                task.task_spec.name,
                task.task_spec.__class__.__name__,
                state_str
            )
        
        console.print(task_table)
        
        # Show data if requested
        if show_data:
            console.print("\n[bold]Workflow Data:[/bold]")
            syntax = Syntax(json.dumps(instance.data, indent=2), "json", theme="monokai")
            console.print(syntax)
            
    except Exception as e:
        console.print(f"[red]✗ Error getting workflow status:[/red] {e}")
        raise typer.Exit(1)


@workflow_app.command("delete")
def delete_workflow(
    id: str = typer.Argument(help="The workflow specification or instance ID to delete"),
    instance: bool = typer.Option(False, "--instance", "-i", help="Delete a workflow instance instead of specification"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a workflow specification or instance."""
    engine = get_engine()
    
    # Confirm deletion
    if not force:
        item_type = "instance" if instance else "specification"
        confirm = typer.confirm(f"Are you sure you want to delete {item_type} '{id}'?")
        if not confirm:
            console.print("[yellow]Deletion cancelled[/yellow]")
            raise typer.Exit(0)
    
    try:
        if instance:
            engine.delete_workflow(id)
            console.print(f"[green]✓[/green] Deleted workflow instance: {id}")
        else:
            engine.delete_workflow_spec(id)
            console.print(f"[green]✓[/green] Deleted workflow specification: {id}")
    except Exception as e:
        console.print(f"[red]✗ Error deleting workflow:[/red] {e}")
        raise typer.Exit(1)


@workflow_app.command("export")
def export_workflow(
    spec_id: str = typer.Argument(help="The workflow specification ID to export"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format: json, yaml"),
):
    """Export a workflow specification."""
    engine = get_engine()
    
    # Check if spec exists
    if spec_id not in engine.specs:
        console.print(f"[red]✗ Workflow specification '{spec_id}' not found[/red]")
        raise typer.Exit(1)
    
    spec = engine.specs[spec_id]
    
    # Create export data
    export_data = {
        "id": spec_id,
        "name": spec.name,
        "exported_at": datetime.now().isoformat(),
        "tasks": {
            name: {
                "type": task.__class__.__name__,
                "class": f"{task.__class__.__module__}.{task.__class__.__name__}",
                "outputs": getattr(task, 'outputs', []),
                "inputs": getattr(task, 'inputs', [])
            }
            for name, task in spec.task_specs.items()
        }
    }
    
    # Format output
    if format == "json":
        output_str = json.dumps(export_data, indent=2)
    elif format == "yaml":
        # Simple YAML-like format
        output_str = f"id: {export_data['id']}\n"
        output_str += f"name: {export_data['name']}\n"
        output_str += f"exported_at: {export_data['exported_at']}\n"
        output_str += "tasks:\n"
        for task_name, task_info in export_data['tasks'].items():
            output_str += f"  {task_name}:\n"
            output_str += f"    type: {task_info['type']}\n"
    else:
        console.print(f"[red]✗ Unknown format: {format}[/red]")
        raise typer.Exit(1)
    
    # Write output
    if output:
        output_path = Path(output)
        output_path.write_text(output_str)
        console.print(f"[green]✓[/green] Exported workflow to: {output}")
    else:
        # Print to console
        syntax = Syntax(output_str, format, theme="monokai")
        console.print(syntax)


@workflow_app.command("validate")
def validate_workflow(
    bpmn_file: str = typer.Argument(help="The BPMN file to validate"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Enable strict validation"),
):
    """Validate a BPMN file without adding it."""
    try:
        # Try to parse the file
        from SpiffWorkflow.bpmn.parser import BpmnParser
        parser = BpmnParser()
        parser.add_bpmn_file(bpmn_file)
        
        # Get all process IDs
        process_ids = list(parser.process_parsers.keys())
        
        console.print(f"[green]✓[/green] BPMN file is valid!")
        console.print(f"\n[bold]Found {len(process_ids)} process(es):[/bold]")
        for pid in process_ids:
            console.print(f"  • {pid}")
            
    except Exception as e:
        console.print(f"[red]✗ Validation failed:[/red] {e}")
        raise typer.Exit(1)