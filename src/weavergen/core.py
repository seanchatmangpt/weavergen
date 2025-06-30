"""Core WeaverGen functionality."""

import json
import subprocess
import tempfile
import time
import importlib.util
from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil

# Import from original models.py file directly 
import sys
from pathlib import Path as PathLib
models_file = PathLib(__file__).parent / "models.py"
spec = importlib.util.spec_from_file_location("models", models_file)
models_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_module)

GenerationConfig = models_module.GenerationConfig
GenerationResult = models_module.GenerationResult
ValidationResult = models_module.ValidationResult
TemplateInfo = models_module.TemplateInfo
FileInfo = models_module.FileInfo

# Define missing classes
from pydantic import BaseModel
from typing import List, Optional

class WeaverConfig(BaseModel):
    """Weaver configuration."""
    weaver_path: Optional[str] = None
    
class WeaverCommand(BaseModel):
    """Weaver command."""
    command: str
    args: List[str] = []


class WeaverGenError(Exception):
    """Base exception for WeaverGen operations."""
    pass


class WeaverNotFoundError(WeaverGenError):
    """Raised when OTel Weaver binary cannot be found."""
    pass


class WeaverGen:
    """Python wrapper for OTel Weaver Forge with Claude Code optimization."""
    
    def __init__(self, config: Optional[GenerationConfig] = None):
        """Initialize WeaverGen with optional configuration."""
        self.config = config
        self._weaver_config = self._load_config()
        self._ensure_weaver_binary()
    
    def _load_config(self) -> WeaverConfig:
        """Load WeaverGen configuration from file or defaults."""
        config_file = Path.home() / ".weavergen" / "config.json"
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    data = json.load(f)
                return WeaverConfig(**data)
            except Exception:
                # Fall back to defaults if config is corrupted
                pass
        
        return WeaverConfig()
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        config_dir = Path.home() / ".weavergen"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(self._weaver_config.dict(), f, default=str, indent=2)
    
    def _ensure_weaver_binary(self) -> None:
        """Ensure OTel Weaver binary is available."""
        # Try configured path first
        if self._weaver_config.weaver_path:
            if self._weaver_config.weaver_path.exists():
                return
        
        # Try to find weaver in PATH
        weaver_path = shutil.which("weaver")
        if weaver_path:
            self._weaver_config.weaver_path = Path(weaver_path)
            return
        
        # Check common installation locations
        common_paths = [
            Path.home() / ".cargo" / "bin" / "weaver",
            Path("/usr/local/bin/weaver"),
            Path("/opt/homebrew/bin/weaver"),
        ]
        
        for path in common_paths:
            if path.exists():
                self._weaver_config.weaver_path = path
                self._save_config()
                return
        
        raise WeaverNotFoundError(
            "OTel Weaver binary not found. Please install it or set the path using 'weavergen config --weaver-path /path/to/weaver'"
        )
    
    def _run_weaver_command(self, command: WeaverCommand) -> subprocess.CompletedProcess:
        """Execute a weaver command and return the result."""
        if not self._weaver_config.weaver_path:
            raise WeaverNotFoundError("Weaver binary path not configured")
        
        cmd = [str(self._weaver_config.weaver_path)] + command.args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=command.cwd,
                env=command.env if command.env else None,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return result
        except subprocess.TimeoutExpired:
            raise WeaverGenError("Weaver command timed out")
        except FileNotFoundError:
            raise WeaverNotFoundError(f"Weaver binary not found at {self._weaver_config.weaver_path}")
    
    def generate(self) -> GenerationResult:
        """Generate code from semantic conventions using OTel Weaver Forge."""
        if not self.config:
            raise WeaverGenError("No generation configuration provided")
        
        start_time = time.time()
        
        try:
            # Ensure output directory exists
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build weaver forge command
            forge_args = [
                "forge",
                "--registry", str(self.config.registry_url),
                "--output", str(self.config.output_dir),
                "--language", self.config.language,
            ]
            
            if self.config.template_dir:
                forge_args.extend(["--templates", str(self.config.template_dir)])
            
            if self.config.force:
                forge_args.append("--force")
            
            if self.config.verbose:
                forge_args.append("--verbose")
            
            command = WeaverCommand(
                command="weaver",
                args=forge_args,
                cwd=self.config.output_dir.parent,
            )
            
            # Execute weaver forge command
            result = self._run_weaver_command(command)
            
            if result.returncode != 0:
                return GenerationResult(
                    success=False,
                    error=f"Weaver forge failed: {result.stderr}",
                    duration_seconds=time.time() - start_time,
                )
            
            # Collect information about generated files
            generated_files = []
            if self.config.output_dir.exists():
                for file_path in self.config.output_dir.rglob("*"):
                    if file_path.is_file():
                        stat = file_path.stat()
                        file_info = FileInfo(
                            path=file_path,
                            size=stat.st_size,
                            file_type=file_path.suffix.lstrip('.') or 'file',
                        )
                        generated_files.append(file_info)
            
            # Parse warnings from output
            warnings = []
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if 'warning:' in line.lower():
                        warnings.append(line.strip())
            
            return GenerationResult(
                success=True,
                files=generated_files,
                warnings=warnings,
                duration_seconds=time.time() - start_time,
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
                duration_seconds=time.time() - start_time,
            )
    
    def validate_registry(self, registry_path: Path, strict: bool = False) -> ValidationResult:
        """Validate a semantic convention registry."""
        command_args = ["registry", "check", str(registry_path)]
        
        if strict:
            command_args.append("--strict")
        
        command = WeaverCommand(command="weaver", args=command_args)
        
        try:
            result = self._run_weaver_command(command)
            
            errors = []
            warnings = []
            
            # Parse output for errors and warnings
            if result.stderr:
                for line in result.stderr.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if 'error:' in line.lower():
                        errors.append(line)
                    elif 'warning:' in line.lower():
                        warnings.append(line)
            
            return ValidationResult(
                valid=result.returncode == 0,
                errors=errors,
                warnings=warnings,
            )
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[str(e)],
            )
    
    def list_templates(self, language_filter: Optional[str] = None) -> List[TemplateInfo]:
        """List available templates."""
        # This would need to be implemented based on how weaver exposes template information
        # For now, return some example templates
        templates = [
            TemplateInfo(
                name="python-client",
                language="python",
                description="Python client SDK generation",
                version="1.0.0",
                path=Path("templates/python-client"),
            ),
            TemplateInfo(
                name="rust-client", 
                language="rust",
                description="Rust client SDK generation",
                version="1.0.0",
                path=Path("templates/rust-client"),
            ),
            TemplateInfo(
                name="go-client",
                language="go", 
                description="Go client SDK generation",
                version="1.0.0",
                path=Path("templates/go-client"),
            ),
        ]
        
        if language_filter:
            templates = [t for t in templates if t.language == language_filter]
        
        return templates
    
    def get_config(self) -> WeaverConfig:
        """Get current configuration."""
        return self._weaver_config
    
    def set_weaver_path(self, path: Path) -> None:
        """Set path to OTel Weaver binary."""
        if not path.exists():
            raise WeaverGenError(f"Weaver binary not found at {path}")
        
        self._weaver_config.weaver_path = path
        self._save_config()
    
    def install_weaver(self, method: str = "cargo") -> bool:
        """Install OTel Weaver using the specified method."""
        if method == "cargo":
            try:
                result = subprocess.run(
                    ["cargo", "install", "otellib-weaver-cli"],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                )
                
                if result.returncode == 0:
                    # Try to find the installed binary
                    self._ensure_weaver_binary()
                    return True
                else:
                    raise WeaverGenError(f"Failed to install weaver: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                raise WeaverGenError("Weaver installation timed out")
            except FileNotFoundError:
                raise WeaverGenError("Cargo not found. Please install Rust first.")
        
        else:
            raise WeaverGenError(f"Unsupported installation method: {method}")
