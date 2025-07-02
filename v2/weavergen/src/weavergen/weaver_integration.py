"""Real Weaver Forge binary integration for WeaverGen v2."""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from pydantic import BaseModel, Field

from .enhanced_instrumentation import semantic_span, add_span_event

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class WeaverTarget(str, Enum):
    """Available Weaver generation targets."""
    CODE_GEN_PYTHON = "codegen_python"
    CODE_GEN_GO = "codegen_go"
    CODE_GEN_RUST = "codegen_rust"
    CODE_GEN_JAVA = "codegen_java"
    CODE_GEN_TYPESCRIPT = "codegen_typescript"
    CODE_GEN_DOTNET = "codegen_dotnet"
    MARKDOWN = "markdown"
    JSON_SCHEMA = "json_schema"
    POLICY = "policy"


class WeaverDiagnosticFormat(str, Enum):
    """Available diagnostic output formats."""
    ANSI = "ansi"
    JSON = "json"
    GH_WORKFLOW_COMMAND = "gh_workflow_command"


@dataclass
class WeaverConfig:
    """Configuration for Weaver operations."""
    weaver_path: Path = Path("weaver")
    templates_dir: Path = Path("templates")
    output_dir: Path = Path("output")
    diagnostic_format: WeaverDiagnosticFormat = WeaverDiagnosticFormat.ANSI
    follow_symlinks: bool = False
    include_unreferenced: bool = False
    future_validation: bool = True
    debug_level: int = 0
    quiet: bool = False


class WeaverValidationResult(BaseModel):
    """Result of Weaver validation."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    diagnostics: List[Dict[str, Any]] = Field(default_factory=list)
    return_code: int
    stdout: str = ""
    stderr: str = ""


class WeaverGenerationResult(BaseModel):
    """Result of Weaver code generation."""
    success: bool
    output_dir: Path
    generated_files: List[str] = Field(default_factory=list)
    template_used: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    return_code: int
    stdout: str = ""
    stderr: str = ""
    diagnostics: List[Dict[str, Any]] = Field(default_factory=list)


class WeaverRegistryInfo(BaseModel):
    """Information about a Weaver registry."""
    registry_path: Path
    valid: bool
    stats: Dict[str, Any] = Field(default_factory=dict)
    groups_count: int = 0
    attributes_count: int = 0
    metrics_count: int = 0
    spans_count: int = 0
    resources_count: int = 0


class WeaverIntegration:
    """Real Weaver Forge binary integration."""
    
    def __init__(self, config: Optional[WeaverConfig] = None):
        self.config = config or WeaverConfig()
        self._validate_weaver_installation()
    
    def _validate_weaver_installation(self) -> None:
        """Validate that Weaver binary is available and working."""
        with tracer.start_as_current_span("weaver.validate_installation") as span:
            span.set_attribute("component", "weaver")
            span.set_attribute("operation", "validate_installation")
            try:
                result = subprocess.run(
                    [str(self.config.weaver_path), "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                version = result.stdout.strip()
                span.set_attribute("weaver.version", version)
                logger.info(f"Weaver {version} found and working")
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Weaver not found"))
                raise RuntimeError(
                    f"Weaver binary not found at {self.config.weaver_path}. "
                    "Install with: cargo install weaver-forge"
                ) from e
    
    @semantic_span("weaver", "registry.check")
    def check_registry(
        self, 
        registry_path: Union[str, Path], 
        strict: bool = False
    ) -> WeaverValidationResult:
        """Validate a semantic convention registry using Weaver."""
        registry_path = Path(registry_path)
        
        with tracer.start_as_current_span("weaver.registry.check") as span:
            span.set_attribute("registry_path", str(registry_path))
            span.set_attribute("strict", strict)
            
            # Build command
            cmd = [
                str(self.config.weaver_path), "registry", "check",
                "-r", str(registry_path)
            ]
            
            if strict:
                cmd.append("--future")
            
            if self.config.debug_level > 0:
                cmd.extend(["--debug"] * self.config.debug_level)
            
            if self.config.quiet:
                cmd.append("--quiet")
            
            add_span_event("weaver.command.start", {"command": " ".join(cmd)})
            
            try:
                # Execute Weaver command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                span.set_attribute("return_code", result.returncode)
                span.set_attribute("stdout_length", len(result.stdout))
                span.set_attribute("stderr_length", len(result.stderr))
                
                # Parse diagnostics if available
                diagnostics = self._parse_diagnostics(result.stderr)
                
                # Determine validation result
                valid = result.returncode == 0
                errors = []
                warnings = []
                
                if not valid:
                    # Parse errors from stderr
                    for line in result.stderr.split('\n'):
                        line = line.strip()
                        if line and ('error' in line.lower() or 'failed' in line.lower()):
                            errors.append(line)
                        elif line and 'warning' in line.lower():
                            warnings.append(line)
                
                # If no explicit errors found but return code is non-zero
                if not valid and not errors:
                    errors = [f"Weaver validation failed with return code {result.returncode}"]
                
                add_span_event("weaver.command.complete", {
                    "valid": valid,
                    "error_count": len(errors),
                    "warning_count": len(warnings)
                })
                
                if valid:
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR, f"Validation failed: {len(errors)} errors"))
                
                return WeaverValidationResult(
                    valid=valid,
                    errors=errors,
                    warnings=warnings,
                    diagnostics=diagnostics,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
                
            except subprocess.TimeoutExpired as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Command timed out"))
                return WeaverValidationResult(
                    valid=False,
                    errors=[f"Weaver command timed out after 300 seconds"],
                    return_code=-1,
                    stderr="Command timed out"
                )
            
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return WeaverValidationResult(
                    valid=False,
                    errors=[f"Weaver command failed: {e}"],
                    return_code=-1,
                    stderr=str(e)
                )
    
    @semantic_span("weaver", "registry.generate")
    def generate_code(
        self,
        registry_path: Union[str, Path],
        target: WeaverTarget,
        output_dir: Optional[Path] = None,
        templates_dir: Optional[Path] = None,
        parameters: Optional[Dict[str, Any]] = None,
        policies: Optional[List[Path]] = None,
        skip_policies: bool = False
    ) -> WeaverGenerationResult:
        """Generate code from semantic conventions using Weaver."""
        registry_path = Path(registry_path)
        output_dir = output_dir or self.config.output_dir
        templates_dir = templates_dir or self.config.templates_dir
        parameters = parameters or {}
        
        with tracer.start_as_current_span("weaver.registry.generate") as span:
            span.set_attribute("registry_path", str(registry_path))
            span.set_attribute("target", target.value)
            span.set_attribute("output_dir", str(output_dir))
            span.set_attribute("templates_dir", str(templates_dir))
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build command
            cmd = [
                str(self.config.weaver_path), "registry", "generate",
                "-r", str(registry_path),
                "-t", str(templates_dir),
                target.value,
                str(output_dir)
            ]
            
            # Add parameters
            for key, value in parameters.items():
                cmd.extend(["-D", f"{key}={value}"])
            
            # Add policies
            if policies and not skip_policies:
                for policy in policies:
                    cmd.extend(["-p", str(policy)])
            
            if skip_policies:
                cmd.append("--skip-policies")
            
            if self.config.follow_symlinks:
                cmd.append("--follow-symlinks")
            
            if self.config.include_unreferenced:
                cmd.append("--include-unreferenced")
            
            if self.config.future_validation:
                cmd.append("--future")
            
            if self.config.debug_level > 0:
                cmd.extend(["--debug"] * self.config.debug_level)
            
            if self.config.quiet:
                cmd.append("--quiet")
            
            add_span_event("weaver.command.start", {"command": " ".join(cmd)})
            
            try:
                # Execute Weaver command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout for generation
                )
                
                span.set_attribute("return_code", result.returncode)
                span.set_attribute("stdout_length", len(result.stdout))
                span.set_attribute("stderr_length", len(result.stderr))
                
                # Parse diagnostics
                diagnostics = self._parse_diagnostics(result.stderr)
                
                # Determine success
                success = result.returncode == 0
                
                # Get generated files
                generated_files = []
                if success and output_dir.exists():
                    generated_files = [
                        str(f.relative_to(output_dir))
                        for f in output_dir.rglob("*")
                        if f.is_file()
                    ]
                
                add_span_event("weaver.command.complete", {
                    "success": success,
                    "files_generated": len(generated_files)
                })
                
                if success:
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR, f"Generation failed: {result.returncode}"))
                
                return WeaverGenerationResult(
                    success=success,
                    output_dir=output_dir,
                    generated_files=generated_files,
                    template_used=target.value,
                    parameters=parameters,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    diagnostics=diagnostics
                )
                
            except subprocess.TimeoutExpired as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Command timed out"))
                return WeaverGenerationResult(
                    success=False,
                    output_dir=output_dir,
                    template_used=target.value,
                    parameters=parameters,
                    return_code=-1,
                    stderr="Command timed out"
                )
            
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return WeaverGenerationResult(
                    success=False,
                    output_dir=output_dir,
                    template_used=target.value,
                    parameters=parameters,
                    return_code=-1,
                    stderr=str(e)
                )
    
    @semantic_span("weaver", "registry.stats")
    def get_registry_stats(self, registry_path: Union[str, Path]) -> WeaverRegistryInfo:
        """Get statistics about a semantic convention registry."""
        registry_path = Path(registry_path)
        
        with tracer.start_as_current_span("weaver.registry.stats") as span:
            span.set_attribute("registry_path", str(registry_path))
            
            # Build command
            cmd = [
                str(self.config.weaver_path), "registry", "stats",
                "-r", str(registry_path)
            ]
            
            if self.config.future_validation:
                cmd.append("--future")
            
            if self.config.debug_level > 0:
                cmd.extend(["--debug"] * self.config.debug_level)
            
            try:
                # Execute Weaver command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                span.set_attribute("return_code", result.returncode)
                
                if result.returncode == 0:
                    # Parse JSON output
                    try:
                        stats = json.loads(result.stdout)
                        span.set_status(Status(StatusCode.OK))
                        
                        return WeaverRegistryInfo(
                            registry_path=registry_path,
                            valid=True,
                            stats=stats,
                            groups_count=stats.get("groups", 0),
                            attributes_count=stats.get("attributes", 0),
                            metrics_count=stats.get("metrics", 0),
                            spans_count=stats.get("spans", 0),
                            resources_count=stats.get("resources", 0)
                        )
                    except json.JSONDecodeError:
                        # Fallback to parsing text output
                        return self._parse_stats_text(result.stdout, registry_path)
                else:
                    span.set_status(Status(StatusCode.ERROR, f"Stats failed: {result.returncode}"))
                    return WeaverRegistryInfo(
                        registry_path=registry_path,
                        valid=False
                    )
                    
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return WeaverRegistryInfo(
                    registry_path=registry_path,
                    valid=False
                )
    
    @semantic_span("weaver", "registry.resolve")
    def resolve_registry(
        self, 
        registry_path: Union[str, Path], 
        output_file: Optional[Path] = None
    ) -> Path:
        """Resolve a semantic convention registry to a single file."""
        registry_path = Path(registry_path)
        
        with tracer.start_as_current_span("weaver.registry.resolve") as span:
            span.set_attribute("registry_path", str(registry_path))
            
            if output_file is None:
                output_file = Path(tempfile.mktemp(suffix=".yaml"))
            
            span.set_attribute("output_file", str(output_file))
            
            # Build command
            cmd = [
                str(self.config.weaver_path), "registry", "resolve",
                "-r", str(registry_path),
                str(output_file)
            ]
            
            if self.config.future_validation:
                cmd.append("--future")
            
            try:
                # Execute Weaver command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                span.set_attribute("return_code", result.returncode)
                
                if result.returncode == 0:
                    span.set_status(Status(StatusCode.OK))
                    return output_file
                else:
                    span.set_status(Status(StatusCode.ERROR, f"Resolve failed: {result.returncode}"))
                    raise RuntimeError(f"Failed to resolve registry: {result.stderr}")
                    
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def _parse_diagnostics(self, stderr: str) -> List[Dict[str, Any]]:
        """Parse diagnostic messages from Weaver stderr output."""
        diagnostics = []
        
        for line in stderr.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Try to parse as JSON diagnostic
            if line.startswith('{') and line.endswith('}'):
                try:
                    diagnostic = json.loads(line)
                    diagnostics.append(diagnostic)
                except json.JSONDecodeError:
                    pass
            
            # Parse ANSI diagnostic format
            elif 'error' in line.lower() or 'warning' in line.lower():
                diagnostics.append({
                    "type": "error" if "error" in line.lower() else "warning",
                    "message": line,
                    "raw": line
                })
        
        return diagnostics
    
    def _parse_stats_text(self, stdout: str, registry_path: Path) -> WeaverRegistryInfo:
        """Parse statistics from text output when JSON is not available."""
        stats = {}
        groups_count = 0
        attributes_count = 0
        metrics_count = 0
        spans_count = 0
        resources_count = 0
        
        for line in stdout.split('\n'):
            line = line.strip()
            if 'groups:' in line.lower():
                try:
                    groups_count = int(line.split(':')[1].strip())
                except (IndexError, ValueError):
                    pass
            elif 'attributes:' in line.lower():
                try:
                    attributes_count = int(line.split(':')[1].strip())
                except (IndexError, ValueError):
                    pass
            elif 'metrics:' in line.lower():
                try:
                    metrics_count = int(line.split(':')[1].strip())
                except (IndexError, ValueError):
                    pass
            elif 'spans:' in line.lower():
                try:
                    spans_count = int(line.split(':')[1].strip())
                except (IndexError, ValueError):
                    pass
            elif 'resources:' in line.lower():
                try:
                    resources_count = int(line.split(':')[1].strip())
                except (IndexError, ValueError):
                    pass
        
        return WeaverRegistryInfo(
            registry_path=registry_path,
            valid=True,
            stats=stats,
            groups_count=groups_count,
            attributes_count=attributes_count,
            metrics_count=metrics_count,
            spans_count=spans_count,
            resources_count=resources_count
        )
    
    def get_available_targets(self) -> List[WeaverTarget]:
        """Get list of available Weaver generation targets."""
        return list(WeaverTarget)
    
    def get_weaver_version(self) -> str:
        """Get Weaver version."""
        try:
            result = subprocess.run(
                [str(self.config.weaver_path), "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return "unknown" 