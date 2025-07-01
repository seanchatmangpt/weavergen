"""
BPMN workflow loader and utilities for SpiffWorkflow integration.

Provides utilities for loading, validating, and executing BPMN workflows
with WeaverGen-specific service task implementations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET

try:
    from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
    from SpiffWorkflow.specs import WorkflowSpec
    SPIFF_AVAILABLE = True
except ImportError:
    # Mock for demonstration when SpiffWorkflow not available
    class MockBpmnParser:
        def add_bpmn_file(self, file_path): pass
        def get_specs(self): return {}
    
    class MockBpmnWorkflow:
        def __init__(self, spec): self.spec = spec
    
    class MockWorkflowSpec:
        def __init__(self, name): self.name = name
    
    BpmnParser = MockBpmnParser
    BpmnWorkflow = MockBpmnWorkflow
    WorkflowSpec = MockWorkflowSpec
    SPIFF_AVAILABLE = False


class BPMNWorkflowLoader:
    """
    Loader for BPMN workflow definitions with WeaverGen integration.
    
    Handles loading, validation, and preparation of BPMN workflows
    for execution with agent service tasks.
    """
    
    def __init__(self, workflow_dir: Optional[Path] = None):
        """Initialize BPMN workflow loader."""
        self.workflow_dir = workflow_dir or Path(__file__).parent / "bpmn"
        self.loaded_specs: Dict[str, WorkflowSpec] = {}
        self.workflow_metadata: Dict[str, Dict[str, Any]] = {}
    
    def load_workflows(self) -> Dict[str, WorkflowSpec]:
        """Load all BPMN workflows from the workflow directory."""
        
        if not SPIFF_AVAILABLE:
            print("⚠️ SpiffWorkflow not available - creating mock workflows")
            return self._create_mock_workflows()
        
        if not self.workflow_dir.exists():
            print(f"⚠️ Workflow directory {self.workflow_dir} not found - creating mock workflows")
            return self._create_mock_workflows()
        
        parser = BpmnParser()
        
        # Load all BPMN files
        bpmn_files = list(self.workflow_dir.glob("*.bpmn"))
        if not bpmn_files:
            print("⚠️ No BPMN files found - creating mock workflows")
            return self._create_mock_workflows()
        
        for bpmn_file in bpmn_files:
            try:
                print(f"📄 Loading BPMN file: {bpmn_file}")
                parser.add_bpmn_file(str(bpmn_file))
                
                # Extract metadata from BPMN file
                self._extract_workflow_metadata(bpmn_file)
                
            except Exception as e:
                print(f"❌ Error loading BPMN file {bpmn_file}: {e}")
        
        # Get loaded specifications
        specs = parser.get_specs()
        self.loaded_specs.update(specs)
        
        print(f"✅ Loaded {len(specs)} workflow specifications")
        return self.loaded_specs
    
    def _create_mock_workflows(self) -> Dict[str, WorkflowSpec]:
        """Create mock workflows when BPMN files are not available."""
        
        mock_specs = {
            "code_generation": WorkflowSpec("code_generation"),
            "validation_workflow": WorkflowSpec("validation_workflow"),
            "agent_coordination": WorkflowSpec("agent_coordination")
        }
        
        # Add mock metadata
        self.workflow_metadata.update({
            "code_generation": {
                "name": "Code Generation Workflow",
                "description": "Main workflow for generating code from semantic conventions",
                "version": "1.0.0",
                "service_tasks": [
                    "validate_semantic_convention",
                    "analyze_semantic_convention", 
                    "execute_multi_agent_generation",
                    "validate_generated_code"
                ]
            },
            "validation_workflow": {
                "name": "Validation Workflow",
                "description": "Comprehensive validation workflow",
                "version": "1.0.0",
                "service_tasks": [
                    "validate_generated_code",
                    "quality_assurance_review"
                ]
            },
            "agent_coordination": {
                "name": "Agent Coordination Workflow",
                "description": "Multi-agent coordination and orchestration",
                "version": "1.0.0",
                "service_tasks": [
                    "execute_multi_agent_generation",
                    "execute_graph_workflow"
                ]
            }
        })
        
        self.loaded_specs.update(mock_specs)
        return mock_specs
    
    def _extract_workflow_metadata(self, bpmn_file: Path):
        """Extract metadata from BPMN file."""
        
        try:
            tree = ET.parse(bpmn_file)
            root = tree.getroot()
            
            # Find process elements
            for process in root.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}process"):
                process_id = process.get("id")
                process_name = process.get("name", process_id)
                
                # Extract service tasks
                service_tasks = []
                for task in process.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}serviceTask"):
                    task_id = task.get("id")
                    task_name = task.get("name", task_id)
                    service_tasks.append({
                        "id": task_id,
                        "name": task_name
                    })
                
                # Extract gateways
                gateways = []
                for gateway in process.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}exclusiveGateway"):
                    gateway_id = gateway.get("id")
                    gateway_name = gateway.get("name", gateway_id)
                    gateways.append({
                        "id": gateway_id,
                        "name": gateway_name,
                        "type": "exclusive"
                    })
                
                for gateway in process.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}parallelGateway"):
                    gateway_id = gateway.get("id")
                    gateway_name = gateway.get("name", gateway_id)
                    gateways.append({
                        "id": gateway_id,
                        "name": gateway_name,
                        "type": "parallel"
                    })
                
                self.workflow_metadata[process_id] = {
                    "name": process_name,
                    "description": f"Workflow loaded from {bpmn_file.name}",
                    "version": "1.0.0",
                    "file": str(bpmn_file),
                    "service_tasks": [task["name"] for task in service_tasks],
                    "gateways": gateways,
                    "task_details": service_tasks
                }
                
        except Exception as e:
            print(f"⚠️ Could not extract metadata from {bpmn_file}: {e}")
    
    def get_workflow_spec(self, workflow_name: str) -> Optional[WorkflowSpec]:
        """Get a specific workflow specification."""
        return self.loaded_specs.get(workflow_name)
    
    def get_workflow_metadata(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific workflow."""
        return self.workflow_metadata.get(workflow_name)
    
    def list_workflows(self) -> List[str]:
        """List all available workflow names."""
        return list(self.loaded_specs.keys())
    
    def validate_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Validate a workflow specification."""
        
        if workflow_name not in self.loaded_specs:
            return {
                "valid": False,
                "errors": [f"Workflow '{workflow_name}' not found"]
            }
        
        metadata = self.workflow_metadata.get(workflow_name, {})
        spec = self.loaded_specs[workflow_name]
        
        errors = []
        warnings = []
        
        # Basic validation
        if not hasattr(spec, 'name') or not spec.name:
            errors.append("Workflow specification missing name")
        
        # Check for required service tasks
        service_tasks = metadata.get("service_tasks", [])
        required_tasks = [
            "validate_semantic_convention",
            "execute_multi_agent_generation"
        ]
        
        for required_task in required_tasks:
            if required_task not in service_tasks:
                warnings.append(f"Missing recommended service task: {required_task}")
        
        # Check for unknown service tasks
        from .agents import AgentWorkflowService
        agent_service = AgentWorkflowService()
        available_tasks = agent_service.get_available_tasks()
        
        for task in service_tasks:
            if task not in available_tasks:
                warnings.append(f"Unknown service task: {task}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata,
            "service_tasks_count": len(service_tasks),
            "available_tasks_count": len(available_tasks)
        }
    
    def create_workflow_instance(self, workflow_name: str) -> Optional[BpmnWorkflow]:
        """Create a workflow instance for execution."""
        
        spec = self.get_workflow_spec(workflow_name)
        if not spec:
            return None
        
        if not SPIFF_AVAILABLE:
            print(f"⚠️ SpiffWorkflow not available - returning mock workflow for {workflow_name}")
            return MockBpmnWorkflow(spec)
        
        return BpmnWorkflow(spec)
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of all loaded workflows."""
        
        summary = {
            "total_workflows": len(self.loaded_specs),
            "spiff_available": SPIFF_AVAILABLE,
            "workflows": {}
        }
        
        for name, metadata in self.workflow_metadata.items():
            validation = self.validate_workflow(name)
            summary["workflows"][name] = {
                "name": metadata.get("name", name),
                "description": metadata.get("description", ""),
                "service_tasks": len(metadata.get("service_tasks", [])),
                "valid": validation["valid"],
                "errors": len(validation["errors"]),
                "warnings": len(validation["warnings"])
            }
        
        return summary