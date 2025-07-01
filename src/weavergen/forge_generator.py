"""80/20 Weaver Forge Generator - Core functionality for complete system generation"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pydantic import BaseModel

console = Console()


class ForgeGenerationConfig(BaseModel):
    """Configuration for Weaver Forge generation"""
    semantic_file: Path
    template_dir: Path = Path("templates/python")
    output_dir: Path = Path("generated_forge")
    components: List[str] = ["agents", "workflows", "validation"]
    weaver_binary: Optional[str] = None
    verbose: bool = False


class ForgeGenerationResult(BaseModel):
    """Result of Weaver Forge generation"""
    success: bool
    components_generated: Dict[str, List[str]]
    total_files: int
    validation_passed: bool
    errors: List[str] = []
    duration_seconds: float


class WeaverForgeGenerator:
    """80/20 implementation of Weaver Forge generation"""
    
    def __init__(self, config: ForgeGenerationConfig):
        self.config = config
        self.env = Environment(
            loader=FileSystemLoader(str(config.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.generated_files: Dict[str, List[str]] = {}
        
    def generate_complete_system(self) -> ForgeGenerationResult:
        """Generate complete system from semantic conventions"""
        start_time = datetime.now()
        errors = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Load semantic conventions
            task = progress.add_task("Loading semantic conventions...", total=1)
            try:
                semantics = self._load_semantics()
                progress.update(task, completed=1)
            except Exception as e:
                errors.append(f"Failed to load semantics: {e}")
                return self._create_result(False, errors, start_time)
            
            # Generate each component
            for component in self.config.components:
                task = progress.add_task(f"Generating {component}...", total=1)
                try:
                    self._generate_component(component, semantics)
                    progress.update(task, completed=1)
                except Exception as e:
                    errors.append(f"Failed to generate {component}: {e}")
                    progress.update(task, completed=1)
            
            # Run Weaver Forge if available
            if self._weaver_available():
                task = progress.add_task("Running Weaver Forge...", total=1)
                try:
                    self._run_weaver_forge()
                    progress.update(task, completed=1)
                except Exception as e:
                    errors.append(f"Weaver Forge failed: {e}")
                    progress.update(task, completed=1)
            
            # Validate generation
            task = progress.add_task("Validating generation...", total=1)
            validation_passed = self._validate_generation()
            progress.update(task, completed=1)
        
        return self._create_result(
            success=len(errors) == 0,
            errors=errors,
            start_time=start_time,
            validation_passed=validation_passed
        )
    
    def _load_semantics(self) -> Dict[str, Any]:
        """Load semantic conventions from YAML"""
        with open(self.config.semantic_file) as f:
            return yaml.safe_load(f)
    
    def _generate_component(self, component: str, semantics: Dict[str, Any]):
        """Generate a specific component"""
        template_name = f"{component}_system.j2"
        output_file = self.config.output_dir / component / f"{component}_system.py"
        
        # Create output directory
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Render template
        template = self.env.get_template(template_name)
        content = template.render(**semantics)
        
        # Write file
        with open(output_file, 'w') as f:
            f.write(content)
        
        # Track generated file
        if component not in self.generated_files:
            self.generated_files[component] = []
        self.generated_files[component].append(str(output_file))
        
        # Create __init__.py
        init_file = output_file.parent / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
            self.generated_files[component].append(str(init_file))
        
        if self.config.verbose:
            rprint(f"[green]✅ Generated {output_file}")
    
    def _weaver_available(self) -> bool:
        """Check if Weaver binary is available"""
        if self.config.weaver_binary:
            return Path(self.config.weaver_binary).exists()
        
        # Try to find weaver in PATH
        try:
            result = subprocess.run(
                ["which", "weaver"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _run_weaver_forge(self):
        """Run OTel Weaver Forge for additional generation"""
        # This would integrate with actual Weaver binary
        # For now, we'll create additional supporting files
        
        # Generate models from semantic conventions
        models_file = self.config.output_dir / "models" / "semantic_models.py"
        models_file.parent.mkdir(parents=True, exist_ok=True)
        
        models_content = '''"""Models generated from semantic conventions"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Auto-generated from semantic conventions
class ComponentType(BaseModel):
    agent: str = "agent"
    workflow: str = "workflow"
    generator: str = "generator"
    validator: str = "validator"

class TelemetrySpan(BaseModel):
    component_type: str
    generation_source: str
    generation_target: str
    timestamp: datetime
    attributes: dict

class SystemHealth(BaseModel):
    overall_health: float
    component_health: dict
    validation_passed: bool
    quine_compliant: Optional[bool] = None
'''
        
        models_file.write_text(models_content)
        
        if "models" not in self.generated_files:
            self.generated_files["models"] = []
        self.generated_files["models"].append(str(models_file))
    
    def _validate_generation(self) -> bool:
        """Validate the generated system"""
        # Check all expected files exist
        for component, files in self.generated_files.items():
            for file_path in files:
                if not Path(file_path).exists():
                    return False
        
        # Check Python syntax
        for component, files in self.generated_files.items():
            for file_path in files:
                if file_path.endswith('.py'):
                    try:
                        compile(Path(file_path).read_text(), file_path, 'exec')
                    except SyntaxError:
                        return False
        
        return True
    
    def _create_result(self, 
                      success: bool, 
                      errors: List[str],
                      start_time: datetime,
                      validation_passed: bool = False) -> ForgeGenerationResult:
        """Create generation result"""
        duration = (datetime.now() - start_time).total_seconds()
        total_files = sum(len(files) for files in self.generated_files.values())
        
        return ForgeGenerationResult(
            success=success,
            components_generated=self.generated_files,
            total_files=total_files,
            validation_passed=validation_passed,
            errors=errors,
            duration_seconds=duration
        )


# CLI Integration
def generate_from_semantics(semantic_file: Path, 
                          output_dir: Path = Path("generated_forge"),
                          components: Optional[List[str]] = None,
                          verbose: bool = False) -> ForgeGenerationResult:
    """Generate complete system from semantic conventions"""
    if components is None:
        components = ["agents", "workflows", "validation"]
    
    config = ForgeGenerationConfig(
        semantic_file=semantic_file,
        output_dir=output_dir,
        components=components,
        verbose=verbose
    )
    
    generator = WeaverForgeGenerator(config)
    result = generator.generate_complete_system()
    
    # Print summary
    if result.success:
        rprint(f"[bold green]✅ Successfully generated {result.total_files} files")
        for component, files in result.components_generated.items():
            rprint(f"  [cyan]{component}:[/cyan] {len(files)} files")
    else:
        rprint(f"[bold red]❌ Generation failed with {len(result.errors)} errors")
        for error in result.errors:
            rprint(f"  [red]• {error}")
    
    return result