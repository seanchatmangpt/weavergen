#!/usr/bin/env python3
"""
Weaver CLI 80/20 Analysis and Implementation

This script analyzes which Weaver commands provide 80% of the value
and ensures our implementation covers them.
"""

import subprocess
from typing import List, Dict, Tuple
import json
from pathlib import Path

# Based on Weaver documentation, here are the main commands:
WEAVER_COMMANDS = {
    # Core Registry Commands (80% value)
    "registry check": {
        "importance": "critical",
        "usage_frequency": "very_high",
        "description": "Validate semantic convention registry",
        "implemented": True,
        "impl_function": "weaver_registry_check"
    },
    "registry generate": {
        "importance": "critical", 
        "usage_frequency": "very_high",
        "description": "Generate code/docs from registry",
        "implemented": True,
        "impl_function": "weaver_registry_generate"
    },
    "registry resolve": {
        "importance": "high",
        "usage_frequency": "high",
        "description": "Resolve references and merge conventions",
        "implemented": True,
        "impl_function": "weaver_registry_resolve"
    },
    "registry stats": {
        "importance": "medium",
        "usage_frequency": "medium", 
        "description": "Show registry statistics",
        "implemented": True,
        "impl_function": "weaver_registry_stats"
    },
    
    # Additional Registry Commands (20% value)
    "registry update-markdown": {
        "importance": "medium",
        "usage_frequency": "low",
        "description": "Update markdown snippets",
        "implemented": False,
        "impl_function": None
    },
    "registry search": {
        "importance": "low",
        "usage_frequency": "low",
        "description": "Search registry contents",
        "implemented": False,
        "impl_function": None
    },
    "registry json-schema": {
        "importance": "low",
        "usage_frequency": "very_low",
        "description": "Generate JSON schema",
        "implemented": False,
        "impl_function": None
    },
    "registry diff": {
        "importance": "medium",
        "usage_frequency": "low",
        "description": "Diff two registry versions",
        "implemented": False,
        "impl_function": None
    }
}

def calculate_coverage() -> Dict[str, float]:
    """Calculate our implementation coverage based on importance weights."""
    
    weights = {
        "critical": 40,
        "high": 30,
        "medium": 20,
        "low": 10
    }
    
    total_weight = 0
    implemented_weight = 0
    
    for cmd, info in WEAVER_COMMANDS.items():
        weight = weights[info["importance"]]
        total_weight += weight
        if info["implemented"]:
            implemented_weight += weight
    
    coverage = (implemented_weight / total_weight) * 100
    
    return {
        "total_commands": len(WEAVER_COMMANDS),
        "implemented_commands": sum(1 for cmd in WEAVER_COMMANDS.values() if cmd["implemented"]),
        "weighted_coverage": coverage,
        "critical_coverage": all(
            cmd["implemented"] for cmd in WEAVER_COMMANDS.values() 
            if cmd["importance"] == "critical"
        )
    }

def verify_implementations():
    """Verify our implementations work correctly."""
    print("=== Verifying Weaver CLI Implementations ===\n")
    
    # Import our runtime implementations
    import sys
    sys.path.append("output")
    from runtime.forge import (
        weaver_registry_check,
        weaver_registry_generate,
        weaver_registry_resolve,
        weaver_registry_stats
    )
    
    results = []
    
    # Test 1: Registry check
    print("1. Testing weaver_registry_check...")
    try:
        is_valid, errors = weaver_registry_check("test_registry2")
        results.append(("registry check", True, f"Valid: {is_valid}"))
        print(f"   ✓ Registry check: {'valid' if is_valid else 'invalid'}")
    except Exception as e:
        results.append(("registry check", False, str(e)))
        print(f"   ✗ Error: {e}")
    
    # Test 2: Registry generate
    print("\n2. Testing weaver_registry_generate...")
    try:
        files = weaver_registry_generate(
            registry_path="test_registry2",
            target_name="python",
            template_path="templates",
            output_dir="test_80_20_output"
        )
        results.append(("registry generate", True, f"Generated {len(files)} files"))
        print(f"   ✓ Generated {len(files)} files")
    except Exception as e:
        results.append(("registry generate", False, str(e)))
        print(f"   ✗ Error: {e}")
    
    # Test 3: Registry resolve
    print("\n3. Testing weaver_registry_resolve...")
    try:
        resolved = weaver_registry_resolve("test_registry2", format="json")
        results.append(("registry resolve", True, "Resolved successfully"))
        print(f"   ✓ Resolved registry to JSON")
    except Exception as e:
        results.append(("registry resolve", False, str(e)))
        print(f"   ✗ Error: {e}")
    
    # Test 4: Registry stats
    print("\n4. Testing weaver_registry_stats...")
    try:
        stats = weaver_registry_stats("test_registry2")
        results.append(("registry stats", True, f"Got {len(stats)} stats"))
        print(f"   ✓ Retrieved {len(stats)} statistics")
    except Exception as e:
        results.append(("registry stats", False, str(e)))
        print(f"   ✗ Error: {e}")
    
    return results

def show_80_20_analysis():
    """Show the 80/20 analysis of Weaver commands."""
    print("=" * 60)
    print("Weaver CLI 80/20 Analysis")
    print("=" * 60)
    
    print("\n[COMMAND IMPORTANCE BREAKDOWN]\n")
    
    # Group by importance
    by_importance = {}
    for cmd, info in WEAVER_COMMANDS.items():
        importance = info["importance"]
        if importance not in by_importance:
            by_importance[importance] = []
        by_importance[importance].append((cmd, info))
    
    # Show commands by importance
    for importance in ["critical", "high", "medium", "low"]:
        if importance in by_importance:
            print(f"{importance.upper()} ({len(by_importance[importance])} commands):")
            for cmd, info in by_importance[importance]:
                status = "✓" if info["implemented"] else "✗"
                print(f"  {status} {cmd:<25} - {info['description']}")
            print()
    
    # Calculate coverage
    coverage = calculate_coverage()
    
    print("[COVERAGE METRICS]\n")
    print(f"Total commands: {coverage['total_commands']}")
    print(f"Implemented: {coverage['implemented_commands']}")
    print(f"Weighted coverage: {coverage['weighted_coverage']:.1f}%")
    print(f"Critical commands covered: {'Yes' if coverage['critical_coverage'] else 'No'}")
    
    print("\n[80/20 PRINCIPLE ANALYSIS]\n")
    
    # Identify the 20% of commands that provide 80% value
    critical_and_high = [
        (cmd, info) for cmd, info in WEAVER_COMMANDS.items()
        if info["importance"] in ["critical", "high"]
    ]
    
    print(f"The {len(critical_and_high)} most important commands ({len(critical_and_high)/len(WEAVER_COMMANDS)*100:.0f}% of total)")
    print("provide approximately 80% of the value:\n")
    
    for cmd, info in critical_and_high:
        status = "✓ Implemented" if info["implemented"] else "✗ Not implemented"
        print(f"  • {cmd}: {status}")
    
    # Recommendations
    print("\n[RECOMMENDATIONS]\n")
    
    if coverage['weighted_coverage'] >= 80:
        print("✅ You have achieved 80/20 coverage!")
        print("   The implementation covers the most valuable commands.")
    else:
        print("⚠️  Below 80/20 threshold")
        print("   Priority implementations needed:")
        for cmd, info in WEAVER_COMMANDS.items():
            if not info["implemented"] and info["importance"] in ["critical", "high"]:
                print(f"   - {cmd} ({info['importance']})")

def generate_cli_wrapper():
    """Generate a complete CLI wrapper that covers 80% use cases."""
    print("\n" + "=" * 60)
    print("Generating 80/20 CLI Wrapper")
    print("=" * 60 + "\n")
    
    wrapper_code = '''#!/usr/bin/env python3
"""
Weaver 80/20 CLI Wrapper

This wrapper implements the 20% of Weaver commands that provide 80% of the value.
"""

import typer
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import sys
import json
import yaml

# Add output directory to path
sys.path.append("output")

from runtime.forge import (
    weaver_registry_check,
    weaver_registry_generate,
    weaver_registry_resolve,
    weaver_registry_stats
)

app = typer.Typer(
    name="weaver80",
    help="🎯 80/20 Weaver CLI - Essential commands only",
    no_args_is_help=True
)

console = Console()

@app.command()
def check(
    registry: Path = typer.Argument(..., help="Registry path"),
    strict: bool = typer.Option(False, "--strict", help="Strict validation")
) -> None:
    """✅ Check registry validity (Most used command)."""
    try:
        is_valid, errors = weaver_registry_check(str(registry))
        if is_valid:
            rprint("[green]✅ Registry is valid[/green]")
        else:
            rprint("[red]❌ Registry validation failed:[/red]")
            for error in errors or []:
                rprint(f"  • {error}")
            raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def generate(
    target: str = typer.Argument(..., help="Target language"),
    registry: Path = typer.Argument(..., help="Registry path"),
    output: Path = typer.Option(Path("./generated"), "-o", "--output"),
    templates: Optional[Path] = typer.Option(None, "-t", "--templates"),
    param: Optional[List[str]] = typer.Option(None, "-p", "--param", help="key=value")
) -> None:
    """🚀 Generate code from registry (Core functionality)."""
    try:
        # Parse parameters
        params = {}
        if param:
            for p in param:
                if "=" in p:
                    key, value = p.split("=", 1)
                    params[key] = value
        
        files = weaver_registry_generate(
            registry_path=str(registry),
            target_name=target,
            template_path=str(templates) if templates else "templates",
            output_dir=str(output),
            params=params
        )
        
        rprint(f"[green]✅ Generated {len(files)} files[/green]")
        for f in files[:5]:
            rprint(f"  • {f}")
        if len(files) > 5:
            rprint(f"  ... and {len(files)-5} more")
            
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def resolve(
    registry: Path = typer.Argument(..., help="Registry path"),
    format: str = typer.Option("yaml", "-f", "--format", help="Output format"),
    output: Optional[Path] = typer.Option(None, "-o", "--output")
) -> None:
    """🔄 Resolve registry references."""
    try:
        resolved = weaver_registry_resolve(
            registry_path=str(registry),
            output_path=str(output) if output else None,
            format=format
        )
        
        if not output:
            if format == "json":
                rprint(json.dumps(resolved, indent=2))
            else:
                rprint(yaml.dump(resolved, default_flow_style=False))
        else:
            rprint(f"[green]✅ Resolved registry written to {output}[/green]")
            
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def stats(
    registry: Path = typer.Argument(..., help="Registry path")
) -> None:
    """📊 Show registry statistics."""
    try:
        stats = weaver_registry_stats(str(registry))
        
        table = Table(title="Registry Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key, str(value))
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def quick(
    registry: Path = typer.Argument(..., help="Registry path")
) -> None:
    """⚡ Quick check + generate Python (80% use case)."""
    rprint("[cyan]Running quick workflow (check + generate)...[/cyan]\\n")
    
    # Check first
    try:
        is_valid, errors = weaver_registry_check(str(registry))
        if is_valid:
            rprint("[green]✅ Registry is valid[/green]")
        else:
            rprint("[red]❌ Registry invalid, aborting[/red]")
            raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Check failed: {e}[/red]")
        raise typer.Exit(1)
    
    # Then generate
    try:
        files = weaver_registry_generate(
            registry_path=str(registry),
            target_name="python",
            template_path="templates",
            output_dir="quick_output"
        )
        rprint(f"\\n[green]✅ Generated {len(files)} Python files[/green]")
    except Exception as e:
        rprint(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
'''
    
    # Write the wrapper
    wrapper_path = Path("weaver_80_20_cli.py")
    wrapper_path.write_text(wrapper_code)
    wrapper_path.chmod(0o755)
    
    print(f"✓ Generated {wrapper_path}")
    print("\nUsage examples:")
    print("  python weaver_80_20_cli.py check test_registry2")
    print("  python weaver_80_20_cli.py generate python test_registry2")
    print("  python weaver_80_20_cli.py quick test_registry2")
    
    return wrapper_path

def main():
    """Run the complete 80/20 analysis."""
    
    # Show analysis
    show_80_20_analysis()
    
    # Verify implementations
    print("\n" + "=" * 60)
    results = verify_implementations()
    
    # Summary
    successful = sum(1 for _, success, _ in results if success)
    print(f"\n[IMPLEMENTATION VERIFICATION]")
    print(f"Successful: {successful}/{len(results)}")
    
    # Generate wrapper
    wrapper_path = generate_cli_wrapper()
    
    # Final recommendation
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    
    coverage = calculate_coverage()
    if coverage['weighted_coverage'] >= 80 and coverage['critical_coverage']:
        print("\n✅ You have achieved optimal 80/20 Weaver CLI coverage!")
        print(f"   - Weighted coverage: {coverage['weighted_coverage']:.1f}%")
        print("   - All critical commands implemented")
        print(f"   - Use {wrapper_path} for streamlined access")
    else:
        print("\n⚠️  More work needed for 80/20 coverage")
        print("   Focus on implementing critical/high importance commands first")
    
    # Cleanup test output
    import shutil
    if Path("test_80_20_output").exists():
        shutil.rmtree("test_80_20_output", ignore_errors=True)

if __name__ == "__main__":
    main()