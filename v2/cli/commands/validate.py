"""
WeaverGen v2 Validation Commands
Comprehensive validation functionality for semantic conventions and generated code
"""

import typer
import asyncio
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from ...core.engine.spiff_engine import WeaverGenV2Engine

app = typer.Typer(
    name="validate",
    help="Validation commands for semantic conventions and generated code",
    rich_markup_mode="rich"
)

console = Console()

@app.command("semantic")
def validate_semantic(
    ctx: typer.Context,
    registry_path: Path = typer.Argument(help="Path to semantic convention registry"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict validation"),
    output_format: str = typer.Option("rich", "--format", help="Output format: rich, json, yaml"),
    save_report: bool = typer.Option(False, "--save-report", help="Save validation report")
):
    """Validate semantic convention definitions"""
    
    async def run_validate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "registry_path": str(registry_path),
            "validation_config": {
                "strict_mode": strict,
                "check_references": True,
                "check_deprecations": True,
                "check_naming": True
            },
            "cli_command": "validate semantic"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Validating semantic conventions...", total=None)
            
            try:
                result = await engine.execute_workflow("semantic_validation", context)
                
                if result.success:
                    validation_result = result.final_data.get("validation_result", {})
                    progress.update(task, description="✅ Validation complete")
                    
                    display_validation_results(validation_result, output_format)
                    
                    if save_report:
                        report_file = Path("validation_report.json")
                        import json
                        with open(report_file, 'w') as f:
                            json.dump(validation_result, f, indent=2)
                        console.print(f"[green]Report saved to: {report_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Validation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Validation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_validate())

@app.command("code")
def validate_code(
    ctx: typer.Context,
    file_paths: List[Path] = typer.Argument(..., help="Paths to files to validate"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Language (auto-detect if not specified)"),
    rules: Optional[Path] = typer.Option(None, "--rules", "-r", help="Custom validation rules file"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues")
):
    """Validate generated code files"""
    
    async def run_validate_code():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "file_paths": [str(fp) for fp in file_paths],
            "code_validation_config": {
                "language": language,
                "custom_rules": str(rules) if rules else None,
                "auto_fix": fix,
                "check_style": True,
                "check_correctness": True,
                "check_performance": True
            },
            "cli_command": "validate code"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🔍 Validating {len(file_paths)} files...", total=None)
            
            try:
                result = await engine.execute_workflow("code_validation", context)
                
                if result.success:
                    code_result = result.final_data.get("code_validation_result", {})
                    progress.update(task, description="✅ Code validation complete")
                    
                    display_code_validation_results(code_result, fix)
                else:
                    progress.update(task, description="❌ Code validation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Code validation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_validate_code())

@app.command("multi")
def validate_multi(
    ctx: typer.Context,
    file_path: Path = typer.Argument(help="Path to file to validate"),
    validators: List[str] = typer.Option(["syntax", "semantic", "performance"], "--validator", "-v"),
    parallel: bool = typer.Option(True, "--parallel/--sequential", help="Run validators in parallel")
):
    """Run multiple validators on a single file"""
    
    async def run_validate_multi():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "file_path": str(file_path),
            "multi_validation_config": {
                "validators": validators,
                "parallel_execution": parallel,
                "aggregate_results": True
            },
            "cli_command": "validate multi"
        }
        
        console.print(Panel(
            f"[bold blue]Multi-Validator[/bold blue]\n"
            f"File: {file_path.name}\n"
            f"Validators: {', '.join(validators)}\n"
            f"Mode: {'Parallel' if parallel else 'Sequential'}",
            title="Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Running multiple validators...", total=None)
            
            try:
                result = await engine.execute_workflow("multi_validation", context)
                
                if result.success:
                    multi_result = result.final_data.get("multi_validation_result", {})
                    progress.update(task, description="✅ Multi-validation complete")
                    
                    display_multi_validation_results(multi_result, validators)
                else:
                    progress.update(task, description="❌ Multi-validation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Multi-validation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_validate_multi())

@app.command("compliance")
def validate_compliance(
    ctx: typer.Context,
    project_dir: Path = typer.Argument(help="Project directory to validate"),
    standards: List[str] = typer.Option(["otel", "semconv"], "--standard", "-s", help="Compliance standards"),
    generate_report: bool = typer.Option(True, "--report/--no-report", help="Generate compliance report")
):
    """Validate project compliance with standards"""
    
    async def run_validate_compliance():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "project_dir": str(project_dir),
            "compliance_config": {
                "standards": standards,
                "deep_scan": True,
                "include_recommendations": True
            },
            "cli_command": "validate compliance"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📋 Checking compliance...", total=None)
            
            try:
                result = await engine.execute_workflow("compliance_validation", context)
                
                if result.success:
                    compliance_result = result.final_data.get("compliance_result", {})
                    progress.update(task, description="✅ Compliance check complete")
                    
                    display_compliance_results(compliance_result, standards)
                    
                    if generate_report:
                        report_path = project_dir / "compliance_report.html"
                        generate_compliance_report(compliance_result, report_path)
                        console.print(f"[green]Report generated: {report_path}[/green]")
                        
                else:
                    progress.update(task, description="❌ Compliance check failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Compliance check failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_validate_compliance())

# Display helper functions

def display_validation_results(result: dict, output_format: str):
    """Display semantic validation results"""
    if output_format == "json":
        import json
        console.print_json(json.dumps(result, indent=2))
        return
    
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    
    if errors:
        console.print(f"\n[red]Found {len(errors)} errors:[/red]")
        for error in errors[:5]:  # Show first 5
            console.print(f"  ❌ {error['message']} ({error.get('location', 'unknown')})")
        if len(errors) > 5:
            console.print(f"  ... and {len(errors) - 5} more")
    
    if warnings:
        console.print(f"\n[yellow]Found {len(warnings)} warnings:[/yellow]")
        for warning in warnings[:5]:  # Show first 5
            console.print(f"  ⚠️  {warning['message']} ({warning.get('location', 'unknown')})")
        if len(warnings) > 5:
            console.print(f"  ... and {len(warnings) - 5} more")
    
    if not errors and not warnings:
        console.print("[green]✅ All validations passed![/green]")

def display_code_validation_results(result: dict, auto_fix: bool):
    """Display code validation results"""
    table = Table(title="Code Validation Results")
    table.add_column("File", style="cyan")
    table.add_column("Issues", style="red")
    table.add_column("Fixed", style="green")
    table.add_column("Status", style="magenta")
    
    for file_result in result.get("file_results", []):
        issues = file_result.get("issue_count", 0)
        fixed = file_result.get("fixed_count", 0) if auto_fix else 0
        status = "✅ Pass" if issues == 0 else "❌ Fail"
        
        table.add_row(
            Path(file_result["file"]).name,
            str(issues),
            str(fixed) if auto_fix else "N/A",
            status
        )
    
    console.print(table)
    
    # Show sample issues
    sample_issues = result.get("sample_issues", [])
    if sample_issues:
        console.print("\n[bold]Sample Issues:[/bold]")
        for issue in sample_issues[:3]:
            console.print(f"  {issue['severity']}: {issue['message']} ({issue['file']}:{issue['line']})")

def display_multi_validation_results(result: dict, validators: List[str]):
    """Display multi-validation results"""
    table = Table(title="Multi-Validation Results")
    table.add_column("Validator", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Issues", style="red")
    table.add_column("Score", style="green")
    
    for validator in validators:
        validator_result = result.get(validator, {})
        status = "✅" if validator_result.get("passed", False) else "❌"
        issues = validator_result.get("issue_count", 0)
        score = validator_result.get("score", 0)
        
        table.add_row(
            validator,
            status,
            str(issues),
            f"{score:.1%}"
        )
    
    console.print(table)
    
    # Overall summary
    overall_score = result.get("overall_score", 0)
    overall_status = "PASS" if result.get("overall_passed", False) else "FAIL"
    
    console.print(Panel(
        f"[bold]Overall Status: {overall_status}[/bold]\n"
        f"Overall Score: {overall_score:.1%}",
        title="Summary"
    ))

def display_compliance_results(result: dict, standards: List[str]):
    """Display compliance validation results"""
    for standard in standards:
        standard_result = result.get(standard, {})
        compliant = standard_result.get("compliant", False)
        score = standard_result.get("compliance_score", 0)
        
        console.print(Panel(
            f"[bold]{'✅ COMPLIANT' if compliant else '❌ NON-COMPLIANT'}[/bold]\n"
            f"Score: {score:.1%}\n"
            f"Checks Passed: {standard_result.get('passed', 0)}/{standard_result.get('total', 0)}",
            title=f"{standard.upper()} Compliance"
        ))
        
        # Show violations
        violations = standard_result.get("violations", [])
        if violations:
            console.print(f"\n[red]Violations:[/red]")
            for violation in violations[:5]:
                console.print(f"  • {violation['rule']}: {violation['message']}")

def generate_compliance_report(result: dict, report_path: Path):
    """Generate HTML compliance report"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compliance Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .compliant { color: green; }
            .non-compliant { color: red; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Compliance Report</h1>
        <p>Generated: {timestamp}</p>
        {content}
    </body>
    </html>
    """
    
    # Generate content (simplified)
    from datetime import datetime
    content = "<h2>Results</h2><ul>"
    for standard, data in result.items():
        status = "compliant" if data.get("compliant", False) else "non-compliant"
        content += f'<li class="{status}">{standard}: {data.get("compliance_score", 0):.1%}</li>'
    content += "</ul>"
    
    html = html_content.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        content=content
    )
    
    report_path.write_text(html)

if __name__ == "__main__":
    app()