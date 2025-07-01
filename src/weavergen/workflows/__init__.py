"""
WeaverGen Workflow Orchestration using SpiffWorkflow

This module integrates SpiffWorkflow for production-ready BPMN workflow execution
with multi-agent coordination and OpenTelemetry observability.
"""

try:
    from .engine import WorkflowEngine, WorkflowContext
    from .agents import AgentWorkflowService
    from .bpmn import BPMNWorkflowLoader
    from .otel import WorkflowSpanManager
except ImportError as e:
    # Handle import errors gracefully
    print(f"Warning: Could not import all workflow components: {e}")
    WorkflowEngine = None
    WorkflowContext = None
    AgentWorkflowService = None
    BPMNWorkflowLoader = None
    WorkflowSpanManager = None

__all__ = [
    "WorkflowEngine",
    "WorkflowContext", 
    "AgentWorkflowService",
    "BPMNWorkflowLoader",
    "WorkflowSpanManager"
]