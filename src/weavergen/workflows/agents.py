"""
Agent integration for SpiffWorkflow workflows.

Provides workflow service tasks that coordinate with multi-agent systems
and integrate with the WeaverGen 4-layer architecture.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

try:
    from SpiffWorkflow.task import Task
    from SpiffWorkflow.specs.base import TaskSpec
    SPIFF_AVAILABLE = True
except ImportError:
    # Mock classes when SpiffWorkflow not available
    class Task:
        pass
    class TaskSpec:
        pass
    SPIFF_AVAILABLE = False

from ..agents.multi_agent_ollama import (
    semantic_analysis_agent, generation_planning_agent,
    template_selector_agent, code_validator_agent, qa_agent,
    WeaverGenAgentContext, run_generation_workflow,
    MultiAgentWorkflowGraph
)
from ..layers.contracts import (
    GenerationRequest, TargetLanguage, SemanticConvention,
    ExecutionContext, ExecutionStatus
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
class AgentTaskResult:
    """Result of an agent task execution."""
    task_name: str
    agent_name: str
    status: ExecutionStatus
    output: Any
    execution_time_ms: int
    tokens_used: int
    error: Optional[str] = None


class AgentWorkflowService:
    """
    Service for integrating AI agents with SpiffWorkflow.
    
    Provides service task implementations that can be called from BPMN workflows
    and coordinates with multi-agent systems.
    """
    
    def __init__(self):
        """Initialize agent workflow service."""
        self.tracer = trace.get_tracer(__name__) if OTEL_AVAILABLE else None
        self.task_registry: Dict[str, Callable] = {}
        self._register_service_tasks()
    
    def _register_service_tasks(self):
        """Register all service task implementations."""
        self.task_registry.update({
            "validate_semantic_convention": self.validate_semantic_convention,
            "analyze_semantic_convention": self.analyze_semantic_convention,
            "plan_code_generation": self.plan_code_generation,
            "select_templates": self.select_templates,
            "execute_multi_agent_generation": self.execute_multi_agent_generation,
            "validate_generated_code": self.validate_generated_code,
            "quality_assurance_review": self.quality_assurance_review,
            "execute_graph_workflow": self.execute_graph_workflow
        })
    
    async def execute_service_task(
        self, 
        task_name: str, 
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Execute a service task by name."""
        
        if task_name not in self.task_registry:
            raise ValueError(f"Unknown service task: {task_name}")
        
        task_function = self.task_registry[task_name]
        
        if self.tracer:
            with self.tracer.start_span(f"agent.workflow.task.{task_name}") as span:
                span.set_attributes({
                    "agent.task.name": task_name,
                    "agent.context.session_id": context.session_id,
                    "agent.context.user_id": context.user_id
                })
                
                try:
                    start_time = time.time()
                    result = await task_function(task_data, context)
                    execution_time = (time.time() - start_time) * 1000
                    
                    span.set_attributes({
                        "agent.task.execution_time_ms": execution_time,
                        "agent.task.status": result.status.value,
                        "agent.task.tokens_used": result.tokens_used
                    })
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    span.set_attributes({
                        "agent.task.error": str(e)
                    })
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        else:
            # Execute without tracing
            start_time = time.time()
            result = await task_function(task_data, context)
            return result
    
    async def validate_semantic_convention(
        self, 
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Validate semantic convention using basic validation."""
        
        start_time = time.time()
        
        try:
            semantic_convention = task_data.get("semantic_convention")
            if not semantic_convention:
                raise ValueError("No semantic convention provided")
            
            # Basic validation logic
            if not semantic_convention.get("id"):
                raise ValueError("Semantic convention ID is required")
            
            if not semantic_convention.get("brief"):
                raise ValueError("Semantic convention brief is required")
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="validate_semantic_convention",
                agent_name="validation_service",
                status=ExecutionStatus.SUCCESS,
                output={
                    "validation_passed": True,
                    "convention_id": semantic_convention.get("id"),
                    "convention_brief": semantic_convention.get("brief")
                },
                execution_time_ms=int(execution_time),
                tokens_used=0  # No LLM tokens used for basic validation
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="validate_semantic_convention",
                agent_name="validation_service",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    async def analyze_semantic_convention(
        self,
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Analyze semantic convention using AI agent."""
        
        start_time = time.time()
        
        try:
            semantic_convention = task_data.get("semantic_convention")
            if not semantic_convention:
                raise ValueError("No semantic convention provided")
            
            # Use the semantic analysis agent
            analysis_result = await asyncio.wait_for(
                semantic_analysis_agent.run(
                    f"Analyze this semantic convention: {semantic_convention.get('brief', '')}",
                    deps=context
                ),
                timeout=30
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="analyze_semantic_convention",
                agent_name="semantic_analysis_agent",
                status=ExecutionStatus.SUCCESS,
                output=analysis_result.output,
                execution_time_ms=int(execution_time),
                tokens_used=getattr(analysis_result, 'usage', {}).get('total_tokens', 0)
            )
            
        except asyncio.TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="analyze_semantic_convention",
                agent_name="semantic_analysis_agent",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error="Analysis timed out after 30 seconds"
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="analyze_semantic_convention",
                agent_name="semantic_analysis_agent",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    async def plan_code_generation(
        self,
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Plan code generation using AI agent."""
        
        start_time = time.time()
        
        try:
            target_languages = task_data.get("target_languages", [])
            analysis_result = task_data.get("analysis_result", {})
            
            # Use the generation planning agent
            planning_result = await asyncio.wait_for(
                generation_planning_agent.run(
                    f"Create generation plan for languages {target_languages} based on analysis: {analysis_result}",
                    deps=context
                ),
                timeout=30
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="plan_code_generation",
                agent_name="generation_planning_agent",
                status=ExecutionStatus.SUCCESS,
                output=planning_result.output,
                execution_time_ms=int(execution_time),
                tokens_used=getattr(planning_result, 'usage', {}).get('total_tokens', 0)
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="plan_code_generation",
                agent_name="generation_planning_agent",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    async def select_templates(
        self,
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Select templates using AI agent."""
        
        start_time = time.time()
        
        try:
            generation_plan = task_data.get("generation_plan", {})
            
            # Use the template selector agent
            template_result = await asyncio.wait_for(
                template_selector_agent.run(
                    f"Select templates for generation plan: {generation_plan}",
                    deps=context
                ),
                timeout=30
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="select_templates",
                agent_name="template_selector_agent",
                status=ExecutionStatus.SUCCESS,
                output=template_result.output,
                execution_time_ms=int(execution_time),
                tokens_used=getattr(template_result, 'usage', {}).get('total_tokens', 0)
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="select_templates",
                agent_name="template_selector_agent",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    async def execute_multi_agent_generation(
        self,
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Execute multi-agent generation workflow."""
        
        start_time = time.time()
        
        try:
            semantic_convention = SemanticConvention(
                id=task_data.get("semantic_convention", {}).get("id", "workflow.convention"),
                brief=task_data.get("semantic_convention", {}).get("brief", "Workflow semantic convention")
            )
            
            target_languages = [
                TargetLanguage(lang) for lang in task_data.get("target_languages", ["python"])
            ]
            
            # Execute the multi-agent workflow
            workflow_results = await asyncio.wait_for(
                run_generation_workflow(semantic_convention, target_languages, context),
                timeout=300  # 5 minute timeout
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="execute_multi_agent_generation",
                agent_name="multi_agent_workflow",
                status=ExecutionStatus.SUCCESS,
                output=workflow_results,
                execution_time_ms=int(execution_time),
                tokens_used=sum(result.tokens_used for result in workflow_results.values() if hasattr(result, 'tokens_used'))
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="execute_multi_agent_generation",
                agent_name="multi_agent_workflow",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    async def validate_generated_code(
        self,
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Validate generated code using AI agent."""
        
        start_time = time.time()
        
        try:
            generated_files = task_data.get("generated_files", [])
            
            # Use the code validator agent
            validation_result = await asyncio.wait_for(
                code_validator_agent.run(
                    f"Validate generated files: {generated_files}",
                    deps=context
                ),
                timeout=60
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="validate_generated_code",
                agent_name="code_validator_agent",
                status=ExecutionStatus.SUCCESS,
                output=validation_result.output,
                execution_time_ms=int(execution_time),
                tokens_used=getattr(validation_result, 'usage', {}).get('total_tokens', 0)
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="validate_generated_code",
                agent_name="code_validator_agent",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    async def quality_assurance_review(
        self,
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Perform quality assurance review using AI agent."""
        
        start_time = time.time()
        
        try:
            validation_result = task_data.get("validation_result", {})
            
            # Use the QA agent
            qa_result = await asyncio.wait_for(
                qa_agent.run(
                    f"QA review for validated code: {validation_result}",
                    deps=context
                ),
                timeout=60
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="quality_assurance_review",
                agent_name="qa_agent",
                status=ExecutionStatus.SUCCESS,
                output=qa_result.output,
                execution_time_ms=int(execution_time),
                tokens_used=getattr(qa_result, 'usage', {}).get('total_tokens', 0)
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="quality_assurance_review",
                agent_name="qa_agent",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    async def execute_graph_workflow(
        self,
        task_data: Dict[str, Any],
        context: WeaverGenAgentContext
    ) -> AgentTaskResult:
        """Execute graph-based multi-agent workflow."""
        
        start_time = time.time()
        
        try:
            semantic_convention = SemanticConvention(
                id=task_data.get("semantic_convention", {}).get("id", "workflow.convention"),
                brief=task_data.get("semantic_convention", {}).get("brief", "Workflow semantic convention")
            )
            
            # Execute the graph-based workflow
            graph_workflow = MultiAgentWorkflowGraph()
            final_state = await asyncio.wait_for(
                graph_workflow.execute_workflow(semantic_convention, context),
                timeout=300  # 5 minute timeout
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentTaskResult(
                task_name="execute_graph_workflow",
                agent_name="graph_workflow",
                status=ExecutionStatus.SUCCESS,
                output={
                    "completed_steps": final_state.completed_steps,
                    "failed_steps": final_state.failed_steps,
                    "data": final_state.data
                },
                execution_time_ms=int(execution_time),
                tokens_used=0  # Graph workflow manages its own token counting
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentTaskResult(
                task_name="execute_graph_workflow",
                agent_name="graph_workflow",
                status=ExecutionStatus.FAILED,
                output=None,
                execution_time_ms=int(execution_time),
                tokens_used=0,
                error=str(e)
            )
    
    def get_available_tasks(self) -> List[str]:
        """Get list of available service tasks."""
        return list(self.task_registry.keys())
    
    def register_custom_task(self, task_name: str, task_function: Callable):
        """Register a custom service task."""
        self.task_registry[task_name] = task_function