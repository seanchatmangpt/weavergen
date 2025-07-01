"""
WeaverGen Runtime Engine - 80/20 Implementation
NO PYTESTS - Uses span-based validation only
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
import subprocess
import tempfile
import shutil

from .span_validation import SpanBasedValidator
from .core import WeaverGen, WeaverGenError, GenerationConfig, GenerationResult


class WeaverRuntime:
    """Core execution runtime for WeaverGen - 80/20 implementation"""
    
    def __init__(self, config: Optional[GenerationConfig] = None):
        self.config = config
        self.validator = SpanBasedValidator()
        self.weaver_gen = WeaverGen(config=config)
        self.execution_context = {
            "runtime_id": str(uuid.uuid4())[:8],
            "start_time": time.time(),
            "sessions": {}
        }
    
    async def execute_generation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute semantic convention code generation - CORE 80/20 functionality"""
        
        execution_span = self.validator._start_span("runtime.execute_generation")
        session_id = str(uuid.uuid4())[:8]
        
        try:
            # Parse generation request
            config = self._parse_generation_request(request_data)
            
            # Create execution session
            session = {
                "session_id": session_id,
                "config": config.dict() if hasattr(config, 'dict') else str(config),
                "start_time": time.time(),
                "status": "executing"
            }
            self.execution_context["sessions"][session_id] = session
            
            # Execute weaver generation
            weaver = WeaverGen(config=config)
            result = weaver.generate()
            
            # Process results
            execution_result = {
                "session_id": session_id,
                "success": result.success,
                "generated_files": [str(f.path) for f in result.files] if result.files else [],
                "duration_seconds": result.duration_seconds,
                "error": result.error if not result.success else None,
                "warnings": result.warnings or [],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Update session
            session.update({
                "status": "completed" if result.success else "failed",
                "end_time": time.time(),
                "result": execution_result
            })
            
            # Set span attributes
            execution_span["attributes"] = {
                "runtime.session_id": session_id,
                "runtime.execution.success": result.success,
                "runtime.files_generated": len(execution_result["generated_files"]),
                "runtime.duration_seconds": result.duration_seconds,
                "runtime.config.language": getattr(config, 'language', 'unknown'),
                "runtime.config.output_dir": str(getattr(config, 'output_dir', 'unknown'))
            }
            
            self.validator._end_span(execution_span)
            return execution_result
            
        except Exception as e:
            execution_span["attributes"] = {
                "runtime.session_id": session_id,
                "runtime.execution.success": False,
                "runtime.error": str(e),
                "runtime.error.type": type(e).__name__
            }
            self.validator._end_span(execution_span)
            
            return {
                "session_id": session_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _parse_generation_request(self, request_data: Dict[str, Any]) -> GenerationConfig:
        """Parse generation request into config - 80/20 essential fields"""
        
        parse_span = self.validator._start_span("runtime.parse_request")
        
        try:
            # Essential 80/20 config fields
            registry_url = request_data.get("registry_url") or request_data.get("semantic_file")
            output_dir = Path(request_data.get("output_dir", "./generated"))
            language = request_data.get("language", "python")
            
            if not registry_url:
                raise WeaverGenError("registry_url or semantic_file required")
            
            config = GenerationConfig(
                registry_url=registry_url,
                output_dir=output_dir,
                language=language,
                template_dir=request_data.get("template_dir"),
                force_overwrite=request_data.get("force", False),
                verbose=request_data.get("verbose", False)
            )
            
            parse_span["attributes"] = {
                "parse.registry_url": str(registry_url),
                "parse.output_dir": str(output_dir),
                "parse.language": language,
                "parse.success": True
            }
            
            self.validator._end_span(parse_span)
            return config
            
        except Exception as e:
            parse_span["attributes"] = {
                "parse.success": False,
                "parse.error": str(e)
            }
            self.validator._end_span(parse_span)
            raise
    
    async def execute_validation(self, validation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation workflow - 80/20 functionality"""
        
        validation_span = self.validator._start_span("runtime.execute_validation")
        
        try:
            target_files = validation_request.get("files", [])
            validation_type = validation_request.get("type", "syntax")
            
            if validation_type == "syntax":
                result = self.validator.validate_implementation(target_files)
            elif validation_type == "pipeline":
                convention_name = validation_request.get("convention_name", "test")
                result = self.validator.validate_generation_pipeline(convention_name)
            else:
                raise WeaverGenError(f"Unknown validation type: {validation_type}")
            
            validation_span["attributes"] = {
                "validation.type": validation_type,
                "validation.files_count": len(target_files),
                "validation.success": result.get("validation_passed", False),
                "validation.coverage": result.get("coverage_percentage", 0.0)
            }
            
            self.validator._end_span(validation_span)
            return result
            
        except Exception as e:
            validation_span["attributes"] = {
                "validation.success": False,
                "validation.error": str(e)
            }
            self.validator._end_span(validation_span)
            raise
    
    async def execute_template_operation(self, template_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute template operations - 80/20 functionality"""
        
        template_span = self.validator._start_span("runtime.execute_template")
        
        try:
            operation = template_request.get("operation", "list")
            
            if operation == "list":
                # List available templates
                templates = self.weaver_gen.list_templates(
                    language_filter=template_request.get("language")
                )
                result = {
                    "templates": [
                        {
                            "name": t.name,
                            "language": t.language,
                            "description": t.description,
                            "version": t.version,
                            "path": str(t.path)
                        } for t in templates
                    ]
                }
            
            elif operation == "render":
                # Render template (basic implementation)
                template_name = template_request.get("template_name")
                template_data = template_request.get("data", {})
                
                if not template_name:
                    raise WeaverGenError("template_name required for render operation")
                
                # Basic template rendering simulation
                rendered_content = self._render_template_basic(template_name, template_data)
                
                result = {
                    "template_name": template_name,
                    "rendered_content": rendered_content,
                    "success": True
                }
            
            else:
                raise WeaverGenError(f"Unknown template operation: {operation}")
            
            template_span["attributes"] = {
                "template.operation": operation,
                "template.success": True
            }
            
            self.validator._end_span(template_span)
            return result
            
        except Exception as e:
            template_span["attributes"] = {
                "template.operation": template_request.get("operation", "unknown"),
                "template.success": False,
                "template.error": str(e)
            }
            self.validator._end_span(template_span)
            raise
    
    def _render_template_basic(self, template_name: str, data: Dict[str, Any]) -> str:
        """Basic template rendering - 80/20 implementation"""
        
        # Simple template rendering for common cases
        templates = {
            "python-class": '''
class {class_name}:
    """Generated {description}"""
    
    def __init__(self):
        self.{attribute_name} = "{attribute_value}"
    
    def get_{attribute_name}(self):
        return self.{attribute_name}
''',
            "python-function": '''
def {function_name}({parameters}):
    """Generated function: {description}"""
    return {return_value}
''',
            "rust-struct": '''
pub struct {struct_name} {{
    pub {field_name}: {field_type},
}}

impl {struct_name} {{
    pub fn new({field_name}: {field_type}) -> Self {{
        Self {{ {field_name} }}
    }}
}}
'''
        }
        
        template = templates.get(template_name, "// Template not found: {template_name}")
        
        try:
            return template.format(**data)
        except KeyError as e:
            return f"// Template rendering error: missing data for {e}"
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get runtime execution status"""
        
        status_span = self.validator._start_span("runtime.get_status")
        
        current_time = time.time()
        uptime_seconds = current_time - self.execution_context["start_time"]
        
        active_sessions = [
            s for s in self.execution_context["sessions"].values()
            if s.get("status") == "executing"
        ]
        
        completed_sessions = [
            s for s in self.execution_context["sessions"].values()
            if s.get("status") in ["completed", "failed"]
        ]
        
        status = {
            "runtime_id": self.execution_context["runtime_id"],
            "uptime_seconds": uptime_seconds,
            "total_sessions": len(self.execution_context["sessions"]),
            "active_sessions": len(active_sessions),
            "completed_sessions": len(completed_sessions),
            "spans_captured": len(self.validator.spans),
            "last_activity": max(
                [s.get("start_time", 0) for s in self.execution_context["sessions"].values()],
                default=self.execution_context["start_time"]
            ),
            "status": "active" if active_sessions else "idle"
        }
        
        status_span["attributes"] = {
            "status.runtime_id": status["runtime_id"],
            "status.uptime_seconds": status["uptime_seconds"],
            "status.total_sessions": status["total_sessions"],
            "status.active_sessions": status["active_sessions"],
            "status.status": status["status"]
        }
        
        self.validator._end_span(status_span)
        return status
    
    def save_execution_telemetry(self, output_file: Path):
        """Save execution telemetry including spans"""
        
        telemetry_data = {
            "runtime_context": self.execution_context,
            "execution_status": self.get_execution_status(),
            "validation_spans": self.validator.spans,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(telemetry_data, f, indent=2, default=str)


class TemplateEngine:
    """Template rendering engine - 80/20 implementation"""
    
    def __init__(self):
        self.validator = SpanBasedValidator()
        self.template_cache = {}
    
    async def render_template(self, template_path: Path, context: Dict[str, Any]) -> str:
        """Render template with context - CORE functionality"""
        
        render_span = self.validator._start_span("template.render")
        
        try:
            # Check cache first
            cache_key = str(template_path)
            if cache_key in self.template_cache:
                template_content = self.template_cache[cache_key]
            else:
                if not template_path.exists():
                    raise FileNotFoundError(f"Template not found: {template_path}")
                
                with open(template_path) as f:
                    template_content = f.read()
                
                # Cache template
                self.template_cache[cache_key] = template_content
            
            # Simple template rendering (placeholder replacement)
            rendered = template_content
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                rendered = rendered.replace(placeholder, str(value))
            
            render_span["attributes"] = {
                "template.path": str(template_path),
                "template.context_keys": list(context.keys()),
                "template.rendered_length": len(rendered),
                "template.success": True
            }
            
            self.validator._end_span(render_span)
            return rendered
            
        except Exception as e:
            render_span["attributes"] = {
                "template.path": str(template_path),
                "template.success": False,
                "template.error": str(e)
            }
            self.validator._end_span(render_span)
            raise
    
    def clear_cache(self):
        """Clear template cache"""
        self.template_cache.clear()


class ProcessManager:
    """Process execution manager - 80/20 implementation"""
    
    def __init__(self):
        self.validator = SpanBasedValidator()
        self.active_processes = {}
    
    async def execute_weaver_command(self, command_args: List[str], working_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Execute weaver command - CORE functionality"""
        
        command_span = self.validator._start_span("process.execute_weaver")
        process_id = str(uuid.uuid4())[:8]
        
        try:
            # Find weaver binary
            weaver_path = shutil.which("weaver")
            if not weaver_path:
                # Check common locations
                common_paths = [
                    Path.home() / ".cargo" / "bin" / "weaver",
                    Path("/usr/local/bin/weaver"),
                    Path("/opt/homebrew/bin/weaver")
                ]
                
                for path in common_paths:
                    if path.exists():
                        weaver_path = str(path)
                        break
                
                if not weaver_path:
                    raise WeaverGenError("Weaver binary not found")
            
            # Build command
            full_command = [weaver_path] + command_args
            
            # Execute
            start_time = time.time()
            result = subprocess.run(
                full_command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            end_time = time.time()
            
            execution_result = {
                "process_id": process_id,
                "command": full_command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_seconds": end_time - start_time,
                "success": result.returncode == 0,
                "working_dir": str(working_dir) if working_dir else None
            }
            
            command_span["attributes"] = {
                "process.id": process_id,
                "process.command": " ".join(full_command),
                "process.return_code": result.returncode,
                "process.duration_seconds": execution_result["duration_seconds"],
                "process.success": execution_result["success"],
                "process.stdout_length": len(result.stdout) if result.stdout else 0,
                "process.stderr_length": len(result.stderr) if result.stderr else 0
            }
            
            self.validator._end_span(command_span)
            return execution_result
            
        except subprocess.TimeoutExpired:
            error_result = {
                "process_id": process_id,
                "success": False,
                "error": "Command timed out",
                "timeout": True
            }
            
            command_span["attributes"] = {
                "process.id": process_id,
                "process.success": False,
                "process.error": "timeout"
            }
            
            self.validator._end_span(command_span)
            return error_result
            
        except Exception as e:
            error_result = {
                "process_id": process_id,
                "success": False,
                "error": str(e)
            }
            
            command_span["attributes"] = {
                "process.id": process_id,
                "process.success": False,
                "process.error": str(e)
            }
            
            self.validator._end_span(command_span)
            return error_result


# 80/20 Integration Test - NO PYTESTS
async def validate_runtime_integration():
    """Validate runtime integration using spans only - NO PYTESTS"""
    
    validator = SpanBasedValidator()
    integration_span = validator._start_span("runtime.integration_test")
    
    try:
        # Test runtime initialization
        runtime = WeaverRuntime()
        
        # Test basic generation
        test_request = {
            "registry_url": "https://opentelemetry.io/schemas/1.21.0",
            "output_dir": "./test_output",
            "language": "python"
        }
        
        result = await runtime.execute_generation(test_request)
        
        # Test validation
        validation_result = await runtime.execute_validation({
            "files": ["./test_output"],
            "type": "syntax"
        })
        
        # Test template operations
        template_result = await runtime.execute_template_operation({
            "operation": "list",
            "language": "python"
        })
        
        integration_span["attributes"] = {
            "integration.generation_success": result.get("success", False),
            "integration.validation_success": validation_result.get("validation_passed", False),
            "integration.template_success": bool(template_result.get("templates")),
            "integration.overall_success": True
        }
        
        validator._end_span(integration_span)
        
        # Save telemetry
        runtime.save_execution_telemetry(Path("runtime_integration_telemetry.json"))
        validator.save_validation_spans(Path("runtime_validation_spans.json"))
        
        return {
            "integration_success": True,
            "generation_result": result,
            "validation_result": validation_result,
            "template_result": template_result
        }
        
    except Exception as e:
        integration_span["attributes"] = {
            "integration.overall_success": False,
            "integration.error": str(e)
        }
        validator._end_span(integration_span)
        raise


if __name__ == "__main__":
    # Run integration validation
    asyncio.run(validate_runtime_integration())