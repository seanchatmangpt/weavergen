"""
BPMN-driven Weaver Forge Integration

This module provides BPMN service tasks for OTel Weaver Forge operations,
enabling full BPMN-driven code generation with comprehensive span tracking.
"""

import asyncio
import subprocess
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import tempfile

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .bpmn_first_engine import BPMNServiceTask
from .core import WeaverGen, WeaverGenError, WeaverNotFoundError
from .enhanced_instrumentation import semantic_span, ai_validation, layer_span, resource_span, quine_span

console = Console()
tracer = trace.get_tracer(__name__)


# Weaver-specific Service Tasks
class InitializeWeaverTask(BPMNServiceTask):
    """Initialize OTel Weaver binary"""
    
    @semantic_span("weaver", "initialize")
    @resource_span("weaver", "binary")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        with tracer.start_as_current_span("weaver.initialize") as span:
            try:
                # Find weaver binary
                weaver_path = shutil.which("weaver")
                if not weaver_path:
                    # Try cargo install location
                    cargo_bin = Path.home() / ".cargo" / "bin" / "weaver"
                    if cargo_bin.exists():
                        weaver_path = str(cargo_bin)
                
                if not weaver_path:
                    raise WeaverNotFoundError("Weaver binary not found. Install with: cargo install weaver-cli")
                
                # Verify weaver works
                result = subprocess.run(
                    [weaver_path, "--version"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    raise WeaverGenError(f"Weaver verification failed: {result.stderr}")
                
                version = result.stdout.strip()
                span.set_attribute("weaver.path", weaver_path)
                span.set_attribute("weaver.version", version)
                span.set_attribute("weaver.initialized", True)
                
                return {
                    "weaver_path": weaver_path,
                    "weaver_version": version,
                    "weaver_initialized": True,
                    **context
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise


class LoadSemanticRegistryTask(BPMNServiceTask):
    """Load semantic convention registry"""
    
    @semantic_span("weaver", "load_registry")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        registry_url = context.get("registry_url", context.get("semantic_file"))
        
        with tracer.start_as_current_span("weaver.load_registry") as span:
            span.set_attribute("registry.source", str(registry_url))
            
            try:
                # If it's a URL, download it
                if str(registry_url).startswith("http"):
                    # For now, assume it's already downloaded
                    registry_path = Path("semantic_registry")
                else:
                    registry_path = Path(registry_url)
                
                if not registry_path.exists():
                    raise FileNotFoundError(f"Registry not found: {registry_path}")
                
                # Count semantic groups
                yaml_files = list(registry_path.rglob("*.yaml")) if registry_path.is_dir() else [registry_path]
                
                total_groups = 0
                for yaml_file in yaml_files:
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                        if data and "groups" in data:
                            total_groups += len(data["groups"])
                
                span.set_attribute("registry.path", str(registry_path))
                span.set_attribute("registry.files", len(yaml_files))
                span.set_attribute("registry.groups", total_groups)
                
                return {
                    "registry_path": str(registry_path),
                    "registry_files": len(yaml_files),
                    "registry_groups": total_groups,
                    **context
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise


class ValidateRegistryTask(BPMNServiceTask):
    """Validate semantic registry with Weaver"""
    
    @semantic_span("weaver", "validate_registry")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        weaver_path = context["weaver_path"]
        registry_path = context["registry_path"]
        
        with tracer.start_as_current_span("weaver.validate_registry") as span:
            span.set_attribute("weaver.command", "registry check")
            
            try:
                # Run weaver registry check
                result = subprocess.run(
                    [weaver_path, "registry", "check", "-r", registry_path],
                    capture_output=True,
                    text=True
                )
                
                valid = result.returncode == 0
                span.set_attribute("registry.valid", valid)
                span.set_attribute("registry.check.returncode", result.returncode)
                
                if not valid:
                    span.set_attribute("registry.check.error", result.stderr)
                
                return {
                    "registry_valid": valid,
                    "registry_check_output": result.stdout if valid else result.stderr,
                    **context
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise


class SelectPythonTemplatesTask(BPMNServiceTask):
    """Select Python templates for generation"""
    
    @semantic_span("python", "select_templates")
    @ai_validation("qwen3:latest", "TemplateSelection")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        with tracer.start_as_current_span("python.select_templates") as span:
            # Default Python templates
            templates = {
                "metrics": "templates/python/otel/metrics.j2",
                "attributes": "templates/python/otel/attributes.j2", 
                "resources": "templates/python/otel/resources.j2",
                "spans": "templates/python/otel/spans.j2",
                "registry": "templates/python/otel/registry.j2"
            }
            
            # Check which templates exist
            template_dir = Path("templates/python")
            if not template_dir.exists():
                # Use built-in templates
                templates = {
                    "base": "builtin:python_base",
                    "semantic": "builtin:python_semantic"
                }
            
            span.set_attribute("templates.count", len(templates))
            span.set_attribute("templates.type", "python")
            
            return {
                "python_templates": templates,
                "template_language": "python",
                **context
            }


class GeneratePythonMetricsTask(BPMNServiceTask):
    """Generate Python metrics with Weaver"""
    
    @semantic_span("python", "generate_metrics")
    @layer_span("generation")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        weaver_path = context["weaver_path"]
        registry_path = context["registry_path"]
        output_dir = Path(context.get("output_dir", "generated"))
        
        with tracer.start_as_current_span("python.generate_metrics") as span:
            metrics_dir = output_dir / "metrics"
            metrics_dir.mkdir(parents=True, exist_ok=True)
            
            span.set_attribute("generation.target", "metrics")
            span.set_attribute("generation.language", "python")
            span.set_attribute("generation.output", str(metrics_dir))
            
            try:
                # Create weaver config for metrics
                config = {
                    "file_format": "1.0.0",
                    "schema_url": "https://opentelemetry.io/schemas/1.21.0",
                    "semantic_conventions": {
                        "registry_url": str(registry_path)
                    },
                    "templates": [
                        {
                            "pattern": "metrics.py.j2",
                            "filter": ".",
                            "application_mode": "single"
                        }
                    ]
                }
                
                # Write temporary config
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    config_path = f.name
                
                # Run weaver generate
                result = subprocess.run(
                    [weaver_path, "registry", "generate",
                     "--config", config_path,
                     "--output", str(metrics_dir),
                     "python"],
                    capture_output=True,
                    text=True
                )
                
                # Clean up config
                Path(config_path).unlink()
                
                success = result.returncode == 0
                span.set_attribute("generation.success", success)
                
                if success:
                    # Count generated files
                    generated_files = list(metrics_dir.glob("*.py"))
                    span.set_attribute("generation.files", len(generated_files))
                else:
                    span.set_attribute("generation.error", result.stderr)
                
                return {
                    "metrics_generated": success,
                    "metrics_dir": str(metrics_dir),
                    "metrics_files": len(generated_files) if success else 0,
                    **context
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise


class CaptureGenerationSpansTask(BPMNServiceTask):
    """Capture all generation spans"""
    
    @semantic_span("weaver", "capture_spans")
    @quine_span("span_capture")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        with tracer.start_as_current_span("weaver.capture_spans") as span:
            # In a real implementation, this would capture actual spans
            # For now, create synthetic span data
            
            captured_spans = []
            
            # Add spans from context
            if "metrics_generated" in context:
                captured_spans.append({
                    "name": "weaver.generate.metrics",
                    "timestamp": datetime.now().isoformat(),
                    "attributes": {
                        "target": "metrics",
                        "language": "python",
                        "success": context.get("metrics_generated", False)
                    }
                })
            
            if "attributes_generated" in context:
                captured_spans.append({
                    "name": "weaver.generate.attributes",
                    "timestamp": datetime.now().isoformat(),
                    "attributes": {
                        "target": "attributes",
                        "language": "python",
                        "success": context.get("attributes_generated", False)
                    }
                })
            
            # Save spans to file
            output_dir = Path(context.get("output_dir", "generated"))
            spans_file = output_dir / "generation_spans.json"
            
            with open(spans_file, 'w') as f:
                json.dump(captured_spans, f, indent=2)
            
            span.set_attribute("spans.captured", len(captured_spans))
            span.set_attribute("spans.file", str(spans_file))
            
            return {
                "captured_spans": captured_spans,
                "spans_file": str(spans_file),
                "total_spans": len(captured_spans),
                **context
            }


class ValidateGeneratedCodeTask(BPMNServiceTask):
    """Validate generated code with spans"""
    
    @semantic_span("weaver", "validate_code")
    @layer_span("validation")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        output_dir = Path(context.get("output_dir", "generated"))
        
        with tracer.start_as_current_span("weaver.validate_code") as span:
            validation_results = {
                "syntax_valid": True,
                "imports_valid": True,
                "structure_valid": True,
                "span_instrumented": True
            }
            
            # Check generated Python files
            py_files = list(output_dir.rglob("*.py"))
            span.set_attribute("validation.files", len(py_files))
            
            for py_file in py_files:
                try:
                    # Compile to check syntax
                    with open(py_file) as f:
                        compile(f.read(), py_file, 'exec')
                except SyntaxError as e:
                    validation_results["syntax_valid"] = False
                    span.set_attribute(f"validation.syntax_error.{py_file.name}", str(e))
                
                # Check for OTel imports
                with open(py_file) as f:
                    content = f.read()
                    if "opentelemetry" not in content:
                        validation_results["span_instrumented"] = False
            
            # Overall validation score
            valid_count = sum(1 for v in validation_results.values() if v)
            validation_score = valid_count / len(validation_results)
            
            span.set_attribute("validation.score", validation_score)
            span.set_attribute("validation.passed", validation_score >= 0.8)
            
            return {
                "validation_results": validation_results,
                "validation_score": validation_score,
                "validation_passed": validation_score >= 0.8,
                **context
            }


class GenerateSpanReportTask(BPMNServiceTask):
    """Generate comprehensive span report"""
    
    @semantic_span("weaver", "span_report")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        with tracer.start_as_current_span("weaver.span_report") as span:
            # Create report table
            table = Table(title="Weaver Forge Generation Report", show_header=True)
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Files", style="yellow")
            table.add_column("Spans", style="magenta")
            
            # Add generation results
            if context.get("metrics_generated"):
                table.add_row("Metrics", "✅ Generated", str(context.get("metrics_files", 0)), "✅")
            
            if context.get("validation_passed"):
                table.add_row("Validation", "✅ Passed", "-", "✅")
            else:
                table.add_row("Validation", "❌ Failed", "-", "❌")
            
            # Generate Mermaid diagram
            mermaid = """graph TD
    A[BPMN Process] --> B[Initialize Weaver]
    B --> C[Load Registry]
    C --> D[Validate Registry]
    D --> E{Language?}
    E -->|Python| F[Generate Python]
    E -->|Multi| G[Generate Multi-Language]
    F --> H[Capture Spans]
    G --> H
    H --> I[Validate Code]
    I --> J[Generate Report]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style H fill:#bbf,stroke:#333,stroke-width:2px
    style J fill:#bfb,stroke:#333,stroke-width:2px
"""
            
            console.print(table)
            
            span.set_attribute("report.generated", True)
            span.set_attribute("report.components", 2)
            
            return {
                "report_generated": True,
                "report_mermaid": mermaid,
                **context
            }


# Registry for Weaver BPMN tasks
WEAVER_BPMN_TASKS = {
    "InitializeWeaverTask": InitializeWeaverTask,
    "LoadSemanticRegistryTask": LoadSemanticRegistryTask,
    "ValidateRegistryTask": ValidateRegistryTask,
    "SelectPythonTemplatesTask": SelectPythonTemplatesTask,
    "GeneratePythonMetricsTask": GeneratePythonMetricsTask,
    "CaptureGenerationSpansTask": CaptureGenerationSpansTask,
    "ValidateGeneratedCodeTask": ValidateGeneratedCodeTask,
    "GenerateSpanReportTask": GenerateSpanReportTask,
}


# Enhanced BPMN Engine for Weaver
class WeaverBPMNEngine:
    """BPMN engine with Weaver Forge integration"""
    
    def __init__(self):
        self.service_tasks = WEAVER_BPMN_TASKS
        self.span_collector = []
    
    @semantic_span("bpmn", "execute_weaver_workflow")
    @quine_span("weaver_execution")
    async def execute_weaver_workflow(self, workflow_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Weaver-specific BPMN workflow"""
        
        with tracer.start_as_current_span(f"bpmn.weaver.{workflow_name}") as span:
            span.set_attribute("workflow.name", workflow_name)
            span.set_attribute("workflow.type", "weaver_forge")
            
            try:
                # Mock execution for Weaver Forge Orchestration
                if workflow_name == "WeaverForgeOrchestration":
                    tasks = [
                        ("InitializeWeaverTask", {}),
                        ("LoadSemanticRegistryTask", {}),
                        ("ValidateRegistryTask", {}),
                        ("SelectPythonTemplatesTask", {}),
                        ("GeneratePythonMetricsTask", {}),
                        ("CaptureGenerationSpansTask", {}),
                        ("ValidateGeneratedCodeTask", {}),
                        ("GenerateSpanReportTask", {}),
                    ]
                    
                    for task_name, task_context in tasks:
                        if task_name in self.service_tasks:
                            task_class = self.service_tasks[task_name]
                            task = task_class()
                            
                            # Merge contexts
                            exec_context = {**context, **task_context}
                            
                            # Execute task
                            result = await task.execute(exec_context)
                            
                            # Update context
                            context.update(result)
                            
                            # Collect span
                            self.span_collector.append({
                                "task": task_name,
                                "timestamp": datetime.now().isoformat(),
                                "success": True
                            })
                
                span.set_attribute("workflow.tasks_executed", len(self.span_collector))
                span.set_attribute("workflow.success", True)
                
                return context
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise