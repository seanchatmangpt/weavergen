#!/usr/bin/env python3
"""
WeaverGen - Simple wrapper around OpenTelemetry Weaver
Transform semantic conventions to code in any language.

This is the entire solution in <300 lines. No BPMN, no AI, no complexity.
Just a simple wrapper that does exactly what users need.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import shutil

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

app = typer.Typer(
    name="weavergen",
    help="Generate code from OpenTelemetry semantic conventions",
    add_completion=False,
    no_args_is_help=True
)
console = Console()


class WeaverGen:
    """Dead simple wrapper around the weaver binary"""
    
    def __init__(self):
        self.weaver_path = self._find_weaver()
        if not self.weaver_path:
            console.print("[red]❌ Weaver not found. Run: python weavergen_simple.py install[/red]")
            sys.exit(1)
    
    def _find_weaver(self) -> Optional[str]:
        """Find weaver binary in PATH or cargo bin"""
        # Check PATH first
        if path := shutil.which("weaver"):
            return path
            
        # Check cargo bin
        cargo_bin = Path.home() / ".cargo" / "bin" / "weaver"
        if cargo_bin.exists():
            return str(cargo_bin)
            
        # Also check local development paths
        local_paths = [
            Path("./target/release/weaver"),
            Path("./target/debug/weaver"),
        ]
        for path in local_paths:
            if path.exists():
                return str(path)
            
        return None
    
    def generate(self, semantic_file: str, language: str, output_dir: str) -> bool:
        """Generate code for a single language"""
        # Map common language names to weaver template names
        template_map = {
            "python": "semantic_conventions/python",
            "go": "semantic_conventions/go", 
            "rust": "semantic_conventions/rust",
            "java": "semantic_conventions/java",
            "javascript": "semantic_conventions/javascript",
            "js": "semantic_conventions/javascript",
        }
        
        template = template_map.get(language, f"semantic_conventions/{language}")
        
        cmd = [
            self.weaver_path,
            "generate",
            template,
            output_dir,
            "--registry", semantic_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Error generating {language}: {result.stderr}[/red]")
            return False
            
        return True
    
    def validate(self, semantic_file: str) -> bool:
        """Validate semantic convention file"""
        # First check if file exists and is readable
        path = Path(semantic_file)
        if not path.exists():
            console.print(f"[red]File not found: {semantic_file}[/red]")
            return False
            
        # Run weaver check
        cmd = [
            self.weaver_path,
            "check",
            "--registry", semantic_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[yellow]Validation output: {result.stderr}[/yellow]")
            
        return result.returncode == 0
    

@app.command()
def generate(
    semantic_file: str = typer.Argument(..., help="Semantic convention YAML file"),
    languages: List[str] = typer.Option(["python"], "--language", "-l", help="Target languages"),
    output: str = typer.Option("./generated", "--output", "-o", help="Output directory"),
    validate_first: bool = typer.Option(True, "--validate/--no-validate", help="Validate before generating")
):
    """Generate code from semantic conventions"""
    
    console.print(f"\n🚀 [bold]WeaverGen Simple[/bold] - No complexity, just results")
    console.print(f"📄 Input: {semantic_file}")
    console.print(f"🎯 Languages: {', '.join(languages)}")
    console.print(f"📁 Output: {output}\n")
    
    # Check if semantic file exists
    if not Path(semantic_file).exists():
        console.print(f"[red]❌ File not found: {semantic_file}[/red]")
        sys.exit(1)
    
    weaver = WeaverGen()
    
    # Validate if requested
    if validate_first:
        with console.status("Validating semantic conventions..."):
            if not weaver.validate(semantic_file):
                console.print("[red]❌ Validation failed[/red]")
                sys.exit(1)
        console.print("[green]✅ Validation passed[/green]\n")
    
    # Generate for each language
    success_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Generating code...", total=len(languages))
        
        for lang in languages:
            progress.update(task, description=f"Generating {lang}...")
            
            output_path = Path(output) / lang
            output_path.mkdir(parents=True, exist_ok=True)
            
            if weaver.generate(semantic_file, lang, str(output_path)):
                success_count += 1
                console.print(f"  ✅ {lang} → {output_path}")
            else:
                console.print(f"  ❌ {lang} failed")
                
            progress.advance(task)
    
    # Summary
    console.print(f"\n✨ Generated {success_count}/{len(languages)} languages")
    if success_count == len(languages):
        console.print("[bold green]Success! All code generated.[/bold green]")
    else:
        console.print("[yellow]Some generations failed. Check error messages above.[/yellow]")
    

@app.command()
def validate(
    semantic_file: str = typer.Argument(..., help="Semantic convention YAML file")
):
    """Validate semantic convention file"""
    
    console.print(f"\n🔍 Validating: {semantic_file}")
    
    weaver = WeaverGen()
    if weaver.validate(semantic_file):
        console.print("[green]✅ Valid semantic convention file[/green]")
    else:
        console.print("[red]❌ Invalid semantic convention file[/red]")
        sys.exit(1)


@app.command()
def install():
    """Install the weaver binary via cargo"""
    
    console.print("\n📦 Installing OpenTelemetry Weaver...")
    
    # Check if cargo is available
    if not shutil.which("cargo"):
        console.print("[red]❌ Cargo not found. Install Rust first: https://rustup.rs[/red]")
        console.print("\nThen run: cargo install weaver-forge")
        sys.exit(1)
    
    # Install weaver
    cmd = ["cargo", "install", "weaver-forge"]
    console.print(f"Running: {' '.join(cmd)}\n")
    
    try:
        # Run installation with live output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in iter(process.stdout.readline, ''):
            if line:
                console.print(f"  {line.strip()}")
                
        process.wait()
        
        if process.returncode == 0:
            console.print("\n[green]✅ Weaver installed successfully![/green]")
            console.print("You can now use: python weavergen_simple.py generate")
        else:
            console.print("\n[red]❌ Installation failed[/red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled[/yellow]")
        sys.exit(1)


@app.command()
def list_languages():
    """List supported target languages"""
    
    languages = [
        ("python", ".py", "Python code generation"),
        ("go", ".go", "Go code generation"),
        ("rust", ".rs", "Rust code generation"),
        ("java", ".java", "Java code generation"),
        ("javascript", ".js", "JavaScript code generation"),
    ]
    
    table = Table(title="Supported Languages", show_header=True)
    table.add_column("Language", style="cyan", no_wrap=True)
    table.add_column("Extension", style="green")
    table.add_column("Description", style="dim")
    
    for lang, ext, desc in languages:
        table.add_row(lang, ext, desc)
    
    console.print("\n")
    console.print(table)
    console.print("\nUse: python weavergen_simple.py generate <file> -l <language>")


@app.command()
def version():
    """Show version information"""
    
    console.print("\n[bold]WeaverGen Simple[/bold]")
    console.print("Version: 0.1.0 (The 300-line version)")
    console.print("Purpose: Simple wrapper around OpenTelemetry Weaver")
    console.print("Philosophy: Do one thing well\n")
    
    # Try to get weaver version
    weaver = WeaverGen()
    if weaver.weaver_path:
        result = subprocess.run([weaver.weaver_path, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"Weaver: {result.stdout.strip()}")


if __name__ == "__main__":
    # Show header
    console.print("\n[bold blue]WeaverGen[/bold blue] - The simple semantic convention code generator")
    console.print("[dim]No BPMN, no AI, no complexity. Just works.[/dim]\n")
    
    # Run CLI
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)