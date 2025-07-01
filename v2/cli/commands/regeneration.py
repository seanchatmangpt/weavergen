"""
WeaverGen v2 Regeneration CLI Commands
DMEDI-based system regeneration with BPMN workflow orchestration
"""

import typer
import asyncio
import json
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

from ...core.engine.spiff_engine import WeaverGenV2Engine

app = typer.Typer(
    name="regeneration",
    help="DMEDI-based system regeneration commands",
    rich_markup_mode="rich"
)

console = Console()

@app.command("define")
def regeneration_define(
    ctx: typer.Context,
    system_id: str = typer.Argument(help="System identifier for regeneration"),
    components: List[str] = typer.Option([], "--component", "-c", help="System components"),
    dependencies: List[str] = typer.Option([], "--dependency", "-d", help="Critical dependencies"),
    output: str = typer.Option("regeneration_charter.json", "--output", "-o", help="Charter output file"),
    health_threshold: float = typer.Option(0.8, "--health-threshold", help="Minimum health score"),
    max_regen_time: int = typer.Option(600, "--max-time", help="Maximum regeneration time (seconds)")
):
    """DEFINE: Create regeneration charter for system"""
    
    async def run_define():
        engine = ctx.obj['engine']
        
        context = {
            "system_id": system_id,
            "system_definition": {
                "system_id": system_id,
                "components": components,
                "dependencies": dependencies
            },
            "charter_config": {
                "health_score_minimum": health_threshold,
                "max_regeneration_time": max_regen_time
            },
            "cli_command": "regeneration define"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔧 Defining regeneration charter...", total=None)
            
            try:
                result = await engine.execute_workflow("regeneration_define", context)
                
                if result.success:
                    charter_data = result.final_data["regeneration_charter"]
                    
                    # Save charter to file
                    with open(output, 'w') as f:
                        json.dump(charter_data, f, indent=2, default=str)
                    
                    progress.update(task, description="✅ Charter defined successfully")
                    
                    # Display charter summary
                    display_charter_summary(charter_data)
                    console.print(f"\n[green]Charter saved to: {output}[/green]")
                else:
                    progress.update(task, description="❌ Charter definition failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Charter definition failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_define())

@app.command("measure")
def regeneration_measure(
    ctx: typer.Context,
    system_id: str = typer.Argument(help="System identifier"),
    charter_file: str = typer.Option("regeneration_charter.json", "--charter", "-c", help="Charter file"),
    output_format: str = typer.Option("rich", "--format", help="Output format: rich, json, mermaid"),
    save_measurement: bool = typer.Option(True, "--save/--no-save", help="Save measurement to file")
):
    """MEASURE: Assess system entropy and regeneration needs"""
    
    async def run_measure():
        engine = ctx.obj['engine']
        
        # Load charter
        if not Path(charter_file).exists():
            console.print(f"[red]Charter file not found: {charter_file}[/red]")
            raise typer.Exit(1)
            
        with open(charter_file) as f:
            charter_data = json.load(f)
        
        context = {
            "system_id": system_id,
            "regeneration_charter": charter_data,
            "measurement_config": {
                "include_detailed_analysis": True,
                "capture_drift_indicators": True
            },
            "cli_command": "regeneration measure"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📊 Measuring system entropy...", total=None)
            
            try:
                result = await engine.execute_workflow("regeneration_measure", context)
                
                if result.success:
                    entropy_data = result.final_data["entropy_measurement"]
                    
                    progress.update(task, description="✅ Entropy measurement complete")
                    
                    # Display results based on format
                    if output_format == "rich":
                        display_entropy_results_rich(entropy_data)
                    elif output_format == "json":
                        console.print_json(json.dumps(entropy_data, indent=2, default=str))
                    elif output_format == "mermaid":
                        display_entropy_mermaid(entropy_data)
                    
                    # Save measurement
                    if save_measurement:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        measurement_file = f"entropy_measurement_{system_id}_{timestamp}.json"
                        with open(measurement_file, 'w') as f:
                            json.dump(entropy_data, f, indent=2, default=str)
                        console.print(f"\n[green]Measurement saved to: {measurement_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Entropy measurement failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Entropy measurement failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_measure())

@app.command("explore")
def regeneration_explore(
    ctx: typer.Context,
    system_id: str = typer.Argument(help="System identifier"),
    charter_file: str = typer.Option("regeneration_charter.json", "--charter", "-c", help="Charter file"),
    measurement_file: Optional[str] = typer.Option(None, "--measurement", "-m", help="Entropy measurement file"),
    max_options: int = typer.Option(5, "--max-options", help="Maximum options to generate"),
    save_options: bool = typer.Option(True, "--save/--no-save", help="Save options to file")
):
    """EXPLORE: Generate and evaluate regeneration options"""
    
    async def run_explore():
        engine = ctx.obj['engine']
        
        # Load charter
        if not Path(charter_file).exists():
            console.print(f"[red]Charter file not found: {charter_file}[/red]")
            raise typer.Exit(1)
            
        with open(charter_file) as f:
            charter_data = json.load(f)
        
        # Load or create measurement
        if measurement_file and Path(measurement_file).exists():
            with open(measurement_file) as f:
                measurement_data = json.load(f)
        else:
            # Trigger measurement first
            console.print("[yellow]No measurement file provided, measuring entropy first...[/yellow]")
            measurement_result = await engine.execute_workflow("regeneration_measure", {
                "system_id": system_id,
                "regeneration_charter": charter_data,
                "cli_command": "auto_measure"
            })
            measurement_data = measurement_result.final_data["entropy_measurement"]
        
        context = {
            "system_id": system_id,
            "regeneration_charter": charter_data,
            "entropy_measurement": measurement_data,
            "exploration_config": {
                "max_options": max_options,
                "include_risk_analysis": True,
                "include_resource_estimation": True
            },
            "cli_command": "regeneration explore"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Exploring regeneration options...", total=None)
            
            try:
                result = await engine.execute_workflow("regeneration_explore", context)
                
                if result.success:
                    options_data = result.final_data["regeneration_options"]
                    
                    progress.update(task, description="✅ Options exploration complete")
                    
                    # Display options
                    display_regeneration_options(options_data)
                    
                    # Save options
                    if save_options:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        options_file = f"regeneration_options_{system_id}_{timestamp}.json"
                        with open(options_file, 'w') as f:
                            json.dump(options_data, f, indent=2, default=str)
                        console.print(f"\n[green]Options saved to: {options_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Options exploration failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Options exploration failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_explore())

@app.command("execute")
def regeneration_execute(
    ctx: typer.Context,
    system_id: str = typer.Argument(help="System identifier"),
    strategy: str = typer.Option("auto", "--strategy", "-s", help="Regeneration strategy or 'auto'"),
    charter_file: str = typer.Option("regeneration_charter.json", "--charter", "-c"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without executing"),
    force: bool = typer.Option(False, "--force", help="Force regeneration even if not needed"),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm execution (required for actual execution)")
):
    """Execute complete DMEDI regeneration cycle"""
    
    if not dry_run and not confirm:
        console.print("[red]ERROR: Must use --confirm flag for actual regeneration execution[/red]")
        console.print("[yellow]Use --dry-run for simulation without changes[/yellow]")
        raise typer.Exit(1)
    
    async def run_execute():
        engine = ctx.obj['engine']
        
        # Load charter
        if not Path(charter_file).exists():
            console.print(f"[red]Charter file not found: {charter_file}[/red]")
            raise typer.Exit(1)
            
        with open(charter_file) as f:
            charter_data = json.load(f)
        
        context = {
            "system_id": system_id,
            "regeneration_charter": charter_data,
            "execution_config": {
                "strategy": strategy,
                "dry_run": dry_run,
                "force": force,
                "auto_retry": True,
                "max_retries": 2
            },
            "cli_command": "regeneration execute"
        }
        
        console.print(Panel(
            f"[bold blue]DMEDI Regeneration Execution[/bold blue]\n"
            f"System ID: {system_id}\n"
            f"Strategy: {strategy}\n"
            f"Dry Run: {dry_run}\n"
            f"Force: {force}",
            title="Execution Configuration"
        ))
        
        if not dry_run:
            console.print("[yellow]⚠️  This will execute actual system regeneration![/yellow]")
            if not typer.confirm("Continue with regeneration?"):
                console.print("[yellow]Regeneration cancelled by user[/yellow]")
                return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔄 Executing DMEDI regeneration cycle...", total=None)
            
            try:
                result = await engine.execute_workflow("complete_dmedi_cycle", context)
                
                if result.success:
                    regeneration_result = result.final_data["regeneration_result"]
                    
                    progress.update(task, description="✅ Regeneration cycle complete")
                    
                    # Display regeneration results
                    display_regeneration_results(regeneration_result)
                    
                    # Save execution result
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    result_file = f"regeneration_result_{system_id}_{timestamp}.json"
                    with open(result_file, 'w') as f:
                        json.dump(regeneration_result, f, indent=2, default=str)
                    console.print(f"\n[green]Execution result saved to: {result_file}[/green]")
                    
                else:
                    progress.update(task, description="❌ Regeneration cycle failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Regeneration cycle failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_execute())

@app.command("auto")
def regeneration_auto(
    ctx: typer.Context,
    system_id: str = typer.Argument(help="System identifier"),
    auto_confirm: bool = typer.Option(False, "--auto-confirm", help="Auto-confirm safe regenerations"),
    threshold: str = typer.Option("medium", "--threshold", help="Entropy threshold for auto-regeneration: low, medium, high"),
    schedule: Optional[str] = typer.Option(None, "--schedule", help="Schedule auto-regeneration (cron format)")
):
    """Execute automatic DMEDI regeneration cycle with intelligent decision making"""
    
    async def run_auto():
        engine = ctx.obj['engine']
        
        context = {
            "system_id": system_id,
            "auto_config": {
                "auto_confirm": auto_confirm,
                "entropy_threshold": threshold,
                "schedule": schedule,
                "intelligent_decision_making": True
            },
            "cli_command": "regeneration auto"
        }
        
        console.print(Panel(
            f"[bold blue]Automatic DMEDI Regeneration[/bold blue]\n"
            f"System ID: {system_id}\n"
            f"Auto-confirm: {auto_confirm}\n"
            f"Threshold: {threshold}\n"
            f"Schedule: {schedule or 'On-demand'}",
            title="Automatic Regeneration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🤖 Executing intelligent DMEDI cycle...", total=None)
            
            try:
                result = await engine.execute_workflow("intelligent_dmedi_cycle", context)
                
                if result.success:
                    auto_result = result.final_data["auto_regeneration_result"]
                    
                    progress.update(task, description="✅ Intelligent regeneration complete")
                    
                    display_auto_regeneration_results(auto_result)
                    
                else:
                    progress.update(task, description="❌ Intelligent regeneration failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Intelligent regeneration failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_auto())

@app.command("status")
def regeneration_status(
    ctx: typer.Context,
    system_id: str = typer.Argument(help="System identifier"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed status information")
):
    """Show current regeneration status and system health"""
    
    async def run_status():
        engine = ctx.obj['engine']
        
        context = {
            "system_id": system_id,
            "status_config": {
                "include_health_metrics": True,
                "include_entropy_trends": True,
                "include_recent_regenerations": True,
                "detailed": detailed
            },
            "cli_command": "regeneration status"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📊 Checking regeneration status...", total=None)
            
            try:
                result = await engine.execute_workflow("regeneration_status", context)
                
                if result.success:
                    status_data = result.final_data["regeneration_status"]
                    
                    progress.update(task, description="✅ Status check complete")
                    
                    display_regeneration_status(status_data, detailed)
                    
                else:
                    progress.update(task, description="❌ Status check failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Status check failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_status())

# Display functions

def display_charter_summary(charter_data):
    """Display regeneration charter summary"""
    table = Table(title="Regeneration Charter Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("System ID", charter_data["system_id"])
    table.add_row("Components", str(len(charter_data.get("system_components", []))))
    table.add_row("Dependencies", str(len(charter_data.get("critical_dependencies", []))))
    table.add_row("Health Threshold", f"{charter_data.get('health_score_minimum', 0.8):.2f}")
    table.add_row("Max Regen Time", f"{charter_data.get('max_regeneration_time', 600)}s")
    table.add_row("Entropy Levels", str(len(charter_data.get("entropy_thresholds", {}))))
    
    console.print(table)

def display_entropy_results_rich(entropy_data):
    """Display entropy measurement results with Rich formatting"""
    
    # Main entropy table
    table = Table(title="System Entropy Measurement")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Status", style="green")
    
    entropy_level = entropy_data.get("entropy_level", "unknown")
    status_icon = {
        "low": "🟢 HEALTHY",
        "medium": "🟡 ATTENTION",
        "high": "🟠 WARNING", 
        "critical": "🔴 CRITICAL"
    }.get(entropy_level, "❓ UNKNOWN")
    
    table.add_row("Entropy Level", entropy_level.upper(), status_icon)
    table.add_row("Entropy Score", f"{entropy_data.get('entropy_score', 0):.3f}", "")
    table.add_row("Health Score", f"{entropy_data.get('health_score', 0):.3f}", 
                  "✅ Good" if entropy_data.get('health_score', 0) > 0.8 else "⚠️ Poor")
    table.add_row("Validation Errors", str(entropy_data.get('validation_error_count', 0)),
                  "✅ None" if entropy_data.get('validation_error_count', 0) == 0 else "🚨 Present")
    table.add_row("Drift Indicators", str(len(entropy_data.get('semantic_drift_indicators', []))),
                  "✅ None" if len(entropy_data.get('semantic_drift_indicators', [])) == 0 else "🚨 Present")
    
    console.print(table)
    
    # Regeneration recommendation
    urgency = entropy_data.get('regeneration_urgency', 'none')
    if urgency != 'none':
        urgency_color = {
            'scheduled': 'yellow',
            'immediate': 'orange',
            'emergency': 'red'
        }.get(urgency, 'white')
        
        console.print(Panel(
            f"[{urgency_color}]Regeneration Urgency: {urgency.upper()}[/{urgency_color}]",
            title="Recommendation"
        ))

def display_entropy_mermaid(entropy_data):
    """Display entropy measurement as Mermaid diagram"""
    entropy_level = entropy_data.get("entropy_level", "unknown")
    health_score = entropy_data.get("health_score", 0)
    
    mermaid_lines = [
        "graph TD",
        f'    A[System: {entropy_data.get("system_id", "unknown")}]',
        f'    B[Entropy: {entropy_level.upper()}]',
        f'    C[Health: {health_score:.2f}]',
        "    A --> B",
        "    A --> C"
    ]
    
    # Add drift indicators
    drift_indicators = entropy_data.get('semantic_drift_indicators', [])
    for i, indicator in enumerate(drift_indicators[:3]):  # Show first 3
        mermaid_lines.append(f'    D{i}[{indicator}]')
        mermaid_lines.append(f'    B --> D{i}')
    
    console.print("```mermaid")
    console.print("\n".join(mermaid_lines))
    console.print("```")

def display_regeneration_options(options_data):
    """Display regeneration options table"""
    table = Table(title="Regeneration Options")
    table.add_column("Option", style="cyan")
    table.add_column("Strategy", style="magenta")
    table.add_column("Success Probability", style="green")
    table.add_column("Duration", style="yellow")
    table.add_column("Risk", style="red")
    table.add_column("Health Improvement", style="blue")
    
    for i, option in enumerate(options_data[:5]):  # Show top 5
        table.add_row(
            f"Option {i+1}",
            option.get("strategy_name", "Unknown"),
            f"{option.get('success_probability', 0):.1%}",
            f"{option.get('estimated_duration', 0)}s",
            option.get('estimated_risk', 'unknown'),
            f"{option.get('expected_health_improvement', 0):.1%}"
        )
    
    console.print(table)

def display_regeneration_results(result_data):
    """Display regeneration execution results"""
    success = result_data.get('success', False)
    title_color = "green" if success else "red"
    status = "SUCCESS" if success else "FAILED"
    
    console.print(Panel(
        f"[bold {title_color}]Regeneration {status}[/bold {title_color}]\n"
        f"Execution Time: {result_data.get('execution_time', 0):.1f}s\n"
        f"Health Improvement: {result_data.get('health_improvement', 0):.2%}\n"
        f"Entropy Reduction: {result_data.get('entropy_reduction', 0):.2%}",
        title="DMEDI Execution Result"
    ))

def display_auto_regeneration_results(result_data):
    """Display automatic regeneration results"""
    decision = result_data.get('decision', 'unknown')
    action_taken = result_data.get('action_taken', 'none')
    
    console.print(Panel(
        f"[bold blue]Intelligent Decision: {decision.upper()}[/bold blue]\n"
        f"Action Taken: {action_taken}\n"
        f"Reasoning: {result_data.get('reasoning', 'N/A')}",
        title="Automatic Regeneration Result"
    ))

def display_regeneration_status(status_data, detailed=False):
    """Display current regeneration status"""
    table = Table(title="Regeneration System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Last Check", style="yellow")
    
    components = status_data.get('components', {})
    for component, info in components.items():
        status_icon = "✅" if info.get('healthy', False) else "❌"
        table.add_row(
            component,
            f"{status_icon} {info.get('status', 'unknown')}",
            info.get('last_check', 'never')
        )
    
    console.print(table)
    
    if detailed:
        # Show recent regenerations
        recent = status_data.get('recent_regenerations', [])
        if recent:
            console.print("\n[bold]Recent Regenerations:[/bold]")
            for regen in recent[:5]:
                success_icon = "✅" if regen.get('success', False) else "❌"
                console.print(f"  {success_icon} {regen.get('timestamp', 'unknown')} - {regen.get('strategy', 'unknown')}")

if __name__ == "__main__":
    app()