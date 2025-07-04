"""WeaverGen v2 CLI with BPMN workflow support."""

import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

import typer
import yaml
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .cli_debug import debug_app
from .cli_workflow import workflow_app
from .commands.bpmn import bpmn_app
from .commands.context import context_app
from .commands.mining import mining_app
from .commands.semantic import semantic_app
from .commands.templates import templates_app
from .commands.weaver import weaver_app
from .commands.xes import xes_app
from .engine.service_task import WeaverGenServiceEnvironment
from .engine.simple_engine import SimpleBpmnEngine

app = typer.Typer(help="WeaverGen v2 - BPMN-driven semantic code generation")
console = Console()

# Enable span capture at the very beginning of the CLI execution
from .cli_debug import enable_span_capture
enable_span_capture()

# Enable span capture at the very beginning of the CLI execution
from .cli_debug import enable_span_capture
enable_span_capture()

# Add subcommands
app.add_typer(workflow_app, name="workflow", help="Manage BPMN workflows")
app.add_typer(debug_app, name="debug", help="Debug and visualize OpenTelemetry spans")
app.add_typer(weaver_app, name="weaver", help="Direct Weaver binary commands")
app.add_typer(bpmn_app, name="bpmn", help="BPMN workflow execution")
app.add_typer(templates_app, name="templates", help="Template management")
app.add_typer(semantic_app, name="semantic", help="AI-powered semantic generation")
app.add_typer(mining_app, name="mining", help="Process mining and XES conversion")
app.add_typer(xes_app, name="xes", help="Process mining and XES operations")
app.add_typer(context_app, name="context", help="Gather context for AI models")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components (singleton pattern for demo)
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        script_env = WeaverGenServiceEnvironment()
        _engine = SimpleBpmnEngine(script_env)
    return _engine

engine = get_engine()


@app.command()
def add(
    process_id: str | None = typer.Option(None, "--process", "-p", help="The top-level BPMN Process ID"),
    collaboration_id: str | None = typer.Option(None, "--collaboration", "-c", help="The ID of the collaboration"),
    bpmn_files: list[str] = typer.Option([], "--bpmn", "-b", help="BPMN files to load"),
    dmn_files: list[str] = typer.Option([], "--dmn", "-d", help="DMN files to load"),
):
    """Add a workflow specification."""
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("add", {"process_id": process_id, "collaboration_id": collaboration_id, "bpmn_files": bpmn_files, "dmn_files": dmn_files}):
        if not process_id and not collaboration_id:
            console.print("[red]Error: Either --process or --collaboration must be specified[/red]")
            raise typer.Exit(1)

        if process_id and collaboration_id:
            console.print("[red]Error: Only one of --process or --collaboration can be specified[/red]")
            raise typer.Exit(1)

        try:
            if process_id:
                spec_id = engine.add_spec(process_id, bpmn_files)
                console.print(f"[green]Added process '{process_id}' with ID: {spec_id}[/green]")
            else:
                # For now, treat collaboration as process
                spec_id = engine.add_spec(collaboration_id, bpmn_files)
                console.print(f"[green]Added collaboration '{collaboration_id}' with ID: {spec_id}[/green]")
        except Exception as e:
            console.print(f"[red]Error adding workflow: {e}[/red]")
            raise typer.Exit(1) from e


@app.command()
def list_specs():
    """List available workflow specifications."""
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("list_specs", {}):
        specs = engine.list_specs()

        if not specs:
            console.print("[yellow]No workflow specifications found[/yellow]")
            return

        table = Table(title="Workflow Specifications")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("File", style="green")

        for spec_id, name, filename in specs:
            table.add_row(spec_id, name, filename)

        console.print(table)


@app.command()
def list_instances(include_completed: bool = typer.Option(False, "--all", "-a", help="Include completed workflows")):
    """List workflow instances."""
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("list_instances", {"include_completed": include_completed}):
        workflows = engine.list_workflows(include_completed)

        if not workflows:
            console.print("[yellow]No workflow instances found[/yellow]")
            return

        table = Table(title="Workflow Instances")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Active", style="green")
        table.add_column("Started", style="blue")
        table.add_column("Updated", style="blue")

        for wf_id, name, _filename, active, started, updated in workflows:
            table.add_row(
                wf_id,
                name,
                "✓" if active else "✗",
                started,
                updated or ""
            )

        console.print(table)


@app.command()
def run(
    spec_id: str = typer.Argument(help="The ID of the specification to run"),
    data: str | None = typer.Option(None, "--data", "-d", help="Initial workflow data as JSON"),
):
    """Run a workflow to completion."""
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("run", {"spec_id": spec_id, "data": data}):
        try:
            # Start the workflow
            instance = engine.start_workflow(spec_id)

            # Set initial data if provided
            if data:
                initial_data = json.loads(data)
                instance.workflow.data.update(initial_data)

            # Run until completion or user input required
            instance.run_until_user_input_required()
            instance.save()

            # Display results
            if instance.workflow.is_completed():
                console.print("[green]Workflow completed successfully![/green]")
            else:
                console.print("[yellow]Workflow paused - user input required[/yellow]")

            # Show workflow data
            console.print("\n[bold]Workflow Data:[/bold]")
            console.print(json.dumps(instance.data, indent=2))

        except Exception as e:
            console.print(f"[red]Error running workflow: {e}[/red]")
            raise typer.Exit(1) from e


@app.command()
def delete_spec(
    spec_id: str = typer.Argument(help="The ID of the specification to delete"),
):
    """Delete a workflow specification."""
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("delete_spec", {"spec_id": spec_id}):
        try:
            engine.delete_workflow_spec(spec_id)
            console.print(f"[green]Deleted workflow specification: {spec_id}[/green]")
        except Exception as e:
            console.print(f"[red]Error deleting specification: {e}[/red]")
            raise typer.Exit(1) from e


@app.command()
def delete_instance(
    wf_id: str = typer.Argument(help="The ID of the workflow instance to delete"),
):
    """Delete a workflow instance."""
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("delete_instance", {"wf_id": wf_id}):
        try:
            engine.delete_workflow(wf_id)
            console.print(f"[green]Deleted workflow instance: {wf_id}[/green]")
        except Exception as e:
            console.print(f"[red]Error deleting workflow: {e}[/red]")
            raise typer.Exit(1) from e


class PythonGenerator:
    def __init__(self, config_path: Path = None, output_dir: Path = Path(".")):
        # Load embedded default if none provided
        if config_path is None:
            pkg_dir = Path(__file__).parent
            config_path = pkg_dir / "resources" / "templates" / "python" / "default-forge.yaml"
        self.config_path = config_path
        self.config = yaml.safe_load(config_path.read_text())
        self.output_dir = output_dir

    def run():
        # Invoke the Rust CLI under the hood
        subprocess.check_call([
            "weaver", "registry", "generate", "python",
            "--config", str(self.config_path),
            "--output", str(self.output_dir),
        ])


@app.command()
def generate(
    config: Path = typer.Option(
        None,
        "--config",
        "-c",
        exists=True,
        help="Path to your weaver-forge.yaml (falls back to embedded default)"
    ),
    template: Path = typer.Option(
        ...,
        "--template",
        "-t",
        exists=True,
        help="Path to the Jinja2 template file to use for generation"
    ),
    output: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory for generated code"
    ),
):
    """
    Generate code using Weaver Forge with a specified template and output directory.
    """
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("generate", {"config": str(config) if config else None, "template": str(template) if template else None, "output": str(output)}):
        # Locate the Weaver Rust binary
        weaver_bin = shutil.which("weaver")
        if not weaver_bin:
            typer.secho("Could not find `weaver` binary in PATH.", fg="red")
            raise typer.Exit(1)

        # Determine config path
        if not config:
            # Copy embedded default to cwd
            default_cfg = Path(__file__).parent / "resources" / "templates" / "python" / "default-forge.yaml"
            config = Path.cwd() / "weaver-forge.yaml"
            config.write_text(default_cfg.read_text())
            typer.secho("Initialized default weaver-forge.yaml", fg="green")

        # Delegate to Rust CLI
        cmd = [weaver_bin, "registry", "generate", "--config", str(config)]
        
        # --templates should point to the directory containing the template file
        cmd.extend(["--templates", str(template.parent)])
        # The target is the name of the template file without the .j2 extension
        target_name = template.name.replace(".j2", "")
        cmd.extend([target_name, str(output)])
        
        typer.secho(f"Running: {' '.join(cmd)}", fg="cyan")
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)

@app.command()
def api(
    config: Path = typer.Argument(
        None,
        help="Path to your weaver-forge.yaml (embedded default if omitted)"
    ),
    out_dir: Path = typer.Option(".", "--out", "-o", help="Directory to generate into"),
):
    """
    Programmatic API: Generate code without shelling out.
    """
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("api", {"config": str(config) if config else None, "out_dir": str(out_dir)}):
        gen = PythonGenerator(config_path=config, output_dir=out_dir)
        gen.run()
        typer.secho(f"Code generated under {out_dir}", fg="green")


@app.command()
def fire(name: str = "Chell") -> None:
    """Fire portal gun (legacy command)."""
    from .enhanced_instrumentation import cli_command_span
    with cli_command_span("fire", {"name": name}):
        rprint(f"[bold red]Alert![/bold red] {name} fired [green]portal gun[/green] :boom:")



@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """WeaverGen v2 - BPMN-driven semantic code generation."""
    if version:
        console.print("[cyan]WeaverGen v2.0.0[/cyan]")
        raise typer.Exit(0)
