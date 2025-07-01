#!/usr/bin/env python3
"""
WeaverGen BPMN 80/20 - Simple BPMN-First Code Generation

Preserves the value of BPMN (visual workflows, parallel execution, standards)
while removing 99% of the complexity.

80% of value with 20% of code - but keeping BPMN as the core.
"""

import json
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional

import typer
import yaml
from rich.console import Console
from rich.table import Table


app = typer.Typer(help="BPMN-first semantic code generation")
console = Console()


# Simple Data Models (no Pydantic needed)

@dataclass
class WorkflowContext:
    """Context passed through BPMN workflow"""
    semantic_file: str
    languages: List[str]
    output_dir: str
    validation_passed: bool = False
    results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = {}


# Minimal BPMN Engine (100 lines, not SpiffWorkflow)

class SimpleBPMNEngine:
    """Minimal BPMN engine for the 80/20 use case"""
    
    def __init__(self, bpmn_file: str):
        self.bpmn_file = bpmn_file
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> Dict[str, Any]:
        """Parse BPMN and extract service tasks"""
        tree = ET.parse(self.bpmn_file)
        root = tree.getroot()
        
        # Extract namespace
        ns = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
        
        # Find all service tasks
        tasks = {}
        for task in root.findall('.//bpmn:serviceTask', ns):
            task_id = task.get('id')
            task_name = task.get('name', task_id)
            tasks[task_id] = {
                'id': task_id,
                'name': task_name,
                'type': 'service'
            }
        
        return tasks
    
    def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Execute workflow with given context"""
        
        # This is the 80/20 execution - hardcoded flow that matches our BPMN
        # Real BPMN engines are complex; we just need these 5 steps
        
        # 1. Load Semantic File
        context = self._execute_task('Task_LoadSemantic', LoadSemanticTask(), context)
        if not context.results.get('loaded'):
            return context
        
        # 2. Validate Semantics
        context = self._execute_task('Task_ValidateSemantic', ValidateSemanticTask(), context)
        if not context.validation_passed:
            return context
        
        # 3. Generate Code (parallel for each language)
        generation_results = {}
        for language in context.languages:
            lang_context = self._execute_task(
                f'Task_GenerateCode_{language}', 
                GenerateCodeTask(language), 
                context
            )
            generation_results[language] = lang_context.results.get(language, {})
        
        context.results['generation'] = generation_results
        
        # 4. Generate Report
        context = self._execute_task('Task_GenerateReport', GenerateReportTask(), context)
        
        return context
    
    def _execute_task(self, task_id: str, task_impl, context: WorkflowContext) -> WorkflowContext:
        """Execute a single task"""
        console.print(f"[cyan]→ {task_impl.__class__.__name__}[/cyan]")
        return task_impl.execute(context)


# The 5 Essential Service Tasks (20 lines each max)

class LoadSemanticTask:
    """Load and parse semantic convention file"""
    
    def execute(self, context: WorkflowContext) -> WorkflowContext:
        path = Path(context.semantic_file)
        if not path.exists():
            context.results['error'] = f"File not found: {context.semantic_file}"
            context.results['loaded'] = False
            return context
        
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            context.results['semantic_data'] = data
            context.results['loaded'] = True
        except Exception as e:
            context.results['error'] = f"Failed to load: {e}"
            context.results['loaded'] = False
        
        return context


class ValidateSemanticTask:
    """Validate using weaver binary"""
    
    def execute(self, context: WorkflowContext) -> WorkflowContext:
        weaver = find_weaver_binary()
        if not weaver:
            context.results['error'] = "Weaver binary not found"
            context.validation_passed = False
            return context
        
        # Call weaver validate
        result = subprocess.run(
            [weaver, 'registry', 'check', '-r', context.semantic_file],
            capture_output=True,
            text=True
        )
        
        context.validation_passed = result.returncode == 0
        context.results['validation'] = {
            'passed': context.validation_passed,
            'output': result.stdout if context.validation_passed else result.stderr
        }
        
        return context


class GenerateCodeTask:
    """Generate code for a specific language"""
    
    def __init__(self, language: str):
        self.language = language
    
    def execute(self, context: WorkflowContext) -> WorkflowContext:
        weaver = find_weaver_binary()
        if not weaver:
            context.results[self.language] = {'success': False, 'error': 'Weaver not found'}
            return context
        
        output_path = Path(context.output_dir) / self.language
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Call weaver generate
        result = subprocess.run(
            [weaver, 'registry', 'generate',
             '-r', context.semantic_file,
             '-t', f'code/{self.language}',  # Adjust template path as needed
             '--output', str(output_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Count generated files
            files = list(output_path.rglob('*'))
            file_count = len([f for f in files if f.is_file()])
            
            context.results[self.language] = {
                'success': True,
                'files': file_count,
                'path': str(output_path)
            }
        else:
            context.results[self.language] = {
                'success': False,
                'error': result.stderr
            }
        
        return context


class GenerateReportTask:
    """Generate final report"""
    
    def execute(self, context: WorkflowContext) -> WorkflowContext:
        generation = context.results.get('generation', {})
        
        # Create summary
        total_languages = len(generation)
        successful = sum(1 for r in generation.values() if r.get('success', False))
        total_files = sum(r.get('files', 0) for r in generation.values() if r.get('success', False))
        
        context.results['summary'] = {
            'languages_requested': total_languages,
            'languages_generated': successful,
            'total_files': total_files,
            'success': successful == total_languages
        }
        
        return context


# Helper Functions

def find_weaver_binary() -> Optional[str]:
    """Find weaver binary"""
    import shutil
    
    # Check PATH
    if weaver := shutil.which("weaver"):
        return weaver
    
    # Check cargo location
    cargo_bin = Path.home() / ".cargo" / "bin" / "weaver"
    if cargo_bin.exists():
        return str(cargo_bin)
    
    return None


# CLI Commands - BPMN-First Interface

@app.command()
def generate(
    semantic_file: str = typer.Argument(help="Semantic convention YAML file"),
    languages: List[str] = typer.Option(["python"], "--language", "-l", help="Target languages"),
    output_dir: str = typer.Option("./generated", "--output", "-o", help="Output directory"),
    bpmn_file: str = typer.Option(None, "--bpmn", "-b", help="Custom BPMN workflow file"),
):
    """Generate code using BPMN workflow"""
    
    console.print("[bold cyan]🔥 WeaverGen BPMN 80/20[/bold cyan]")
    console.print("[dim]Visual workflows, simple execution[/dim]\n")
    
    # Use default BPMN if not specified
    if not bpmn_file:
        bpmn_file = Path(__file__).parent / "workflows/bpmn/weaver_generate_8020.bpmn"
        if not bpmn_file.exists():
            # Fallback to embedded workflow
            bpmn_file = "weaver_generate_8020.bpmn"
    
    console.print(f"[cyan]📋 BPMN Workflow: {bpmn_file}[/cyan]")
    console.print(f"[cyan]🎯 Languages: {', '.join(languages)}[/cyan]")
    console.print(f"[cyan]📂 Output: {output_dir}[/cyan]\n")
    
    # Create workflow context
    context = WorkflowContext(
        semantic_file=semantic_file,
        languages=languages,
        output_dir=output_dir
    )
    
    # Execute BPMN workflow
    try:
        engine = SimpleBPMNEngine(bpmn_file)
        result_context = engine.execute(context)
        
        # Display results
        display_results(result_context)
        
    except Exception as e:
        console.print(f"[red]❌ Workflow failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def visualize(
    bpmn_file: str = typer.Option(None, "--bpmn", "-b", help="BPMN workflow file to visualize"),
):
    """Open BPMN workflow in default viewer"""
    
    if not bpmn_file:
        bpmn_file = "weaver_generate_8020.bpmn"
    
    console.print(f"[cyan]🎨 Opening BPMN workflow: {bpmn_file}[/cyan]")
    console.print("[dim]Tip: Use bpmn.io, Camunda Modeler, or any BPMN 2.0 editor[/dim]")
    
    # Open in default application
    import webbrowser
    webbrowser.open(f"https://demo.bpmn.io/new?url=file://{Path(bpmn_file).absolute()}")


@app.command()
def validate(
    semantic_file: str = typer.Argument(help="Semantic convention YAML file"),
):
    """Validate semantic conventions (first step of BPMN workflow)"""
    
    context = WorkflowContext(
        semantic_file=semantic_file,
        languages=[],
        output_dir=""
    )
    
    # Execute just validation tasks
    context = LoadSemanticTask().execute(context)
    if context.results.get('loaded'):
        context = ValidateSemanticTask().execute(context)
        
        if context.validation_passed:
            console.print("[green]✅ Validation passed![/green]")
        else:
            console.print("[red]❌ Validation failed![/red]")
            console.print(context.results.get('validation', {}).get('output', ''))
    else:
        console.print(f"[red]❌ {context.results.get('error', 'Unknown error')}[/red]")


def display_results(context: WorkflowContext):
    """Display workflow execution results"""
    
    summary = context.results.get('summary', {})
    generation = context.results.get('generation', {})
    
    # Create results table
    table = Table(title="BPMN Workflow Results")
    table.add_column("Language", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Files", style="blue")
    table.add_column("Location", style="yellow")
    
    for lang, result in generation.items():
        status = "✅ Success" if result.get('success') else "❌ Failed"
        files = str(result.get('files', 0)) if result.get('success') else "-"
        location = result.get('path', '-') if result.get('success') else result.get('error', 'Error')[:30]
        
        table.add_row(lang, status, files, location)
    
    console.print(table)
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  • Languages: {summary.get('languages_generated')}/{summary.get('languages_requested')}")
    console.print(f"  • Total Files: {summary.get('total_files')}")
    console.print(f"  • Success: {'✅' if summary.get('success') else '❌'}")


if __name__ == "__main__":
    app()