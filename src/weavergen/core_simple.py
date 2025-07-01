#!/usr/bin/env python3
"""
80/20 Core Implementation of WeaverGen

Simple, direct implementation that just works - no over-engineering.
Focuses on the core JTBD: Generate code from semantic conventions quickly.
"""

import subprocess
import shutil
import json
import yaml
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import tempfile
import time

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


@dataclass
class GenerationResult:
    """Simple result of code generation."""
    success: bool
    files_generated: List[Path]
    execution_time: float
    error: Optional[str] = None
    weaver_output: Optional[str] = None


class WeaverGen:
    """
    Simple, direct implementation of WeaverGen.
    
    80/20 approach: Focus on what matters most.
    - Find and run Weaver
    - Process templates
    - Generate files
    - Show progress
    """
    
    def __init__(self):
        """Initialize WeaverGen with minimal setup."""
        self.weaver_path = self._find_weaver()
        self.templates_dir = Path(__file__).parent / "templates"
        
    def _find_weaver(self) -> Optional[Path]:
        """Find the Weaver binary in common locations."""
        # Check if weaver is in PATH
        weaver_in_path = shutil.which("weaver")
        if weaver_in_path:
            return Path(weaver_in_path)
        
        # Also check for weaver-forge in PATH
        weaver_forge_in_path = shutil.which("weaver-forge")
        if weaver_forge_in_path:
            return Path(weaver_forge_in_path)
        
        # Check common installation locations
        common_paths = [
            Path.home() / ".cargo" / "bin" / "weaver",
            Path.home() / ".cargo" / "bin" / "weaver-forge",
            Path("/usr/local/bin/weaver"),
            Path("/usr/local/bin/weaver-forge"),
            Path("/opt/homebrew/bin/weaver"),
            Path("/opt/homebrew/bin/weaver-forge"),
        ]
        
        for path in common_paths:
            if path.exists() and path.is_file():
                return path
        
        return None
    
    def check_requirements(self) -> Tuple[bool, List[str]]:
        """Check if all requirements are met."""
        issues = []
        
        # Check Weaver
        if not self.weaver_path:
            issues.append("❌ Weaver not found. Install with: cargo install weaver-forge")
        else:
            # Check if weaver works
            try:
                result = subprocess.run(
                    [str(self.weaver_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    issues.append(f"❌ Weaver not working: {result.stderr}")
            except Exception as e:
                issues.append(f"❌ Weaver error: {e}")
        
        # Check templates
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            issues.append("⚠️ Templates directory created - add templates for better output")
        
        return len(issues) == 0, issues
    
    async def generate(
        self,
        semantic_file: str,
        target_languages: List[str],
        output_dir: str = "./generated"
    ) -> GenerationResult:
        """
        Generate code from semantic conventions.
        
        Simple approach:
        1. Validate inputs
        2. Run Weaver for each language
        3. Collect generated files
        4. Return results
        """
        start_time = time.time()
        
        # Validate inputs
        semantic_path = Path(semantic_file)
        if not semantic_path.exists():
            return GenerationResult(
                success=False,
                files_generated=[],
                execution_time=time.time() - start_time,
                error=f"Semantic file not found: {semantic_file}"
            )
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Check if weaver is available
        if not self.weaver_path:
            return GenerationResult(
                success=False,
                files_generated=[],
                execution_time=time.time() - start_time,
                error="Weaver not found. Install with: cargo install weaver-forge"
            )
        
        generated_files = []
        weaver_outputs = []
        
        # Generate for each language
        for language in target_languages:
            console.print(f"🔧 Generating {language} code...")
            
            try:
                # Create language-specific output directory
                lang_output = output_path / language
                lang_output.mkdir(exist_ok=True)
                
                # Get template for language
                template = self._get_template_for_language(language)
                
                # Run Weaver
                # For now, we'll use a simple approach - just generate with defaults
                # In a real implementation, we'd need proper template management
                cmd = [
                    str(self.weaver_path),
                    "registry",
                    "generate",
                    language,  # Target is the language
                    str(lang_output),  # Output directory
                    "-r", str(semantic_path.parent),  # Registry path
                    "--quiet",
                    "--skip-policies"
                ]
                
                # Look for templates in the project directory first
                project_templates = semantic_path.parent.parent.parent / "templates"
                if project_templates.exists():
                    cmd.extend(["-t", str(project_templates)])
                elif template and template.parent.exists():
                    cmd.extend(["-t", str(template.parent.parent.parent)])
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Find generated files
                    for file_path in lang_output.rglob("*"):
                        if file_path.is_file():
                            generated_files.append(file_path)
                    
                    weaver_outputs.append(f"{language}: {result.stdout}")
                    console.print(f"  ✅ {language} generation complete")
                else:
                    console.print(f"  ❌ {language} generation failed: {result.stderr}")
                    weaver_outputs.append(f"{language} ERROR: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                console.print(f"  ❌ {language} generation timed out")
                weaver_outputs.append(f"{language}: TIMEOUT")
            except Exception as e:
                console.print(f"  ❌ {language} generation error: {e}")
                weaver_outputs.append(f"{language} ERROR: {str(e)}")
        
        execution_time = time.time() - start_time
        
        return GenerationResult(
            success=len(generated_files) > 0,
            files_generated=generated_files,
            execution_time=execution_time,
            weaver_output="\n".join(weaver_outputs),
            error=None if generated_files else "No files generated"
        )
    
    def _get_template_for_language(self, language: str) -> Optional[Path]:
        """Get template path for a language."""
        # Map language to template
        template_map = {
            "python": "python_models.j2",
            "go": "go_models.j2",
            "java": "java_models.j2",
            "rust": "rust_models.j2",
            "typescript": "typescript_models.j2",
            "javascript": "javascript_models.j2"
        }
        
        template_name = template_map.get(language.lower())
        if not template_name:
            return None
        
        template_path = self.templates_dir / template_name
        if template_path.exists():
            return template_path
        
        # Create a basic template if it doesn't exist
        self._create_basic_template(template_path, language)
        return template_path
    
    def _create_basic_template(self, template_path: Path, language: str):
        """Create a basic template for a language."""
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Basic template content
        if language == "python":
            content = """# Generated from {{ semantic.id }}
\"\"\"{{ semantic.brief }}\"\"\"

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

{% for attribute in semantic.attributes %}
@dataclass
class {{ attribute.name | pascal_case }}:
    \"\"\"{{ attribute.brief }}\"\"\"
    {% for field in attribute.fields %}
    {{ field.name }}: {{ field.type | python_type }}
    {% endfor %}
{% endfor %}
"""
        elif language == "go":
            content = """// Generated from {{ semantic.id }}
// {{ semantic.brief }}

package models

{% for attribute in semantic.attributes %}
// {{ attribute.name | pascal_case }} - {{ attribute.brief }}
type {{ attribute.name | pascal_case }} struct {
    {% for field in attribute.fields %}
    {{ field.name | pascal_case }} {{ field.type | go_type }} `json:"{{ field.name }}"`
    {% endfor %}
}
{% endfor %}
"""
        else:
            content = f"// Basic template for {language}\n// TODO: Implement proper template"
        
        template_path.write_text(content)
    
    async def validate_output(self, generated_files: List[Path]) -> Dict[str, Any]:
        """Simple validation of generated files."""
        validation_results = {
            "total_files": len(generated_files),
            "valid_files": 0,
            "issues": []
        }
        
        for file_path in generated_files:
            try:
                # Basic validation - file exists and has content
                if file_path.exists() and file_path.stat().st_size > 0:
                    validation_results["valid_files"] += 1
                    
                    # Language-specific validation
                    if file_path.suffix == ".py":
                        # Try to compile Python code
                        compile(file_path.read_text(), str(file_path), 'exec')
                    elif file_path.suffix == ".go":
                        # Could run go fmt -n for validation
                        pass
                else:
                    validation_results["issues"].append(f"Empty file: {file_path}")
                    
            except SyntaxError as e:
                validation_results["issues"].append(f"Syntax error in {file_path}: {e}")
            except Exception as e:
                validation_results["issues"].append(f"Error validating {file_path}: {e}")
        
        validation_results["success_rate"] = (
            validation_results["valid_files"] / validation_results["total_files"] * 100
            if validation_results["total_files"] > 0 else 0
        )
        
        return validation_results


async def generate_code(
    semantic_file: str,
    languages: List[str],
    output_dir: str = "./generated"
) -> None:
    """Simple entry point for code generation."""
    
    console.print(Panel(
        f"""🚀 WeaverGen Code Generation (80/20 Edition)
        
📄 Semantic File: {semantic_file}
🎯 Languages: {', '.join(languages)}
📁 Output: {output_dir}""",
        title="Generation Configuration",
        border_style="blue"
    ))
    
    # Initialize generator
    generator = WeaverGen()
    
    # Check requirements
    ready, issues = generator.check_requirements()
    if not ready:
        console.print("\n[red]⚠️ Requirements Check Failed:[/red]")
        for issue in issues:
            console.print(f"  {issue}")
        
        if not generator.weaver_path:
            console.print("\n[yellow]To install Weaver:[/yellow]")
            console.print("  cargo install weaver-forge")
            console.print("  # or")
            console.print("  brew install weaver-forge")
        return
    
    # Generate code with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("Generating code...", total=len(languages))
        
        result = await generator.generate(semantic_file, languages, output_dir)
        
        progress.update(task, completed=len(languages))
    
    # Show results
    if result.success:
        console.print(Panel(
            f"""✅ Code Generation Successful!
            
📊 Files Generated: {len(result.files_generated)}
⏱️ Execution Time: {result.execution_time:.2f}s
📁 Output Directory: {output_dir}""",
            title="Generation Complete",
            border_style="green"
        ))
        
        # List generated files
        console.print("\n📄 Generated Files:")
        for file_path in result.files_generated:
            relative_path = file_path.relative_to(Path(output_dir))
            console.print(f"  ✓ {relative_path}")
        
        # Validate output
        console.print("\n🔍 Validating output...")
        validation = await generator.validate_output(result.files_generated)
        
        console.print(f"  ✅ Valid files: {validation['valid_files']}/{validation['total_files']}")
        console.print(f"  📊 Success rate: {validation['success_rate']:.1f}%")
        
        if validation['issues']:
            console.print("\n⚠️ Validation Issues:")
            for issue in validation['issues'][:5]:  # Show first 5 issues
                console.print(f"  • {issue}")
    else:
        console.print(Panel(
            f"""❌ Code Generation Failed
            
Error: {result.error}

Weaver Output:
{result.weaver_output}""",
            title="Generation Failed",
            border_style="red"
        ))


# Example usage
async def main():
    """Example usage of the 80/20 WeaverGen implementation."""
    
    # Create a sample semantic convention file
    sample_semantic = {
        "id": "http.server",
        "brief": "HTTP server semantic conventions",
        "attributes": [
            {
                "name": "http.request.method",
                "type": "string",
                "brief": "HTTP request method",
                "examples": ["GET", "POST", "PUT", "DELETE"]
            },
            {
                "name": "http.response.status_code",
                "type": "int",
                "brief": "HTTP response status code",
                "examples": [200, 404, 500]
            }
        ]
    }
    
    # Write sample file
    sample_file = Path("sample_semantic.yaml")
    with open(sample_file, "w") as f:
        yaml.dump(sample_semantic, f)
    
    # Generate code
    await generate_code(
        str(sample_file),
        ["python", "go"],
        "./generated_80_20"
    )


if __name__ == "__main__":
    asyncio.run(main())