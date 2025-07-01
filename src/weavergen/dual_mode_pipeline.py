"""
Dual-Mode Pipeline - Works with or without Weaver binary

This module implements a pipeline that can generate code using either:
1. Weaver binary (when available) for full compatibility
2. Direct parsing + AI generation (fallback mode)
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
import json

from .semantic_parser import SemanticConventionParser, SemanticConvention
from .template_learner import TemplateExtractor, CodePattern
from .layers.contracts import GenerationRequest, GenerationResult
from .layers.runtime import WeaverRuntime, TemplateEngine
from .examples.sql_generation import create_sql_agent


@dataclass
class PipelineConfig:
    """Configuration for the dual-mode pipeline."""
    prefer_weaver: bool = True
    weaver_binary_path: Optional[Path] = None
    use_ai_enhancement: bool = True
    template_dir: Path = Path("templates")
    output_dir: Path = Path("generated")
    cache_templates: bool = True


class DualModePipeline:
    """Pipeline that works with or without Weaver binary."""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.weaver_available = self._check_weaver()
        self.parser = SemanticConventionParser()
        self.template_extractor = TemplateExtractor()
        self.ai_agent = None
        
        # Initialize components
        self._setup_pipeline()
    
    def _check_weaver(self) -> bool:
        """Check if Weaver binary is available."""
        if self.config.weaver_binary_path:
            return self.config.weaver_binary_path.exists()
        
        # Check common locations
        weaver_cmd = shutil.which("weaver")
        if weaver_cmd:
            self.config.weaver_binary_path = Path(weaver_cmd)
            return True
        
        # Check project-specific locations
        possible_paths = [
            Path("bin/weaver"),
            Path("tools/weaver"),
            Path("../weaver/weaver"),
            Path.home() / ".local/bin/weaver"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.config.weaver_binary_path = path
                return True
        
        return False
    
    def _setup_pipeline(self) -> None:
        """Initialize pipeline components."""
        # Extract templates from existing code
        if self.config.cache_templates:
            self.templates = self.template_extractor.analyze_directory()
        
        # Initialize AI agent if requested
        if self.config.use_ai_enhancement:
            try:
                self.ai_agent = self._create_ai_agent()
            except ImportError:
                print("AI enhancement unavailable - continuing without it")
                self.config.use_ai_enhancement = False
    
    def _create_ai_agent(self):
        """Create AI agent for code generation."""
        try:
            from pydantic_ai import Agent
            
            return Agent(
                "ollama:llama3.2",
                system_prompt="""You are an expert at generating code from OpenTelemetry semantic conventions.
                Given a semantic convention, generate clean, type-safe code following these principles:
                1. Use Pydantic models for data validation
                2. Follow the 4-layer architecture pattern
                3. Include comprehensive docstrings
                4. Add type hints throughout
                5. Generate both the model and helper functions"""
            )
        except Exception as e:
            print(f"Could not create AI agent: {e}")
            return None
    
    def generate(self, 
                 convention_path: Union[str, Path],
                 target_languages: List[str] = ["python"],
                 force_mode: Optional[str] = None) -> GenerationResult:
        """
        Generate code from semantic convention.
        
        Args:
            convention_path: Path to semantic convention YAML
            target_languages: List of target languages
            force_mode: Force specific mode ('weaver', 'direct', or None for auto)
        
        Returns:
            GenerationResult with generated code
        """
        convention_path = Path(convention_path)
        
        # Determine generation mode
        use_weaver = self._should_use_weaver(force_mode)
        
        print(f"🚀 Generating from {convention_path.name}")
        print(f"📊 Mode: {'Weaver' if use_weaver else 'Direct'} generation")
        
        if use_weaver:
            return self._generate_with_weaver(convention_path, target_languages)
        else:
            return self._generate_direct(convention_path, target_languages)
    
    def _should_use_weaver(self, force_mode: Optional[str]) -> bool:
        """Determine whether to use Weaver or direct generation."""
        if force_mode == "weaver":
            if not self.weaver_available:
                raise RuntimeError("Weaver forced but not available")
            return True
        elif force_mode == "direct":
            return False
        else:
            # Auto mode - use Weaver if available and preferred
            return self.weaver_available and self.config.prefer_weaver
    
    def _generate_with_weaver(self, 
                              convention_path: Path,
                              target_languages: List[str]) -> GenerationResult:
        """Generate using Weaver binary."""
        print("🔧 Using Weaver binary for generation")
        
        # Prepare Weaver command
        cmd = [
            str(self.config.weaver_binary_path),
            "forge",
            "generate",
            "-c", str(convention_path),
            "-o", str(self.config.output_dir),
        ]
        
        for lang in target_languages:
            cmd.extend(["-l", lang])
        
        try:
            # Run Weaver
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Collect generated files
            generated_files = list(self.config.output_dir.glob("**/*"))
            
            return GenerationResult(
                success=True,
                files_generated=[str(f) for f in generated_files],
                logs=result.stdout,
                mode="weaver"
            )
            
        except subprocess.CalledProcessError as e:
            return GenerationResult(
                success=False,
                error=f"Weaver failed: {e.stderr}",
                logs=e.stdout,
                mode="weaver"
            )
    
    def _generate_direct(self,
                        convention_path: Path,
                        target_languages: List[str]) -> GenerationResult:
        """Generate using direct parsing and templates."""
        print("🎯 Using direct generation (no Weaver required)")
        
        generated_files = []
        logs = []
        
        try:
            # Parse semantic convention
            conventions = self.parser.parse_file(convention_path)
            logs.append(f"Parsed {len(conventions)} conventions")
            
            for lang in target_languages:
                if lang == "python":
                    files = self._generate_python(conventions)
                    generated_files.extend(files)
                else:
                    logs.append(f"Warning: {lang} generation not yet implemented in direct mode")
            
            # Apply AI enhancement if available
            if self.config.use_ai_enhancement and self.ai_agent:
                enhanced_files = self._enhance_with_ai(conventions, generated_files)
                generated_files.extend(enhanced_files)
                logs.append("Applied AI enhancement")
            
            return GenerationResult(
                success=True,
                files_generated=generated_files,
                logs="\n".join(logs),
                mode="direct"
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
                logs="\n".join(logs),
                mode="direct"
            )
    
    def _generate_python(self, conventions: List[SemanticConvention]) -> List[str]:
        """Generate Python code from conventions."""
        generated = []
        
        # Generate Pydantic models
        models_code = self.parser.generate_pydantic_models(conventions)
        models_path = self.config.output_dir / "models.py"
        models_path.parent.mkdir(parents=True, exist_ok=True)
        models_path.write_text(models_code)
        generated.append(str(models_path))
        
        # Generate helper functions using templates
        if self.templates.get('function'):
            helpers_code = self._generate_helpers(conventions)
            helpers_path = self.config.output_dir / "helpers.py"
            helpers_path.write_text(helpers_code)
            generated.append(str(helpers_path))
        
        # Generate validation code
        validation_code = self._generate_validation(conventions)
        validation_path = self.config.output_dir / "validation.py"
        validation_path.write_text(validation_code)
        generated.append(str(validation_path))
        
        return generated
    
    def _generate_helpers(self, conventions: List[SemanticConvention]) -> str:
        """Generate helper functions using learned templates."""
        code_lines = [
            '"""Helper functions for semantic conventions."""',
            '',
            'from typing import Dict, Any',
            'from .models import *',
            '',
        ]
        
        # Use function templates to generate helpers
        func_template = self.templates.get('function', [{}])[0]
        
        for convention in conventions:
            # Generate creation helper
            code_lines.append(f'def create_{convention.id.replace(".", "_")}(**kwargs) -> {convention.class_name}:')
            code_lines.append(f'    """Create {convention.brief}"""')
            code_lines.append(f'    return {convention.class_name}(**kwargs)')
            code_lines.append('')
            
            # Generate validation helper
            code_lines.append(f'def validate_{convention.id.replace(".", "_")}(data: Dict[str, Any]) -> bool:')
            code_lines.append(f'    """Validate {convention.brief}"""')
            code_lines.append('    try:')
            code_lines.append(f'        {convention.class_name}(**data)')
            code_lines.append('        return True')
            code_lines.append('    except Exception:')
            code_lines.append('        return False')
            code_lines.append('')
        
        return '\n'.join(code_lines)
    
    def _generate_validation(self, conventions: List[SemanticConvention]) -> str:
        """Generate validation code for conventions."""
        code_lines = [
            '"""Validation for semantic conventions."""',
            '',
            'from typing import List, Dict, Any',
            'from .models import *',
            '',
            '',
            'class ConventionValidator:',
            '    """Validates semantic convention compliance."""',
            '    ',
            '    def __init__(self):',
            '        self.conventions = {',
        ]
        
        # Register conventions
        for conv in conventions:
            code_lines.append(f'            "{conv.id}": {conv.class_name},')
        
        code_lines.extend([
            '        }',
            '    ',
            '    def validate(self, convention_id: str, data: Dict[str, Any]) -> bool:',
            '        """Validate data against convention."""',
            '        if convention_id not in self.conventions:',
            '            return False',
            '        try:',
            '            self.conventions[convention_id](**data)',
            '            return True',
            '        except Exception:',
            '            return False',
            ''
        ])
        
        return '\n'.join(code_lines)
    
    def _enhance_with_ai(self, 
                        conventions: List[SemanticConvention],
                        existing_files: List[str]) -> List[str]:
        """Enhance generated code with AI."""
        enhanced = []
        
        if not self.ai_agent:
            return enhanced
        
        for convention in conventions[:1]:  # Limit for demo
            prompt = f"""Generate advanced helper code for the {convention.id} semantic convention.
            Include:
            1. Builder pattern for easy construction
            2. Validation with detailed error messages
            3. Serialization helpers
            4. OTEL span integration
            
            Convention details:
            {convention.model_dump_json(indent=2)}
            """
            
            try:
                response = self.ai_agent.run_sync(prompt)
                enhanced_path = self.config.output_dir / f"{convention.id.replace('.', '_')}_enhanced.py"
                enhanced_path.write_text(response.data)
                enhanced.append(str(enhanced_path))
            except Exception as e:
                print(f"AI enhancement failed for {convention.id}: {e}")
        
        return enhanced
    
    def validate_generation(self, result: GenerationResult) -> bool:
        """Validate the generated code."""
        if not result.success:
            return False
        
        # Run basic validation
        for file_path in result.files_generated:
            if file_path.endswith('.py'):
                try:
                    # Compile to check syntax
                    with open(file_path, 'r') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError:
                    print(f"Syntax error in {file_path}")
                    return False
        
        return True


# CLI Integration
def add_dual_mode_commands(app):
    """Add dual-mode commands to CLI."""
    import typer
    
    @app.command()
    def generate_smart(
        convention: Path = typer.Argument(..., help="Path to semantic convention YAML"),
        languages: List[str] = typer.Option(["python"], "-l", "--language"),
        mode: Optional[str] = typer.Option(None, "--mode", help="Force mode: weaver, direct, or auto"),
        output: Path = typer.Option(Path("generated"), "-o", "--output"),
        no_ai: bool = typer.Option(False, "--no-ai", help="Disable AI enhancement")
    ):
        """Generate code using smart dual-mode pipeline."""
        from rich import print as rprint
        
        config = PipelineConfig(
            output_dir=output,
            use_ai_enhancement=not no_ai
        )
        
        pipeline = DualModePipeline(config)
        
        rprint(f"[bold cyan]🚀 WeaverGen Smart Generation[/bold cyan]")
        rprint(f"📁 Convention: {convention}")
        rprint(f"🎯 Languages: {', '.join(languages)}")
        rprint(f"🤖 AI Enhancement: {'Enabled' if not no_ai else 'Disabled'}")
        
        result = pipeline.generate(convention, languages, mode)
        
        if result.success:
            rprint(f"[green]✅ Generation successful![/green]")
            rprint(f"📊 Mode used: {result.mode}")
            rprint(f"📁 Files generated: {len(result.files_generated)}")
            for file in result.files_generated:
                rprint(f"  - {file}")
        else:
            rprint(f"[red]❌ Generation failed: {result.error}[/red]")
    
    return app


if __name__ == "__main__":
    # Test the pipeline
    pipeline = DualModePipeline()
    print(f"Weaver available: {pipeline.weaver_available}")
    
    # Test with a sample convention
    test_path = Path("test_semantic.yaml")
    if test_path.exists():
        result = pipeline.generate(test_path, force_mode="direct")
        print(f"Generation {'succeeded' if result.success else 'failed'}")
        print(f"Mode: {result.mode}")
        print(f"Files: {result.files_generated}")