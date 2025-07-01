#!/usr/bin/env python3
"""
WeaverGen CLI Extension
Semantic convention CLI commands
"""

import typer
import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from .layers.semantic_runtime import SemanticConventionRuntime

app = typer.Typer()
console = Console()

@app.command()
def generate_semantic(
    convention_file: str = typer.Argument(..., help="Path to semantic convention YAML/JSON file"),
    output_dir: str = typer.Option("generated", help="Output directory for generated code"),
    language: str = typer.Option("python", help="Target language for generation")
):
    """Generate code from semantic convention"""
    
    console.print(f"🚀 Generating code from convention: {convention_file}")
    
    runtime = SemanticConventionRuntime()
    
    try:
        result = asyncio.run(
            runtime.process_convention(
                Path(convention_file),
                Path(output_dir)
            )
        )
        
        if result["success"]:
            console.print("✅ Generation completed successfully!")
            console.print(f"📁 Generated files:")
            for file in result["generated_files"]:
                console.print(f"   - {file}")
        else:
            console.print("❌ Generation failed:")
            for error in result.get("errors", []):
                console.print(f"   - {error}")
    
    except Exception as e:
        console.print(f"❌ Error: {e}")

@app.command()
def validate_semantic(
    convention_file: str = typer.Argument(..., help="Path to semantic convention file"),
):
    """Validate semantic convention"""
    
    from .semantic_parser import SemanticConventionParser
    
    console.print(f"🔍 Validating convention: {convention_file}")
    
    parser = SemanticConventionParser()
    
    try:
        convention = parser.parse_convention_file(Path(convention_file))
        issues = parser.validate_convention(convention)
        
        if not issues:
            console.print("✅ Convention is valid!")
        else:
            console.print("⚠️ Validation issues found:")
            for issue in issues:
                console.print(f"   - {issue}")
    
    except Exception as e:
        console.print(f"❌ Error: {e}")

if __name__ == "__main__":
    app()
