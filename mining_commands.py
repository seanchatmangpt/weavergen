"""
Mining CLI Commands - Professional Process Mining Integration

This module contains all the CLI commands for process mining functionality
including XES conversion, PM4Py integration, and professional process analysis.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .xes_converter import XESConverter
from .bpmn_process_miner import BPMNProcessMiner
from .bpmn_adaptive_engine import AdaptiveBPMNEngine
from .pydantic_ai_bpmn_engine import PydanticAIContext

console = Console()


def get_mining_app():
    """Get the mining CLI app with all commands registered"""
    
    mining_app = typer.Typer(help="⛏️ Process mining and XES conversion")
    
    @mining_app.command()
    def spans_to_xes(
        spans_file: str = typer.Argument(..., help="Path to spans JSON file"),
        output: str = typer.Option("output.xes", "--output", "-o", help="Output XES file path"),
        case_field: str = typer.Option("trace_id", "--case-field", help="Field to use as case ID"),
        activity_field: str = typer.Option("task", "--activity-field", help="Field to use as activity name"),
        timestamp_field: str = typer.Option("timestamp", "--timestamp-field", help="Field to use as timestamp")
    ):
        """🔄 Convert OpenTelemetry spans to XES format for process mining
        
        Converts execution spans to the industry-standard XES format that can be
        imported into professional process mining tools like ProM, Celonis, etc.
        """
        
        console.print(f"\n[bold blue]🔄 Converting Spans to XES[/bold blue]")
        console.print(f"Input: {spans_file}")
        console.print(f"Output: {output}\n")
        
        # Load spans
        try:
            with open(spans_file) as f:
                spans = json.load(f)
                
            if not isinstance(spans, list):
                console.print("[red]❌ Spans file must contain a list of spans[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]❌ Error loading spans: {e}[/red]")
            raise typer.Exit(1)
        
        # Convert to XES
        converter = XESConverter()
        result_file = converter.spans_to_xes(
            spans=spans,
            output_path=output,
            case_id_field=case_field,
            activity_field=activity_field,
            timestamp_field=timestamp_field
        )
        
        console.print(f"\n[green]✅ Conversion complete![/green]")
        console.print(f"XES file saved: {result_file}")
        console.print("\n[dim]You can now import this file into process mining tools like ProM, Celonis, or Disco.[/dim]")
    
    @mining_app.command()
    def analyze_xes(
        xes_file: str = typer.Argument(..., help="Path to XES file"),
        generate_models: bool = typer.Option(True, "--models/--no-models", help="Generate process models"),
        output_dir: str = typer.Option("process_analysis", "--output", "-o", help="Output directory for analysis")
    ):
        """📊 Analyze XES file and generate process insights
        
        Performs comprehensive process mining analysis on XES files including:
        - Process statistics and variants
        - Process model discovery
        - Performance analysis
        - Visualization generation
        """
        
        console.print(f"\n[bold blue]📊 Analyzing XES File[/bold blue]")
        console.print(f"Input: {xes_file}\n")
        
        if not Path(xes_file).exists():
            console.print(f"[red]❌ XES file not found: {xes_file}[/red]")
            raise typer.Exit(1)
        
        # Analyze XES
        converter = XESConverter()
        analysis = converter.analyze_xes(xes_file)
        
        # Generate process models if requested
        if generate_models:
            console.print(f"\n[cyan]🏗️  Generating process models...[/cyan]")
            models = converter.generate_process_model(xes_file, output_dir)
            
            if models:
                console.print(f"\n[green]✅ Generated {len(models)} process models:[/green]")
                for model_type, file_path in models.items():
                    console.print(f"  {model_type}: {file_path}")
        
        # Save analysis results
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        analysis_file = output_path / "analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        console.print(f"\n[green]✅ Analysis saved: {analysis_file}[/green]")
    
    @mining_app.command()
    def xes_to_bpmn(
        xes_file: str = typer.Argument(..., help="Path to XES file"),
        output: str = typer.Option("discovered.bpmn", "--output", "-o", help="Output BPMN file path")
    ):
        """🔄 Convert XES log to BPMN workflow
        
        Discovers a BPMN workflow model from XES execution logs.
        The generated BPMN can be used for workflow automation.
        """
        
        console.print(f"\n[bold blue]🔄 Converting XES to BPMN[/bold blue]")
        console.print(f"Input: {xes_file}")
        console.print(f"Output: {output}\n")
        
        if not Path(xes_file).exists():
            console.print(f"[red]❌ XES file not found: {xes_file}[/red]")
            raise typer.Exit(1)
        
        # Convert XES to BPMN
        converter = XESConverter()
        result_file = converter.xes_to_bpmn(xes_file, output)
        
        console.print(f"\n[green]✅ BPMN generated: {result_file}[/green]")
        console.print("[dim]You can now use this BPMN file in workflow engines like SpiffWorkflow.[/dim]")
    
    @mining_app.command()
    def mine_patterns(
        spans_file: str = typer.Argument(..., help="Path to spans JSON file"),
        output_dir: str = typer.Option("mined_patterns", "--output", "-o", help="Output directory"),
        workflow_name: str = typer.Option("MinedWorkflow", "--name", help="Name for discovered workflow"),
        generate_bpmn: bool = typer.Option(True, "--bpmn/--no-bpmn", help="Generate BPMN from patterns")
    ):
        """⛏️  Mine process patterns from execution spans
        
        Discovers process patterns, sequences, and optimizations from span data.
        Generates insights about workflow efficiency and improvement opportunities.
        """
        
        console.print(f"\n[bold blue]⛏️  Mining Process Patterns[/bold blue]")
        console.print(f"Input: {spans_file}")
        console.print(f"Output: {output_dir}\n")
        
        # Load spans
        try:
            with open(spans_file) as f:
                spans = json.load(f)
                
            if not isinstance(spans, list):
                console.print("[red]❌ Spans file must contain a list of spans[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]❌ Error loading spans: {e}[/red]")
            raise typer.Exit(1)
        
        # Mine workflow
        miner = BPMNProcessMiner()
        discovered = miner.mine_workflow(spans, workflow_name)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save discovered patterns
        patterns_file = output_path / "patterns.json"
        patterns_data = {
            "workflow_name": discovered.name,
            "patterns": [
                {
                    "type": p.pattern_type,
                    "tasks": p.tasks,
                    "frequency": p.frequency,
                    "confidence": p.confidence,
                    "performance_impact": p.performance_impact
                }
                for p in discovered.patterns
            ],
            "quality_metrics": discovered.quality_metrics,
            "start_tasks": list(discovered.start_tasks),
            "end_tasks": list(discovered.end_tasks)
        }
        
        with open(patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)
        
        console.print(f"[green]✅ Patterns saved: {patterns_file}[/green]")
        
        # Generate BPMN if requested
        if generate_bpmn:
            bpmn_file = output_path / f"{workflow_name.lower()}.bpmn"
            miner.generate_bpmn(discovered, str(bpmn_file))
            console.print(f"[green]✅ BPMN generated: {bpmn_file}[/green]")
    
    @mining_app.command()
    def adaptive_demo(
        semantic_file: str = typer.Argument(..., help="Semantic convention file"),
        runs: int = typer.Option(10, "--runs", "-r", help="Number of execution runs"),
        output_dir: str = typer.Option("adaptive_demo", "--output", "-o", help="Output directory")
    ):
        """🧠 Demonstrate adaptive BPMN learning
        
        Runs multiple workflow executions to demonstrate adaptive learning
        and performance optimization over time.
        """
        
        console.print(f"\n[bold blue]🧠 Adaptive BPMN Learning Demo[/bold blue]")
        console.print(f"Semantic file: {semantic_file}")
        console.print(f"Execution runs: {runs}")
        console.print(f"Output: {output_dir}\n")
        
        async def run_adaptive_demo():
            # Create adaptive engine
            engine = AdaptiveBPMNEngine(use_mock=True)
            
            # Run multiple executions
            for i in range(runs):
                console.print(f"\n[dim]Execution {i+1}/{runs}[/dim]")
                
                context = PydanticAIContext(
                    semantic_file=semantic_file,
                    output_dir=f"{output_dir}/run_{i}"
                )
                
                # Enable optimization after 30% of runs
                enable_opt = i >= (runs * 0.3)
                
                result = await engine.execute_adaptive(
                    workflow_name="AdaptiveDemo",
                    context=context,
                    enable_optimization=enable_opt
                )
                
                if enable_opt and i == int(runs * 0.3):
                    console.print("\n[yellow]🎯 Adaptive optimization enabled![/yellow]")
            
            # Show results
            console.print("\n[bold green]📊 Adaptive Learning Results:[/bold green]")
            console.print(engine.get_performance_report())
            
            console.print("\n[bold]📈 Learning Curve:[/bold]")
            console.print(engine.visualize_learning_curve())
            
            # Save execution history
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            history_file = output_path / "execution_history.json"
            with open(history_file, 'w') as f:
                history_data = [
                    {
                        "execution_id": m.execution_id,
                        "duration_ms": m.duration_ms,
                        "quality_score": m.quality_score,
                        "success": m.success,
                        "task_durations": m.task_durations
                    }
                    for m in engine.execution_history
                ]
                json.dump(history_data, f, indent=2)
            
            console.print(f"\n[green]✅ Execution history saved: {history_file}[/green]")
        
        # Run the demo
        asyncio.run(run_adaptive_demo())
    
    @mining_app.command()
    def convert_all(
        input_dir: str = typer.Argument(..., help="Directory containing span files"),
        output_dir: str = typer.Option("converted_xes", "--output", "-o", help="Output directory"),
        pattern: str = typer.Option("**/*spans*.json", "--pattern", help="File pattern to match"),
        analyze: bool = typer.Option(True, "--analyze/--no-analyze", help="Analyze converted files")
    ):
        """🔄 Batch convert span files to XES format
        
        Converts all span files in a directory to XES format for batch processing
        in professional process mining tools.
        """
        
        console.print(f"\n[bold blue]🔄 Batch Converting Spans to XES[/bold blue]")
        console.print(f"Input directory: {input_dir}")
        console.print(f"Pattern: {pattern}")
        console.print(f"Output: {output_dir}\n")
        
        input_path = Path(input_dir)
        if not input_path.exists():
            console.print(f"[red]❌ Input directory not found: {input_dir}[/red]")
            raise typer.Exit(1)
        
        # Find span files
        span_files = list(input_path.glob(pattern))
        
        if not span_files:
            console.print(f"[yellow]⚠️  No files found matching pattern: {pattern}[/yellow]")
            raise typer.Exit(1)
        
        console.print(f"Found {len(span_files)} span files")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert each file
        converter = XESConverter()
        converted_files = []
        
        for span_file in span_files:
            try:
                console.print(f"\n[cyan]Converting: {span_file.name}[/cyan]")
                
                with open(span_file) as f:
                    spans = json.load(f)
                
                if not isinstance(spans, list):
                    console.print(f"[yellow]⚠️  Skipping {span_file.name}: not a list[/yellow]")
                    continue
                
                # Generate output filename
                xes_filename = span_file.stem + ".xes"
                xes_path = output_path / xes_filename
                
                # Convert to XES
                result_file = converter.spans_to_xes(spans, str(xes_path))
                converted_files.append(result_file)
                
                console.print(f"[green]✅ Converted: {xes_filename}[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error converting {span_file.name}: {e}[/red]")
        
        # Summary
        console.print(f"\n[bold green]🎉 Batch conversion complete![/bold green]")
        console.print(f"Successfully converted: {len(converted_files)}/{len(span_files)} files")
        
        # Analyze if requested
        if analyze and converted_files:
            console.print(f"\n[cyan]📊 Analyzing converted files...[/cyan]")
            
            for xes_file in converted_files[:3]:  # Analyze first 3 files
                console.print(f"\nAnalyzing: {Path(xes_file).name}")
                try:
                    converter.analyze_xes(xes_file)
                except Exception as e:
                    console.print(f"[yellow]⚠️  Analysis error: {e}[/yellow]")
    
    @mining_app.command()
    def export_dataframe(
        spans_file: str = typer.Argument(..., help="Path to spans JSON file"),
        output: str = typer.Option("spans_data.csv", "--output", "-o", help="Output CSV file path"),
        format: str = typer.Option("csv", "--format", help="Output format (csv, parquet, json)")
    ):
        """📊 Export spans to DataFrame format for analysis
        
        Converts spans to a flattened DataFrame format suitable for
        data analysis tools like Excel, R, or Python pandas.
        """
        
        console.print(f"\n[bold blue]📊 Exporting Spans to DataFrame[/bold blue]")
        console.print(f"Input: {spans_file}")
        console.print(f"Output: {output}")
        console.print(f"Format: {format}\n")
        
        # Load spans
        try:
            with open(spans_file) as f:
                spans = json.load(f)
                
            if not isinstance(spans, list):
                console.print("[red]❌ Spans file must contain a list of spans[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]❌ Error loading spans: {e}[/red]")
            raise typer.Exit(1)
        
        # Convert to DataFrame
        converter = XESConverter()
        df = converter.spans_to_dataframe(spans)
        
        # Export based on format
        try:
            if format.lower() == "csv":
                df.to_csv(output, index=False)
            elif format.lower() == "parquet":
                df.to_parquet(output, index=False)
            elif format.lower() == "json":
                df.to_json(output, orient="records", indent=2)
            else:
                console.print(f"[red]❌ Unsupported format: {format}[/red]")
                raise typer.Exit(1)
            
            console.print(f"[green]✅ DataFrame exported: {output}[/green]")
            console.print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Show preview
            console.print("\n[bold]Preview:[/bold]")
            preview_table = Table()
            
            # Add columns (first 5)
            for col in list(df.columns)[:5]:
                preview_table.add_column(col, style="cyan")
            
            # Add rows (first 3)
            for _, row in df.head(3).iterrows():
                values = [str(row[col])[:20] + "..." if len(str(row[col])) > 20 else str(row[col]) 
                         for col in list(df.columns)[:5]]
                preview_table.add_row(*values)
            
            console.print(preview_table)
            
        except Exception as e:
            console.print(f"[red]❌ Export error: {e}[/red]")
            raise typer.Exit(1)
    
    return mining_app