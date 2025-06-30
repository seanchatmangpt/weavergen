#!/usr/bin/env python3
"""
Generate Pydantic models from semantic conventions using Weaver.
This is the core of the working loop.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import yaml
import black
from rich.console import Console

try:
    # When imported as module
    from .core import WeaverGen
    from .models import GenerationConfig, GenerationResult
except ImportError:
    # When run directly
    from weavergen.core import WeaverGen
    from weavergen.models import GenerationConfig, GenerationResult

console = Console()


def create_temp_registry(semantic_yaml: Path) -> Path:
    """Create a temporary registry structure for Weaver."""
    temp_dir = Path.cwd() / "temp_registry"
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
        
    registry_dir = temp_dir
    registry_dir.mkdir(parents=True)
    
    # Create registry structure - just put the file directly in the registry
    target = registry_dir / semantic_yaml.name
    target.write_text(semantic_yaml.read_text())
    
    return registry_dir


def generate_pydantic_models(
    semantic_yaml: Path,
    output_dir: Path,
    weaver_path: Optional[Path] = None
) -> GenerationResult:
    """Generate Pydantic models from semantic conventions."""
    
    console.print(f"[blue]Generating Pydantic models from {semantic_yaml}[/blue]")
    
    # Create temporary registry
    try:
        # If it's already a registry, use it directly
        if (semantic_yaml.parent.name == "groups" and 
            (semantic_yaml.parent.parent / "manifest.yaml").exists()):
            registry_path = semantic_yaml.parent.parent
            console.print("[green]Using existing registry structure[/green]")
        else:
            registry_path = create_temp_registry(semantic_yaml)
            console.print("[green]Created temporary registry[/green]")
        
        # Get template directory
        template_dir = Path(__file__).parent.parent.parent / "templates"
        if not template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        
        # Create config
        config = GenerationConfig(
            registry_url=str(registry_path),
            output_dir=output_dir,
            language="pydantic",  # Our custom target
            template_dir=template_dir,
            force=True,
            verbose=True
        )
        
        # Configure Weaver with our config
        weaver = WeaverGen(config=config)
        if weaver_path:
            weaver._weaver_config.weaver_path = weaver_path
        
        # Generate using Weaver
        console.print("[blue]Running Weaver Forge...[/blue]")
        result = weaver.generate()
        
        if result.success:
            # Format generated Python files with black
            for file_info in result.files:
                if file_info.path.suffix == ".py":
                    try:
                        console.print(f"[blue]Formatting {file_info.path}[/blue]")
                        content = file_info.path.read_text()
                        formatted = black.format_str(content, mode=black.Mode())
                        file_info.path.write_text(formatted)
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not format {file_info.path}: {e}[/yellow]")
            
            console.print(f"[green]✅ Generated {len(result.files)} files[/green]")
        else:
            console.print(f"[red]❌ Generation failed: {str(result.error).replace('[', '\\[').replace(']', '\\]')}[/red]")
        
        return result
        
    except Exception as e:
        console.print(f"[red]Error: {str(e).replace('[', '\\[').replace(']', '\\]')}[/red]")
        return GenerationResult(
            success=False,
            error=str(e)
        )


def validate_generated_models(model_file: Path) -> bool:
    """Validate that generated models can be imported."""
    try:
        # Try to import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("generated_models", model_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        console.print(f"[green]✅ Models validated successfully[/green]")
        
        # List available models
        models = [name for name in dir(module) if name.endswith("Model") or name.endswith("Output")]
        console.print(f"[blue]Available models: {', '.join(models)}[/blue]")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        return False


if __name__ == "__main__":
    # Test with agents-ai.yaml
    semantic_file = Path("semantic-conventions/groups/agents-ai.yaml")
    output_dir = Path("generated/pydantic")
    
    if semantic_file.exists():
        result = generate_pydantic_models(semantic_file, output_dir)
        
        if result.success:
            # Validate the generated models
            model_file = output_dir / "pydantic" / "models.py"
            if model_file.exists():
                validate_generated_models(model_file)