#!/usr/bin/env python3
"""
WeaverGen 80/20 - The Simple Version

This is what WeaverGen should be: A simple wrapper around OTel Weaver
that makes it easy to generate code from semantic conventions.

80% of the value with 20% of the complexity.
"""

import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any

import typer
import yaml
from rich.console import Console
from rich.table import Table


app = typer.Typer(help="Simple semantic convention code generator")
console = Console()
logger = logging.getLogger(__name__)


class WeaverGen:
    """Simple wrapper around OTel Weaver - does one thing well"""
    
    def __init__(self, weaver_binary: Optional[str] = None):
        self.weaver_binary = weaver_binary or self._find_weaver()
        if not self.weaver_binary:
            raise RuntimeError("Weaver not found. Install with: cargo install weaver-forge")
    
    def _find_weaver(self) -> Optional[str]:
        """Find weaver binary"""
        # Check PATH first
        if weaver := shutil.which("weaver"):
            return weaver
        
        # Check common cargo location
        cargo_bin = Path.home() / ".cargo" / "bin" / "weaver"
        if cargo_bin.exists():
            return str(cargo_bin)
        
        return None
    
    def generate(self, semantic_file: str, languages: List[str], output_dir: str = "./generated") -> Dict[str, Any]:
        """Generate code for specified languages - the core functionality"""
        
        semantic_path = Path(semantic_file)
        if not semantic_path.exists():
            raise FileNotFoundError(f"Semantic file not found: {semantic_file}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        errors = []
        
        # Generate for each language in parallel (the actual 80/20 optimization)
        for language in languages:
            try:
                lang_output = output_path / language
                lang_output.mkdir(exist_ok=True)
                
                # Call weaver - this is what actually matters
                cmd = [
                    self.weaver_binary,
                    "generate",
                    "-f", str(semantic_path),
                    "-t", language,
                    "-o", str(lang_output)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Count generated files
                    files = list(lang_output.rglob("*"))
                    file_count = len([f for f in files if f.is_file()])
                    
                    results[language] = {
                        "success": True,
                        "files": file_count,
                        "output_dir": str(lang_output)
                    }
                    logger.info(f"✅ Generated {file_count} files for {language}")
                else:
                    errors.append(f"{language}: {result.stderr}")
                    results[language] = {
                        "success": False,
                        "error": result.stderr
                    }
            
            except Exception as e:
                errors.append(f"{language}: {str(e)}")
                results[language] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": len(errors) == 0,
            "languages": results,
            "errors": errors
        }
    
    def validate(self, semantic_file: str) -> Dict[str, Any]:
        """Validate semantic convention file"""
        
        semantic_path = Path(semantic_file)
        if not semantic_path.exists():
            return {"valid": False, "error": "File not found"}
        
        try:
            # Basic YAML validation
            with open(semantic_path) as f:
                data = yaml.safe_load(f)
            
            # Check for required fields
            if not isinstance(data, dict):
                return {"valid": False, "error": "Invalid YAML structure"}
            
            if "groups" not in data:
                return {"valid": False, "error": "Missing 'groups' field"}
            
            # Use weaver to validate if available
            cmd = [self.weaver_binary, "validate", "-f", str(semantic_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                "valid": result.returncode == 0,
                "message": result.stdout if result.returncode == 0 else result.stderr
            }
            
        except yaml.YAMLError as e:
            return {"valid": False, "error": f"YAML parse error: {e}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}


# CLI Commands - Only the essentials

@app.command()
def generate(
    semantic_file: str = typer.Argument(help="Path to semantic convention YAML"),
    languages: List[str] = typer.Option(["python"], "--language", "-l", help="Target languages"),
    output_dir: str = typer.Option("./generated", "--output", "-o", help="Output directory"),
):
    """Generate code from semantic conventions"""
    
    try:
        console.print(f"[cyan]🚀 Generating code for: {', '.join(languages)}[/cyan]")
        
        gen = WeaverGen()
        results = gen.generate(semantic_file, languages, output_dir)
        
        # Display results
        table = Table(title="Generation Results")
        table.add_column("Language", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Files", style="blue")
        table.add_column("Location", style="yellow")
        
        for lang, result in results["languages"].items():
            status = "✅ Success" if result["success"] else "❌ Failed"
            files = str(result.get("files", 0)) if result["success"] else "-"
            location = result.get("output_dir", "-") if result["success"] else result.get("error", "Unknown error")[:30]
            
            table.add_row(lang, status, files, location)
        
        console.print(table)
        
        if results["errors"]:
            console.print("\n[red]Errors:[/red]")
            for error in results["errors"]:
                console.print(f"  • {error}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    semantic_file: str = typer.Argument(help="Path to semantic convention YAML"),
):
    """Validate semantic convention file"""
    
    try:
        console.print(f"[cyan]🔍 Validating: {semantic_file}[/cyan]")
        
        gen = WeaverGen()
        result = gen.validate(semantic_file)
        
        if result["valid"]:
            console.print(f"[green]✅ Valid semantic convention file[/green]")
            if result.get("message"):
                console.print(f"[dim]{result['message']}[/dim]")
        else:
            console.print(f"[red]❌ Invalid semantic convention file[/red]")
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            if result.get("message"):
                console.print(f"[dim]{result['message']}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def install():
    """Install weaver binary using cargo"""
    
    console.print("[cyan]📦 Installing OTel Weaver...[/cyan]")
    
    # Check if cargo is available
    if not shutil.which("cargo"):
        console.print("[red]❌ Cargo not found. Please install Rust first.[/red]")
        console.print("[yellow]Visit: https://rustup.rs[/yellow]")
        raise typer.Exit(1)
    
    try:
        # Install weaver
        result = subprocess.run(
            ["cargo", "install", "weaver-forge"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            console.print("[green]✅ Weaver installed successfully![/green]")
            
            # Verify installation
            gen = WeaverGen()
            console.print(f"[green]📍 Weaver location: {gen.weaver_binary}[/green]")
        else:
            console.print(f"[red]❌ Installation failed: {result.stderr}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info():
    """Show WeaverGen information"""
    
    try:
        gen = WeaverGen()
        
        console.print("[bold cyan]WeaverGen 80/20 - Simple Semantic Code Generation[/bold cyan]")
        console.print(f"[green]✅ Weaver binary: {gen.weaver_binary}[/green]")
        
        # Get weaver version
        result = subprocess.run(
            [gen.weaver_binary, "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            console.print(f"[green]📦 Weaver version: {result.stdout.strip()}[/green]")
        
        console.print("\n[yellow]Usage:[/yellow]")
        console.print("  weavergen generate semantic.yaml -l python -l go")
        console.print("  weavergen validate semantic.yaml")
        console.print("  weavergen install")
        
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/red]")
        console.print("[yellow]Run 'weavergen install' to install the weaver binary[/yellow]")


# Optional: Simple LLM enhancement (only if actually needed)

def enhance_with_llm(semantic_file: str, model: str = "llama3") -> Optional[str]:
    """Optional: Enhance semantic conventions with LLM suggestions"""
    
    # Only implement if users actually ask for this
    # Keep it simple - one function, not 20 agents
    pass


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )
    
    app()