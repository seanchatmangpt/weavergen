"""Simplified BPMN Engine for WeaverGen v2."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.parser import BpmnParser
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine

from ..enhanced_instrumentation import semantic_span
from .instance import Instance

logger = logging.getLogger(__name__)


class SimpleBpmnEngine:
    """Simplified BPMN workflow engine."""
    
    def __init__(self, script_env=None):
        self.parser = BpmnParser()
        self.workflows: Dict[str, BpmnWorkflow] = {}
        self.specs: Dict[str, Any] = {}
        self._script_engine = PythonScriptEngine(script_env)
    
    @semantic_span("bpmn_engine", "add_spec")
    def add_spec(self, process_id: str, bpmn_files: list) -> str:
        """Add a BPMN specification."""
        # Load BPMN files
        for bpmn_file in bpmn_files:
            self.parser.add_bpmn_file(bpmn_file)
        
        # Get the process specification
        spec = self.parser.get_spec(process_id)
        spec_id = process_id  # Simple ID strategy
        self.specs[spec_id] = spec
        
        logger.info(f'Added {process_id} with id {spec_id}')
        return spec_id
    
    def list_specs(self) -> list:
        """List all specifications."""
        return [(spec_id, spec.name, f"{spec_id}.bpmn") for spec_id, spec in self.specs.items()]
    
    @semantic_span("bpmn_engine", "start_workflow")
    def start_workflow(self, spec_id: str) -> Instance:
        """Start a new workflow instance."""
        if spec_id not in self.specs:
            raise ValueError(f"Specification {spec_id} not found")
        
        spec = self.specs[spec_id]
        wf = BpmnWorkflow(spec, script_engine=self._script_engine)
        wf_id = f"{spec_id}_{len(self.workflows)}"
        self.workflows[wf_id] = wf
        
        logger.info(f'Created workflow with id {wf_id}')
        return Instance(wf_id, wf, save=self.update_workflow)
    
    def get_workflow(self, wf_id: str) -> Instance:
        """Get an existing workflow instance."""
        if wf_id not in self.workflows:
            raise ValueError(f"Workflow {wf_id} not found")
        
        wf = self.workflows[wf_id]
        return Instance(wf_id, wf, save=self.update_workflow)
    
    def update_workflow(self, instance: Instance):
        """Update a workflow instance."""
        logger.info(f'Updated workflow {instance.wf_id}')
        self.workflows[instance.wf_id] = instance.workflow
    
    def list_workflows(self, include_completed: bool = False) -> list:
        """List all workflow instances."""
        workflows = []
        for wf_id, wf in self.workflows.items():
            is_completed = wf.is_completed()
            if not include_completed and is_completed:
                continue
            
            workflows.append((
                wf_id,
                wf.spec.name,
                f"{wf_id}.json",
                not is_completed,
                "2025-01-01T00:00:00",
                None
            ))
        return workflows
    
    def delete_workflow(self, wf_id: str):
        """Delete a workflow instance."""
        if wf_id in self.workflows:
            del self.workflows[wf_id]
            logger.info(f'Deleted workflow with id {wf_id}')
    
    def delete_workflow_spec(self, spec_id: str):
        """Delete a workflow specification."""
        if spec_id in self.specs:
            del self.specs[spec_id]
            logger.info(f'Deleted workflow spec with id {spec_id}')