"""
WeaverGen v2 Process Mining Commands
Process mining and XES conversion functionality
"""

import typer
import asyncio
import json
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from ...core.engine.spiff_engine import WeaverGenV2Engine

app = typer.Typer(
    name="mining",
    help="Process mining and XES conversion tools",
    rich_markup_mode="rich"
)

console = Console()

@app.command("convert")
def mining_convert(
    ctx: typer.Context,
    input_file: Path = typer.Argument(help="Input file to convert"),
    output_format: str = typer.Option("xes", "--format", "-f", help="Output format: xes, csv, json"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    include_metadata: bool = typer.Option(True, "--metadata/--no-metadata", help="Include metadata")
):
    """Convert logs to XES format for process mining"""
    
    async def run_convert():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        if not input_file.exists():
            console.print(f"[red]Input file not found: {input_file}[/red]")
            raise typer.Exit(1)
        
        output_path = output_file or input_file.with_suffix(f".{output_format}")
        
        context = {
            "input_file": str(input_file),
            "conversion_config": {
                "output_format": output_format,
                "output_file": str(output_path),
                "include_metadata": include_metadata,
                "preserve_attributes": True
            },
            "cli_command": "mining convert"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🔄 Converting to {output_format.upper()}...", total=None)
            
            try:
                result = await engine.execute_workflow("convert_to_xes", context)
                
                if result.success:
                    conversion_result = result.final_data.get("conversion_result", {})
                    progress.update(task, description="✅ Conversion complete")
                    
                    display_conversion_results(conversion_result, output_path)
                else:
                    progress.update(task, description="❌ Conversion failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Conversion failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_convert())

@app.command("discover")
def mining_discover(
    ctx: typer.Context,
    log_file: Path = typer.Argument(help="Process log file (XES format)"),
    algorithm: str = typer.Option("alpha", "--algorithm", "-a", help="Discovery algorithm: alpha, heuristic, inductive"),
    output_format: str = typer.Option("bpmn", "--format", "-f", help="Output format: bpmn, petri, graph"),
    threshold: float = typer.Option(0.8, "--threshold", "-t", help="Discovery threshold")
):
    """Discover process models from event logs"""
    
    async def run_discover():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "log_file": str(log_file),
            "discovery_config": {
                "algorithm": algorithm,
                "output_format": output_format,
                "threshold": threshold,
                "filter_noise": True,
                "simplify_model": True
            },
            "cli_command": "mining discover"
        }
        
        console.print(Panel(
            f"[bold blue]Process Discovery[/bold blue]\n"
            f"Algorithm: {algorithm}\n"
            f"Output: {output_format}\n"
            f"Threshold: {threshold:.1%}",
            title="Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("⛏️ Discovering process model...", total=None)
            
            try:
                result = await engine.execute_workflow("discover_process", context)
                
                if result.success:
                    discovery_result = result.final_data.get("discovery_result", {})
                    progress.update(task, description="✅ Discovery complete")
                    
                    display_discovery_results(discovery_result, algorithm)
                else:
                    progress.update(task, description="❌ Discovery failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Discovery failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_discover())

@app.command("analyze")
def mining_analyze(
    ctx: typer.Context,
    log_file: Path = typer.Argument(help="Process log file to analyze"),
    metrics: List[str] = typer.Option(["duration", "frequency"], "--metric", "-m", help="Metrics to calculate"),
    group_by: Optional[str] = typer.Option(None, "--group-by", "-g", help="Group analysis by: resource, activity, time"),
    export_stats: bool = typer.Option(False, "--export", help="Export statistics")
):
    """Analyze process logs for insights"""
    
    async def run_analyze():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "log_file": str(log_file),
            "analysis_config": {
                "metrics": metrics,
                "group_by": group_by,
                "calculate_variants": True,
                "identify_bottlenecks": True,
                "detect_anomalies": True
            },
            "cli_command": "mining analyze"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📊 Analyzing process logs...", total=None)
            
            try:
                result = await engine.execute_workflow("analyze_process_logs", context)
                
                if result.success:
                    analysis_result = result.final_data.get("analysis_result", {})
                    progress.update(task, description="✅ Analysis complete")
                    
                    display_process_analysis(analysis_result, metrics)
                    
                    if export_stats:
                        stats_file = log_file.with_suffix(".stats.json")
                        with open(stats_file, 'w') as f:
                            json.dump(analysis_result, f, indent=2, default=str)
                        console.print(f"[green]Statistics exported to: {stats_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Analysis failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Analysis failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_analyze())

@app.command("conformance")
def mining_conformance(
    ctx: typer.Context,
    log_file: Path = typer.Argument(help="Process log file"),
    model_file: Path = typer.Argument(help="Process model file (BPMN/Petri net)"),
    technique: str = typer.Option("token-replay", "--technique", "-t", help="Conformance technique"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed deviations")
):
    """Check conformance between logs and process models"""
    
    async def run_conformance():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "log_file": str(log_file),
            "model_file": str(model_file),
            "conformance_config": {
                "technique": technique,
                "calculate_fitness": True,
                "calculate_precision": True,
                "identify_deviations": True,
                "detailed_analysis": detailed
            },
            "cli_command": "mining conformance"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Checking conformance...", total=None)
            
            try:
                result = await engine.execute_workflow("check_conformance", context)
                
                if result.success:
                    conformance_result = result.final_data.get("conformance_result", {})
                    progress.update(task, description="✅ Conformance check complete")
                    
                    display_conformance_results(conformance_result, detailed)
                else:
                    progress.update(task, description="❌ Conformance check failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Conformance check failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_conformance())

@app.command("visualize")
def mining_visualize(
    ctx: typer.Context,
    input_file: Path = typer.Argument(help="Process model or log file"),
    visualization: str = typer.Option("process-map", "--type", "-t", help="Visualization type"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Generate interactive visualization")
):
    """Visualize process models and logs"""
    
    async def run_visualize():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        output_path = output_file or input_file.with_suffix(".html" if interactive else ".png")
        
        context = {
            "input_file": str(input_file),
            "visualization_config": {
                "type": visualization,
                "output_file": str(output_path),
                "interactive": interactive,
                "include_statistics": True,
                "color_by_frequency": True
            },
            "cli_command": "mining visualize"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🎨 Creating visualization...", total=None)
            
            try:
                result = await engine.execute_workflow("visualize_process", context)
                
                if result.success:
                    viz_result = result.final_data.get("visualization_result", {})
                    progress.update(task, description="✅ Visualization complete")
                    
                    display_visualization_results(viz_result, output_path, interactive)
                else:
                    progress.update(task, description="❌ Visualization failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Visualization failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_visualize())

@app.command("predict")
def mining_predict(
    ctx: typer.Context,
    log_file: Path = typer.Argument(help="Historical process log file"),
    prediction_type: str = typer.Option("next-activity", "--type", "-t", help="Prediction type"),
    model: str = typer.Option("lstm", "--model", "-m", help="ML model: lstm, random-forest, xgboost"),
    evaluate: bool = typer.Option(True, "--evaluate/--no-evaluate", help="Evaluate model performance")
):
    """Predict process outcomes using ML"""
    
    async def run_predict():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "log_file": str(log_file),
            "prediction_config": {
                "prediction_type": prediction_type,
                "model_type": model,
                "train_test_split": 0.8,
                "evaluate_model": evaluate,
                "feature_engineering": True
            },
            "cli_command": "mining predict"
        }
        
        console.print(Panel(
            f"[bold blue]Process Prediction[/bold blue]\n"
            f"Type: {prediction_type}\n"
            f"Model: {model.upper()}\n"
            f"Evaluation: {'Enabled' if evaluate else 'Disabled'}",
            title="Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔮 Training prediction model...", total=None)
            
            try:
                result = await engine.execute_workflow("predict_process", context)
                
                if result.success:
                    prediction_result = result.final_data.get("prediction_result", {})
                    progress.update(task, description="✅ Prediction model ready")
                    
                    display_prediction_results(prediction_result, prediction_type)
                else:
                    progress.update(task, description="❌ Prediction failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Prediction failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_predict())

# Display helper functions

def display_conversion_results(result: dict, output_file: Path):
    """Display XES conversion results"""
    stats = result.get("statistics", {})
    
    table = Table(title="Conversion Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Events Converted", str(stats.get("event_count", 0)))
    table.add_row("Cases/Traces", str(stats.get("case_count", 0)))
    table.add_row("Unique Activities", str(stats.get("activity_count", 0)))
    table.add_row("Time Span", f"{stats.get('duration_days', 0)} days")
    table.add_row("Output Size", f"{stats.get('file_size_mb', 0):.2f} MB")
    
    console.print(table)
    console.print(f"\n[green]Output saved to: {output_file}[/green]")

def display_discovery_results(result: dict, algorithm: str):
    """Display process discovery results"""
    model_stats = result.get("model_statistics", {})
    
    console.print(Panel(
        f"[bold green]Process Model Discovered![/bold green]\n"
        f"Algorithm: {algorithm}\n"
        f"Activities: {model_stats.get('activity_count', 0)}\n"
        f"Transitions: {model_stats.get('transition_count', 0)}\n"
        f"Gateways: {model_stats.get('gateway_count', 0)}",
        title="Discovery Results"
    ))
    
    # Show process variants
    variants = result.get("top_variants", [])
    if variants:
        console.print("\n[bold]Top Process Variants:[/bold]")
        for i, variant in enumerate(variants[:5], 1):
            console.print(f"{i}. {variant['path']} ({variant['frequency']} occurrences, {variant['percentage']:.1%})")

def display_process_analysis(result: dict, metrics: List[str]):
    """Display process analysis results"""
    # General statistics
    stats = result.get("general_statistics", {})
    
    table = Table(title="Process Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for metric, value in stats.items():
        table.add_row(metric.replace("_", " ").title(), str(value))
    
    console.print(table)
    
    # Metric-specific results
    for metric in metrics:
        metric_data = result.get(f"{metric}_analysis", {})
        if metric_data:
            console.print(f"\n[bold]{metric.upper()} Analysis:[/bold]")
            
            if metric == "duration":
                console.print(f"  Average: {metric_data.get('average', 0):.2f} hours")
                console.print(f"  Median: {metric_data.get('median', 0):.2f} hours")
                console.print(f"  Min: {metric_data.get('min', 0):.2f} hours")
                console.print(f"  Max: {metric_data.get('max', 0):.2f} hours")
            elif metric == "frequency":
                top_activities = metric_data.get('top_activities', [])
                for activity in top_activities[:5]:
                    console.print(f"  • {activity['name']}: {activity['count']} times")

def display_conformance_results(result: dict, detailed: bool):
    """Display conformance checking results"""
    fitness = result.get("fitness", 0)
    precision = result.get("precision", 0)
    generalization = result.get("generalization", 0)
    simplicity = result.get("simplicity", 0)
    
    # Overall conformance score
    overall = (fitness + precision + generalization + simplicity) / 4
    
    console.print(Panel(
        f"[bold]Overall Conformance: {overall:.1%}[/bold]\n"
        f"Fitness: {fitness:.1%}\n"
        f"Precision: {precision:.1%}\n"
        f"Generalization: {generalization:.1%}\n"
        f"Simplicity: {simplicity:.1%}",
        title="Conformance Metrics"
    ))
    
    if detailed:
        deviations = result.get("deviations", [])
        if deviations:
            console.print("\n[bold]Detected Deviations:[/bold]")
            for dev in deviations[:10]:
                console.print(f"  • Case {dev['case_id']}: {dev['description']} at {dev['activity']}")

def display_visualization_results(result: dict, output_file: Path, interactive: bool):
    """Display visualization results"""
    console.print(Panel(
        f"[bold green]Visualization Created![/bold green]\n"
        f"Type: {result.get('visualization_type', 'unknown')}\n"
        f"Format: {'Interactive HTML' if interactive else 'Static Image'}\n"
        f"Elements: {result.get('element_count', 0)}\n"
        f"File: {output_file}",
        title="Visualization Summary"
    ))
    
    if interactive:
        console.print("\n[dim]Open the HTML file in a web browser to interact with the visualization[/dim]")

def display_prediction_results(result: dict, prediction_type: str):
    """Display prediction model results"""
    if result.get("evaluation_metrics"):
        metrics = result["evaluation_metrics"]
        
        table = Table(title=f"{prediction_type} Prediction Performance")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Accuracy", f"{metrics.get('accuracy', 0):.1%}")
        table.add_row("Precision", f"{metrics.get('precision', 0):.1%}")
        table.add_row("Recall", f"{metrics.get('recall', 0):.1%}")
        table.add_row("F1 Score", f"{metrics.get('f1_score', 0):.1%}")
        
        console.print(table)
    
    # Sample predictions
    samples = result.get("sample_predictions", [])
    if samples:
        console.print("\n[bold]Sample Predictions:[/bold]")
        for sample in samples[:5]:
            console.print(f"  • Input: {sample['input']} → Predicted: {sample['predicted']} (Confidence: {sample['confidence']:.1%})")

if __name__ == "__main__":
    app()