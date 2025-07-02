"""YAML BPMN Parser for WeaverGen."""

from typing import Any, Dict, List, Optional
import yaml
from pathlib import Path
from pydantic import BaseModel, Field


class BPMNTask(BaseModel):
    """BPMN Task definition."""
    id: str
    name: str
    type: str = "serviceTask"
    implementation: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)


class BPMNGateway(BaseModel):
    """BPMN Gateway definition."""
    id: str
    type: str  # exclusive, parallel, inclusive
    name: Optional[str] = None
    conditions: Dict[str, str] = Field(default_factory=dict)


class BPMNSequenceFlow(BaseModel):
    """BPMN Sequence Flow definition."""
    id: str
    source: str
    target: str
    condition: Optional[str] = None


class BPMNProcess(BaseModel):
    """BPMN Process definition."""
    id: str
    name: str
    start_event: str
    end_events: List[str]
    tasks: List[BPMNTask]
    gateways: List[BPMNGateway] = Field(default_factory=list)
    flows: List[BPMNSequenceFlow]
    data_objects: Dict[str, Any] = Field(default_factory=dict)


class YAMLBPMNDefinition(BaseModel):
    """Complete YAML BPMN definition."""
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    process: BPMNProcess
    service_tasks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class YAMLBPMNParser:
    """Parser for YAML-based BPMN definitions."""
    
    def parse_file(self, file_path: Path) -> YAMLBPMNDefinition:
        """Parse YAML BPMN file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return self.parse_definition(data)
    
    def parse_string(self, yaml_content: str) -> YAMLBPMNDefinition:
        """Parse YAML BPMN string."""
        data = yaml.safe_load(yaml_content)
        return self.parse_definition(data)
    
    def parse_definition(self, data: Dict[str, Any]) -> YAMLBPMNDefinition:
        """Parse YAML BPMN definition from dictionary."""
        # Parse process
        process_data = data['process']
        
        # Parse tasks
        tasks = [
            BPMNTask(**task_data)
            for task_data in process_data.get('tasks', [])
        ]
        
        # Parse gateways
        gateways = [
            BPMNGateway(**gateway_data)
            for gateway_data in process_data.get('gateways', [])
        ]
        
        # Parse flows
        flows = [
            BPMNSequenceFlow(**flow_data)
            for flow_data in process_data.get('flows', [])
        ]
        
        # Create process
        process = BPMNProcess(
            id=process_data['id'],
            name=process_data['name'],
            start_event=process_data['start_event'],
            end_events=process_data['end_events'],
            tasks=tasks,
            gateways=gateways,
            flows=flows,
            data_objects=process_data.get('data_objects', {})
        )
        
        # Create definition
        return YAMLBPMNDefinition(
            name=data['name'],
            version=data.get('version', '1.0'),
            description=data.get('description'),
            process=process,
            service_tasks=data.get('service_tasks', {})
        )