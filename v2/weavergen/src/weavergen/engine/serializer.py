"""Simple file-based serializer for WeaverGen workflows."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.util.deep_merge import DeepMerge


class FileSerializer:
    """File-based workflow serializer."""
    
    def __init__(self, data_dir: str = "wf_data", registry=None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.registry = registry
        self.workflow_serializer = BpmnWorkflowSerializer()
        
        # Create subdirectories
        (self.data_dir / "specs").mkdir(exist_ok=True)
        (self.data_dir / "workflows").mkdir(exist_ok=True)
    
    def create_workflow_spec(self, spec, dependencies: Dict[str, Any]) -> str:
        """Save a workflow specification."""
        spec_id = str(uuid.uuid4())
        spec_data = {
            'id': spec_id,
            'name': spec.name,
            'spec': self.workflow_serializer.spec_to_dict(spec),
            'dependencies': {
                name: self.workflow_serializer.spec_to_dict(dep_spec)
                for name, dep_spec in dependencies.items()
            },
            'created': datetime.now().isoformat()
        }
        
        spec_path = self.data_dir / "specs" / f"{spec_id}.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f, indent=2)
        
        return spec_id
    
    def get_workflow_spec(self, spec_id: str, include_dependencies: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """Load a workflow specification."""
        spec_path = self.data_dir / "specs" / f"{spec_id}.json"
        with open(spec_path, 'r') as f:
            spec_data = json.load(f)
        
        spec = self.workflow_serializer.spec_from_dict(spec_data['spec'])
        
        dependencies = {}
        if include_dependencies:
            for name, dep_data in spec_data.get('dependencies', {}).items():
                dependencies[name] = self.workflow_serializer.spec_from_dict(dep_data)
        
        return spec, dependencies
    
    def list_specs(self) -> List[Tuple[str, str, str]]:
        """List all available workflow specifications."""
        specs = []
        for spec_file in (self.data_dir / "specs").glob("*.json"):
            with open(spec_file, 'r') as f:
                spec_data = json.load(f)
            specs.append((
                spec_data['id'],
                spec_data['name'],
                spec_file.name
            ))
        return specs
    
    def delete_workflow_spec(self, spec_id: str):
        """Delete a workflow specification."""
        spec_path = self.data_dir / "specs" / f"{spec_id}.json"
        if spec_path.exists():
            spec_path.unlink()
    
    def create_workflow(self, workflow: BpmnWorkflow, spec_id: str) -> str:
        """Save a workflow instance."""
        wf_id = str(uuid.uuid4())
        wf_data = {
            'id': wf_id,
            'spec_id': spec_id,
            'workflow': self.workflow_serializer.to_dict(workflow),
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }
        
        wf_path = self.data_dir / "workflows" / f"{wf_id}.json"
        with open(wf_path, 'w') as f:
            json.dump(wf_data, f, indent=2)
        
        return wf_id
    
    def get_workflow(self, wf_id: str) -> BpmnWorkflow:
        """Load a workflow instance."""
        wf_path = self.data_dir / "workflows" / f"{wf_id}.json"
        with open(wf_path, 'r') as f:
            wf_data = json.load(f)
        
        return self.workflow_serializer.from_dict(wf_data['workflow'])
    
    def update_workflow(self, workflow: BpmnWorkflow, wf_id: str):
        """Update a workflow instance."""
        wf_path = self.data_dir / "workflows" / f"{wf_id}.json"
        with open(wf_path, 'r') as f:
            wf_data = json.load(f)
        
        wf_data['workflow'] = self.workflow_serializer.to_dict(workflow)
        wf_data['updated'] = datetime.now().isoformat()
        
        with open(wf_path, 'w') as f:
            json.dump(wf_data, f, indent=2)
    
    def list_workflows(self, include_completed: bool = False) -> List[Tuple[str, str, str, bool, str, Optional[str]]]:
        """List all workflow instances."""
        workflows = []
        for wf_file in (self.data_dir / "workflows").glob("*.json"):
            with open(wf_file, 'r') as f:
                wf_data = json.load(f)
            
            # Simple check - in real implementation would deserialize and check
            is_active = True  # Placeholder
            
            if not include_completed and not is_active:
                continue
                
            workflows.append((
                wf_data['id'],
                wf_data.get('name', 'Workflow'),
                wf_file.name,
                is_active,
                wf_data['created'],
                wf_data.get('updated')
            ))
        return workflows
    
    def delete_workflow(self, wf_id: str):
        """Delete a workflow instance."""
        wf_path = self.data_dir / "workflows" / f"{wf_id}.json"
        if wf_path.exists():
            wf_path.unlink()