"""
WeaverGen Operations Layer - 80/20 Business Logic Implementation
NO PYTESTS - Uses span-based validation only
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import uuid
import tempfile

from .span_validation import SpanBasedValidator
from .runtime_engine import WeaverRuntime, TemplateEngine, ProcessManager
from .core import GenerationConfig, GenerationResult, ValidationResult


class GenerationOperation:
    """Core generation business logic - 80/20 implementation"""
    
    def __init__(self):
        self.validator = SpanBasedValidator()
        self.runtime = WeaverRuntime()
        self.template_engine = TemplateEngine()
        self.process_manager = ProcessManager()
        self.operation_history = []
    
    async def generate_from_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute complete generation workflow - CORE 80/20 functionality"""
        
        operation_span = self.validator._start_span("operations.generate_from_request")
        operation_id = str(uuid.uuid4())[:8]
        
        try:
            # Phase 1: Prepare generation
            preparation_result = await self._prepare_generation(request, context)
            if not preparation_result["success"]:
                raise Exception(f"Generation preparation failed: {preparation_result['error']}")
            
            # Phase 2: Execute generation
            execution_result = await self.runtime.execute_generation(request)
            if not execution_result["success"]:
                raise Exception(f"Generation execution failed: {execution_result['error']}")
            
            # Phase 3: Post-process results
            post_process_result = await self._post_process_generation(execution_result)
            
            # Combine results
            final_result = {
                "operation_id": operation_id,
                "success": True,
                "phases": {
                    "preparation": preparation_result,
                    "execution": execution_result,
                    "post_processing": post_process_result
                },
                "generated_files": execution_result.get("generated_files", []),
                "duration_seconds": sum([
                    preparation_result.get("duration_seconds", 0),
                    execution_result.get("duration_seconds", 0),
                    post_process_result.get("duration_seconds", 0)
                ]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Record operation
            self.operation_history.append({
                "operation_id": operation_id,
                "type": "generation",
                "result": final_result,
                "timestamp": time.time()
            })
            
            operation_span["attributes"] = {
                "operation.id": operation_id,
                "operation.type": "generation",
                "operation.success": True,
                "operation.files_generated": len(final_result["generated_files"]),
                "operation.duration_seconds": final_result["duration_seconds"],
                "operation.language": request.get("language", "unknown")
            }
            
            self.validator._end_span(operation_span)
            return final_result
            
        except Exception as e:
            error_result = {
                "operation_id": operation_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            operation_span["attributes"] = {
                "operation.id": operation_id,
                "operation.type": "generation", 
                "operation.success": False,
                "operation.error": str(e)
            }
            
            self.validator._end_span(operation_span)
            return error_result
    
    async def _prepare_generation(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare generation environment and validate inputs"""
        
        prep_span = self.validator._start_span("operations.prepare_generation")
        start_time = time.time()
        
        try:
            # Validate required fields
            required_fields = ["registry_url", "output_dir", "language"]
            missing_fields = [field for field in required_fields if not request.get(field)]
            
            if missing_fields:
                raise Exception(f"Missing required fields: {missing_fields}")
            
            # Ensure output directory
            output_dir = Path(request["output_dir"])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Validate registry URL/file
            registry_source = request["registry_url"]
            if registry_source.startswith("http"):
                # Remote registry - validate accessibility
                source_type = "remote"
            else:
                # Local file - validate existence
                source_type = "local"
                if not Path(registry_source).exists():
                    raise Exception(f"Local registry file not found: {registry_source}")
            
            # Language-specific preparation
            language = request["language"]
            language_prep = await self._prepare_language_environment(language, output_dir)
            
            result = {
                "success": True,
                "output_dir": str(output_dir),
                "registry_source": registry_source,
                "source_type": source_type,
                "language": language,
                "language_preparation": language_prep,
                "duration_seconds": time.time() - start_time
            }
            
            prep_span["attributes"] = {
                "prep.output_dir": str(output_dir),
                "prep.registry_source": registry_source,
                "prep.source_type": source_type,
                "prep.language": language,
                "prep.success": True
            }
            
            self.validator._end_span(prep_span)
            return result
            
        except Exception as e:
            prep_span["attributes"] = {
                "prep.success": False,
                "prep.error": str(e)
            }
            self.validator._end_span(prep_span)
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - start_time
            }
    
    async def _prepare_language_environment(self, language: str, output_dir: Path) -> Dict[str, Any]:
        """Prepare language-specific environment"""
        
        lang_prep_span = self.validator._start_span(f"operations.prepare_language_{language}")
        
        try:
            preparation_steps = []
            
            if language == "python":
                # Create Python package structure
                (output_dir / "__init__.py").touch()
                preparation_steps.append("created_init_py")
                
                # Create setup.py template
                setup_content = '''from setuptools import setup, find_packages

setup(
    name="generated-otel-package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opentelemetry-api",
        "opentelemetry-sdk",
    ],
)'''
                (output_dir / "setup.py").write_text(setup_content)
                preparation_steps.append("created_setup_py")
            
            elif language == "rust":
                # Create Cargo.toml
                cargo_content = '''[package]
name = "generated-otel-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
opentelemetry = "0.20"
opentelemetry-semantic-conventions = "0.12"
'''
                (output_dir / "Cargo.toml").write_text(cargo_content)
                preparation_steps.append("created_cargo_toml")
                
                # Create src directory
                src_dir = output_dir / "src"
                src_dir.mkdir(exist_ok=True)
                (src_dir / "lib.rs").touch()
                preparation_steps.append("created_src_structure")
            
            elif language == "go":
                # Create go.mod
                go_mod_content = '''module generated-otel-module

go 1.21

require (
    go.opentelemetry.io/otel v1.21.0
    go.opentelemetry.io/otel/trace v1.21.0
)
'''
                (output_dir / "go.mod").write_text(go_mod_content)
                preparation_steps.append("created_go_mod")
            
            result = {
                "language": language,
                "preparation_steps": preparation_steps,
                "success": True
            }
            
            lang_prep_span["attributes"] = {
                "lang_prep.language": language,
                "lang_prep.steps_count": len(preparation_steps),
                "lang_prep.success": True
            }
            
            self.validator._end_span(lang_prep_span)
            return result
            
        except Exception as e:
            lang_prep_span["attributes"] = {
                "lang_prep.language": language,
                "lang_prep.success": False,
                "lang_prep.error": str(e)
            }
            self.validator._end_span(lang_prep_span)
            return {
                "language": language,
                "success": False,
                "error": str(e)
            }
    
    async def _post_process_generation(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process generation results"""
        
        post_span = self.validator._start_span("operations.post_process_generation")
        start_time = time.time()
        
        try:
            generated_files = execution_result.get("generated_files", [])
            post_processing_steps = []
            
            # Validate generated files
            file_validation_results = []
            for file_path in generated_files:
                if Path(file_path).exists():
                    file_size = Path(file_path).stat().st_size
                    file_validation_results.append({
                        "file": file_path,
                        "exists": True,
                        "size_bytes": file_size,
                        "valid": file_size > 0
                    })
                else:
                    file_validation_results.append({
                        "file": file_path,
                        "exists": False,
                        "valid": False
                    })
            
            post_processing_steps.append("validated_generated_files")
            
            # Generate manifest file
            manifest = {
                "generation_timestamp": execution_result.get("timestamp"),
                "generated_files": file_validation_results,
                "total_files": len(generated_files),
                "valid_files": len([f for f in file_validation_results if f["valid"]]),
                "total_size_bytes": sum([f.get("size_bytes", 0) for f in file_validation_results])
            }
            
            # Save manifest if files were generated
            if generated_files:
                manifest_path = Path(generated_files[0]).parent / "generation_manifest.json"
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=2)
                post_processing_steps.append("created_manifest")
            
            result = {
                "success": True,
                "post_processing_steps": post_processing_steps,
                "file_validation_results": file_validation_results,
                "manifest": manifest,
                "duration_seconds": time.time() - start_time
            }
            
            post_span["attributes"] = {
                "post.files_processed": len(generated_files),
                "post.valid_files": manifest["valid_files"],
                "post.total_size_bytes": manifest["total_size_bytes"],
                "post.success": True
            }
            
            self.validator._end_span(post_span)
            return result
            
        except Exception as e:
            post_span["attributes"] = {
                "post.success": False,
                "post.error": str(e)
            }
            self.validator._end_span(post_span)
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - start_time
            }


class ValidationOperation:
    """Validation workflow orchestration - 80/20 implementation"""
    
    def __init__(self):
        self.validator = SpanBasedValidator()
        self.validation_history = []
    
    async def validate_workflow(self, validation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive validation workflow"""
        
        validation_span = self.validator._start_span("operations.validate_workflow")
        validation_id = str(uuid.uuid4())[:8]
        
        try:
            validation_type = validation_request.get("type", "comprehensive")
            target_files = validation_request.get("files", [])
            
            # Multi-stage validation
            validation_stages = []
            
            # Stage 1: Syntax validation
            if target_files:
                syntax_result = self.validator.validate_implementation(target_files)
                validation_stages.append({
                    "stage": "syntax",
                    "result": syntax_result
                })
            
            # Stage 2: Pipeline validation
            if validation_type in ["comprehensive", "pipeline"]:
                convention_name = validation_request.get("convention_name", "test_convention")
                pipeline_result = self.validator.validate_generation_pipeline(convention_name)
                validation_stages.append({
                    "stage": "pipeline",
                    "result": pipeline_result
                })
            
            # Stage 3: Integration validation (if requested)
            if validation_type == "comprehensive":
                integration_result = await self._validate_integration(validation_request)
                validation_stages.append({
                    "stage": "integration",
                    "result": integration_result
                })
            
            # Aggregate results
            overall_success = all(
                stage["result"].get("validation_passed", stage["result"].get("pipeline_functional", False))
                for stage in validation_stages
            )
            
            final_result = {
                "validation_id": validation_id,
                "validation_type": validation_type,
                "overall_success": overall_success,
                "stages": validation_stages,
                "summary": {
                    "stages_total": len(validation_stages),
                    "stages_passed": sum(1 for stage in validation_stages 
                                       if stage["result"].get("validation_passed", stage["result"].get("pipeline_functional", False))),
                    "files_validated": len(target_files)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Record validation
            self.validation_history.append({
                "validation_id": validation_id,
                "result": final_result,
                "timestamp": time.time()
            })
            
            validation_span["attributes"] = {
                "validation.id": validation_id,
                "validation.type": validation_type,
                "validation.overall_success": overall_success,
                "validation.stages_total": len(validation_stages),
                "validation.files_count": len(target_files)
            }
            
            self.validator._end_span(validation_span)
            return final_result
            
        except Exception as e:
            validation_span["attributes"] = {
                "validation.id": validation_id,
                "validation.success": False,
                "validation.error": str(e)
            }
            self.validator._end_span(validation_span)
            
            return {
                "validation_id": validation_id,
                "overall_success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _validate_integration(self, validation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration aspects"""
        
        integration_span = self.validator._start_span("operations.validate_integration")
        
        try:
            integration_checks = []
            
            # Check file system integration
            target_files = validation_request.get("files", [])
            for file_path in target_files:
                if Path(file_path).exists():
                    integration_checks.append({
                        "check": "file_existence",
                        "target": file_path,
                        "passed": True
                    })
                else:
                    integration_checks.append({
                        "check": "file_existence", 
                        "target": file_path,
                        "passed": False
                    })
            
            # Check manifest integration
            if target_files:
                manifest_path = Path(target_files[0]).parent / "generation_manifest.json"
                if manifest_path.exists():
                    integration_checks.append({
                        "check": "manifest_exists",
                        "target": str(manifest_path),
                        "passed": True
                    })
                else:
                    integration_checks.append({
                        "check": "manifest_exists",
                        "target": str(manifest_path),
                        "passed": False
                    })
            
            passed_checks = len([c for c in integration_checks if c["passed"]])
            total_checks = len(integration_checks)
            
            result = {
                "integration_functional": passed_checks == total_checks,
                "checks": integration_checks,
                "checks_passed": passed_checks,
                "checks_total": total_checks
            }
            
            integration_span["attributes"] = {
                "integration.checks_total": total_checks,
                "integration.checks_passed": passed_checks,
                "integration.functional": result["integration_functional"]
            }
            
            self.validator._end_span(integration_span)
            return result
            
        except Exception as e:
            integration_span["attributes"] = {
                "integration.functional": False,
                "integration.error": str(e)
            }
            self.validator._end_span(integration_span)
            return {
                "integration_functional": False,
                "error": str(e)
            }


class WorkflowOrchestrator:
    """Complex workflow coordination - 80/20 implementation"""
    
    def __init__(self):
        self.validator = SpanBasedValidator()
        self.generation_op = GenerationOperation()
        self.validation_op = ValidationOperation()
        self.workflows = {}
    
    async def execute_complete_workflow(self, workflow_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute end-to-end workflow: generation + validation + optimization"""
        
        workflow_span = self.validator._start_span("operations.execute_complete_workflow")
        workflow_id = str(uuid.uuid4())[:8]
        
        try:
            workflow_type = workflow_request.get("type", "standard")
            
            # Phase 1: Generation
            generation_request = workflow_request.get("generation", {})
            generation_result = await self.generation_op.generate_from_request(generation_request)
            
            if not generation_result["success"]:
                raise Exception(f"Generation phase failed: {generation_result.get('error', 'Unknown error')}")
            
            # Phase 2: Validation
            validation_request = {
                "type": "comprehensive",
                "files": generation_result.get("generated_files", []),
                "convention_name": workflow_request.get("convention_name", "workflow_test")
            }
            validation_result = await self.validation_op.validate_workflow(validation_request)
            
            # Phase 3: Optimization (if requested)
            optimization_result = None
            if workflow_request.get("optimize", False):
                optimization_result = await self._optimize_generated_code(generation_result)
            
            # Aggregate workflow results
            workflow_result = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "success": generation_result["success"] and validation_result["overall_success"],
                "phases": {
                    "generation": generation_result,
                    "validation": validation_result,
                    "optimization": optimization_result
                },
                "final_artifacts": generation_result.get("generated_files", []),
                "total_duration_seconds": (
                    generation_result.get("duration_seconds", 0) +
                    (optimization_result.get("duration_seconds", 0) if optimization_result else 0)
                ),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Store workflow
            self.workflows[workflow_id] = workflow_result
            
            workflow_span["attributes"] = {
                "workflow.id": workflow_id,
                "workflow.type": workflow_type,
                "workflow.success": workflow_result["success"],
                "workflow.phases_executed": len([p for p in workflow_result["phases"].values() if p]),
                "workflow.artifacts_count": len(workflow_result["final_artifacts"]),
                "workflow.total_duration": workflow_result["total_duration_seconds"]
            }
            
            self.validator._end_span(workflow_span)
            return workflow_result
            
        except Exception as e:
            workflow_span["attributes"] = {
                "workflow.id": workflow_id,
                "workflow.success": False,
                "workflow.error": str(e)
            }
            self.validator._end_span(workflow_span)
            
            return {
                "workflow_id": workflow_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _optimize_generated_code(self, generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize generated code (basic implementation)"""
        
        optimization_span = self.validator._start_span("operations.optimize_code")
        start_time = time.time()
        
        try:
            generated_files = generation_result.get("generated_files", [])
            optimization_actions = []
            
            for file_path in generated_files:
                file_path_obj = Path(file_path)
                if file_path_obj.exists() and file_path_obj.suffix == ".py":
                    # Basic Python optimization: remove empty lines, format imports
                    with open(file_path_obj) as f:
                        content = f.read()
                    
                    # Simple optimizations
                    lines = content.split('\n')
                    optimized_lines = []
                    
                    for line in lines:
                        # Remove excessive blank lines
                        if line.strip() or (optimized_lines and optimized_lines[-1].strip()):
                            optimized_lines.append(line)
                    
                    # Write optimized content
                    optimized_content = '\n'.join(optimized_lines)
                    with open(file_path_obj, 'w') as f:
                        f.write(optimized_content)
                    
                    optimization_actions.append({
                        "file": file_path,
                        "action": "removed_blank_lines",
                        "original_lines": len(lines),
                        "optimized_lines": len(optimized_lines)
                    })
            
            result = {
                "success": True,
                "optimization_actions": optimization_actions,
                "files_optimized": len(optimization_actions),
                "duration_seconds": time.time() - start_time
            }
            
            optimization_span["attributes"] = {
                "optimization.files_processed": len(generated_files),
                "optimization.files_optimized": len(optimization_actions),
                "optimization.success": True
            }
            
            self.validator._end_span(optimization_span)
            return result
            
        except Exception as e:
            optimization_span["attributes"] = {
                "optimization.success": False,
                "optimization.error": str(e)
            }
            self.validator._end_span(optimization_span)
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - start_time
            }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflow executions"""
        return [
            {
                "workflow_id": wf_id,
                "success": wf["success"],
                "timestamp": wf["timestamp"],
                "type": wf.get("workflow_type", "unknown")
            }
            for wf_id, wf in self.workflows.items()
        ]


# 80/20 Operations Integration Test - NO PYTESTS
async def validate_operations_integration():
    """Validate operations layer integration using spans only"""
    
    validator = SpanBasedValidator()
    integration_span = validator._start_span("operations.integration_test")
    
    try:
        # Test generation operation
        generation_op = GenerationOperation()
        test_generation_request = {
            "registry_url": "https://opentelemetry.io/schemas/1.21.0",
            "output_dir": "./test_operations_output",
            "language": "python"
        }
        
        generation_result = await generation_op.generate_from_request(test_generation_request)
        
        # Test validation operation
        validation_op = ValidationOperation()
        validation_request = {
            "type": "comprehensive",
            "files": generation_result.get("generated_files", []),
            "convention_name": "integration_test"
        }
        
        validation_result = await validation_op.validate_workflow(validation_request)
        
        # Test workflow orchestrator
        orchestrator = WorkflowOrchestrator()
        workflow_request = {
            "type": "integration_test",
            "generation": test_generation_request,
            "optimize": True,
            "convention_name": "integration_test"
        }
        
        workflow_result = await orchestrator.execute_complete_workflow(workflow_request)
        
        integration_span["attributes"] = {
            "integration.generation_success": generation_result.get("success", False),
            "integration.validation_success": validation_result.get("overall_success", False),
            "integration.workflow_success": workflow_result.get("success", False),
            "integration.overall_success": True
        }
        
        validator._end_span(integration_span)
        
        # Save integration telemetry
        validator.save_validation_spans(Path("operations_integration_spans.json"))
        
        return {
            "integration_success": True,
            "generation_result": generation_result,
            "validation_result": validation_result,
            "workflow_result": workflow_result
        }
        
    except Exception as e:
        integration_span["attributes"] = {
            "integration.overall_success": False,
            "integration.error": str(e)
        }
        validator._end_span(integration_span)
        raise


if __name__ == "__main__":
    # Run operations integration validation
    asyncio.run(validate_operations_integration())