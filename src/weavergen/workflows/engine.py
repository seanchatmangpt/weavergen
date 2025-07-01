"""
SpiffWorkflow-based Workflow Engine for WeaverGen

Integrates BPMN workflow execution with multi-agent coordination,
OpenTelemetry observability, and the 4-layer architecture.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from SpiffWorkflow import Workflow
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import Task, TaskState
from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser

from ..layers.contracts import (
    GenerationRequest, GenerationResult, ExecutionContext, 
    ExecutionStatus, TargetLanguage, SemanticConvention
)
from ..agents.multi_agent_ollama import (
    WeaverGenAgentContext, run_generation_workflow,
    MultiAgentWorkflowGraph
)

try:
    from opentelemetry import trace
    from opentelemetry.trace.status import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    # Mock for demonstration
    class MockTracer:
        def start_span(self, name, context=None):
            class MockSpan:
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def set_attributes(self, attrs): pass
                def set_status(self, status): pass
            return MockSpan()
    
    trace = type('MockTrace', (), {'get_tracer': lambda x: MockTracer()})()
    Status = type('MockStatus', (), {})()
    StatusCode = type('MockStatusCode', (), {'OK': 'OK', 'ERROR': 'ERROR'})()
    OTEL_AVAILABLE = False


@dataclass
class WorkflowContext:
    """Context for workflow execution with multi-agent support."""
    
    # Workflow identification
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = "system"
    
    # Generation request
    generation_request: Optional[GenerationRequest] = None
    execution_context: Optional[ExecutionContext] = None
    
    # Agent context
    agent_context: Optional[WeaverGenAgentContext] = None
    
    # Workflow state
    workflow_data: Dict[str, Any] = field(default_factory=dict)
    task_results: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_execution_time: Optional[float] = None
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add an error to the context."""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a warning to the context."""
        self.warnings.append(warning)
    
    def mark_completed(self):
        """Mark workflow as completed and calculate execution time."""
        self.end_time = time.time()
        self.total_execution_time = self.end_time - self.start_time
    
    def has_errors(self) -> bool:
        """Check if workflow has any errors."""
        return len(self.errors) > 0


class WorkflowEngine:
    """
    SpiffWorkflow-based engine for WeaverGen workflow orchestration.
    
    Coordinates BPMN workflows with multi-agent execution and OpenTelemetry tracing.
    """
    
    def __init__(self, workflow_dir: Optional[Path] = None):
        """Initialize workflow engine."""
        self.workflow_dir = workflow_dir or Path(__file__).parent / "bpmn"
        self.tracer = trace.get_tracer(__name__) if OTEL_AVAILABLE else None
        self.active_workflows: Dict[str, BpmnWorkflow] = {}
        self.workflow_contexts: Dict[str, WorkflowContext] = {}
        
        # Initialize workflow specifications
        self._workflow_specs: Dict[str, WorkflowSpec] = {}
        self._load_workflow_specs()
    
    def _load_workflow_specs(self):
        """Load BPMN workflow specifications."""
        try:
            if self.workflow_dir.exists():
                for bpmn_file in self.workflow_dir.glob("*.bpmn"):
                    self._load_bpmn_spec(bpmn_file)
        except Exception as e:
            print(f"Warning: Could not load BPMN specs: {e}")
            # Create default programmatic workflows
            self._create_default_workflows()
    
    def _load_bpmn_spec(self, bpmn_file: Path):
        """Load a single BPMN specification."""
        try:
            parser = BpmnParser()
            parser.add_bpmn_file(str(bpmn_file))
            
            for spec_name, spec in parser.get_specs().items():
                self._workflow_specs[spec_name] = spec
                print(f"Loaded BPMN workflow: {spec_name}")
                
        except Exception as e:
            print(f"Error loading BPMN file {bpmn_file}: {e}")
    
    def _create_default_workflows(self):
        """Create default programmatic workflows when BPMN files not available."""
        # For now, we'll use programmatic workflow creation
        # In production, these would be proper BPMN files
        print("Creating default programmatic workflows...")
    
    async def execute_generation_workflow(
        self, 
        request: GenerationRequest,
        context: ExecutionContext,
        workflow_name: str = "code_generation"
    ) -> WorkflowContext:
        """Execute the code generation workflow."""
        
        workflow_context = WorkflowContext(
            generation_request=request,
            execution_context=context,
            agent_context=WeaverGenAgentContext(
                session_id=str(uuid4()),
                user_id="workflow_engine",
                working_directory=context.working_directory,
                semantic_conventions={request.semantic_convention.id: request.semantic_convention},
                template_cache={},
                generation_results={}
            )
        )
        
        if self.tracer:
            with self.tracer.start_span("workflow.generation.execute") as span:
                span.set_attributes({
                    "workflow.id": workflow_context.workflow_id,
                    "workflow.name": workflow_name,
                    "workflow.semantic_convention": request.semantic_convention.id,
                    "workflow.target_languages": ",".join([lang.value for lang in request.target_languages])
                })
                
                try:
                    result = await self._execute_workflow_steps(workflow_context)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    workflow_context.add_error(f"Workflow execution failed: {e}")
                    raise
        else:
            return await self._execute_workflow_steps(workflow_context)
    
    async def _execute_workflow_steps(self, context: WorkflowContext) -> WorkflowContext:
        """Execute the workflow steps programmatically."""
        
        # Step 1: Validate Semantic Convention
        await self._execute_step(
            context, 
            "validate_semantic",
            self._validate_semantic_convention
        )
        
        # Step 2: Initialize Generation Environment
        await self._execute_step(
            context,
            "initialize_environment", 
            self._initialize_generation_environment
        )
        
        # Step 3: Multi-Agent Code Generation
        await self._execute_step(
            context,
            "multi_agent_generation",
            self._execute_multi_agent_generation
        )
        
        # Step 4: Template Processing
        await self._execute_step(
            context,
            "template_processing",
            self._process_templates
        )
        
        # Step 5: File Generation
        await self._execute_step(
            context,
            "file_generation", 
            self._generate_files
        )
        
        # Step 6: Validation and Quality Assurance
        await self._execute_step(
            context,
            "validation_qa",
            self._validate_and_qa
        )
        
        # Step 7: Finalization
        await self._execute_step(
            context,
            "finalization",
            self._finalize_generation
        )
        
        context.mark_completed()
        return context
    
    async def _execute_step(
        self, 
        context: WorkflowContext,
        step_name: str,
        step_function
    ):
        """Execute a single workflow step with tracing."""
        
        step_span_name = f"workflow.step.{step_name}"
        
        if self.tracer:
            with self.tracer.start_span(step_span_name) as span:
                span.set_attributes({
                    "workflow.step.name": step_name,
                    "workflow.id": context.workflow_id
                })
                
                try:
                    start_time = time.time()
                    result = await step_function(context)
                    execution_time = (time.time() - start_time) * 1000
                    
                    span.set_attributes({
                        "workflow.step.execution_time_ms": execution_time,
                        "workflow.step.status": "success"
                    })
                    
                    context.task_results[step_name] = {
                        "status": "success",
                        "execution_time_ms": execution_time,
                        "result": result
                    }
                    
                    span.set_status(Status(StatusCode.OK))
                    
                except Exception as e:
                    span.set_attributes({
                        "workflow.step.status": "failed",
                        "workflow.step.error": str(e)
                    })
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    context.add_error(f"Step {step_name} failed: {e}")
                    context.task_results[step_name] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    raise
        else:
            # Execute without tracing
            try:
                start_time = time.time()
                result = await step_function(context)
                execution_time = (time.time() - start_time) * 1000
                
                context.task_results[step_name] = {
                    "status": "success",
                    "execution_time_ms": execution_time,
                    "result": result
                }
            except Exception as e:
                context.add_error(f"Step {step_name} failed: {e}")
                context.task_results[step_name] = {
                    "status": "failed", 
                    "error": str(e)
                }
                raise
    
    async def _validate_semantic_convention(self, context: WorkflowContext) -> Dict[str, Any]:
        """Validate the semantic convention."""
        semantic_convention = context.generation_request.semantic_convention
        
        # Basic validation
        if not semantic_convention.id:
            raise ValueError("Semantic convention ID is required")
        
        if not semantic_convention.brief:
            raise ValueError("Semantic convention brief is required") 
        
        return {
            "validation_status": "passed",
            "convention_id": semantic_convention.id,
            "convention_brief": semantic_convention.brief
        }
    
    async def _initialize_generation_environment(self, context: WorkflowContext) -> Dict[str, Any]:
        """Initialize the generation environment."""
        
        # Create output directory if it doesn't exist
        output_dir = context.generation_request.output_directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize workspace
        workspace = {
            "output_directory": str(output_dir),
            "target_languages": [lang.value for lang in context.generation_request.target_languages],
            "working_directory": str(context.execution_context.working_directory)
        }
        
        context.workflow_data["workspace"] = workspace
        
        return {
            "environment_status": "initialized",
            "workspace": workspace
        }
    
    async def _execute_multi_agent_generation(self, context: WorkflowContext) -> Dict[str, Any]:
        """Execute multi-agent code generation workflow."""
        
        try:
            # Use the existing multi-agent workflow
            agent_results = await asyncio.wait_for(
                run_generation_workflow(
                    context.generation_request.semantic_convention,
                    context.generation_request.target_languages,
                    context.agent_context
                ),
                timeout=300  # 5 minute timeout
            )
            
            # Store agent results in workflow context
            context.workflow_data["agent_results"] = agent_results
            
            return {
                "generation_status": "completed",
                "agent_results_count": len(agent_results),
                "agents_executed": list(agent_results.keys())
            }
            
        except asyncio.TimeoutError:
            raise Exception("Multi-agent generation timed out after 5 minutes")
        except Exception as e:
            raise Exception(f"Multi-agent generation failed: {e}")
    
    async def _process_templates(self, context: WorkflowContext) -> Dict[str, Any]:
        """Process templates for code generation."""
        
        # For now, simulate template processing
        # In production, this would use the actual template engine
        
        languages = context.generation_request.target_languages
        templates_processed = []
        
        for language in languages:
            template_info = {
                "language": language.value,
                "templates": [f"{language.value}/models.j2", f"{language.value}/instrumentation.j2"],
                "processed_at": time.time()
            }
            templates_processed.append(template_info)
        
        context.workflow_data["templates"] = templates_processed
        
        return {
            "template_status": "processed",
            "templates_count": len(templates_processed),
            "languages": [lang.value for lang in languages]
        }
    
    async def _generate_files(self, context: WorkflowContext) -> Dict[str, Any]:
        """Generate the output files."""
        
        # For now, simulate file generation
        # In production, this would use the actual Weaver CLI integration
        
        output_dir = context.generation_request.output_directory
        languages = context.generation_request.target_languages
        generated_files = []
        
        for language in languages:
            lang_dir = output_dir / language.value
            lang_dir.mkdir(exist_ok=True)
            
            # Simulate generating files
            files = [
                lang_dir / "models.py" if language == TargetLanguage.PYTHON else lang_dir / "models.go",
                lang_dir / "instrumentation.py" if language == TargetLanguage.PYTHON else lang_dir / "instrumentation.go"
            ]
            
            for file_path in files:
                # Create placeholder files
                file_path.write_text(f"// Generated code for {language.value}\n// Semantic convention: {context.generation_request.semantic_convention.id}\n")
                generated_files.append(str(file_path))
        
        context.workflow_data["generated_files"] = generated_files
        
        return {
            "generation_status": "completed",
            "files_generated": len(generated_files),
            "output_directory": str(output_dir)
        }
    
    async def _validate_and_qa(self, context: WorkflowContext) -> Dict[str, Any]:
        """Validate generated code and perform quality assurance."""
        
        generated_files = context.workflow_data.get("generated_files", [])
        
        # Basic validation
        validation_results = []
        for file_path in generated_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                validation_results.append({
                    "file": str(file_path),
                    "exists": True,
                    "size_bytes": file_obj.stat().st_size,
                    "valid": True
                })
            else:
                validation_results.append({
                    "file": str(file_path),
                    "exists": False,
                    "valid": False
                })
        
        context.workflow_data["validation_results"] = validation_results
        
        return {
            "validation_status": "completed",
            "files_validated": len(validation_results),
            "all_valid": all(result["valid"] for result in validation_results)
        }
    
    async def _finalize_generation(self, context: WorkflowContext) -> Dict[str, Any]:
        """Finalize the generation process."""
        
        # Create summary
        summary = {
            "workflow_id": context.workflow_id,
            "semantic_convention": context.generation_request.semantic_convention.id,
            "target_languages": [lang.value for lang in context.generation_request.target_languages],
            "files_generated": len(context.workflow_data.get("generated_files", [])),
            "execution_time_seconds": context.total_execution_time,
            "status": "completed" if not context.has_errors() else "failed_with_errors",
            "errors": context.errors,
            "warnings": context.warnings
        }
        
        context.workflow_data["summary"] = summary
        
        return summary
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow."""
        
        context = self.workflow_contexts.get(workflow_id)
        if not context:
            return None
        
        return {
            "workflow_id": workflow_id,
            "status": "completed" if context.end_time else "running",
            "start_time": context.start_time,
            "end_time": context.end_time,
            "execution_time": context.total_execution_time,
            "errors": context.errors,
            "warnings": context.warnings,
            "task_results": context.task_results
        }
    
    def list_active_workflows(self) -> List[str]:
        """List all active workflow IDs."""
        return [
            wf_id for wf_id, context in self.workflow_contexts.items()
            if context.end_time is None
        ]
    
    def get_workflow_summary(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a completed workflow."""
        context = self.workflow_contexts.get(workflow_id)
        if not context or not context.end_time:
            return None
        
        return context.workflow_data.get("summary")