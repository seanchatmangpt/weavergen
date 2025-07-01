#!/usr/bin/env python3
"""
BPMN Agent - An agent that executes based on BPMN process definitions.

Instead of agents calling agents, BPMN processes orchestrate agent execution.
The BPMN process IS the logic - agents are just execution units.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from weavergen.otel.mock_tracer import MockTracer


class TaskType(Enum):
    """BPMN task types that can involve AI agents."""
    SERVICE = "serviceTask"
    USER = "userTask"
    BUSINESS_RULE = "businessRuleTask"
    SCRIPT = "scriptTask"
    SEND = "sendTask"
    RECEIVE = "receiveTask"


@dataclass
class BPMNContext:
    """Context passed through BPMN process execution."""
    process_id: str
    instance_id: str
    variables: Dict[str, Any]
    current_task: Optional[str] = None
    execution_path: List[str] = None
    
    def __post_init__(self):
        if self.execution_path is None:
            self.execution_path = []


class BPMNAgent:
    """
    A single agent that executes tasks as directed by BPMN processes.
    
    Key principle: The agent doesn't decide what to do next - the BPMN process does.
    """
    
    def __init__(self, model: Any, system_prompt: str = None):
        """Initialize BPMN Agent with a model."""
        self.agent = Agent(
            model,
            system_prompt=system_prompt or "You are a BPMN task executor. Follow the task instructions precisely."
        )
        self.tracer = MockTracer()
    
    async def execute_task(self, task_definition: Dict[str, Any], context: BPMNContext) -> Any:
        """Execute a single BPMN task based on its definition."""
        
        with self.tracer.start_span(f"bpmn.task.{task_definition.get('id', 'unknown')}") as span:
            span.set_attribute("task.type", task_definition.get("type"))
            span.set_attribute("process.id", context.process_id)
            
            task_type = TaskType(task_definition.get("type", "serviceTask"))
            
            if task_type == TaskType.SERVICE:
                return await self._execute_service_task(task_definition, context)
            elif task_type == TaskType.BUSINESS_RULE:
                return await self._execute_business_rule_task(task_definition, context)
            elif task_type == TaskType.SCRIPT:
                return await self._execute_script_task(task_definition, context)
            else:
                raise NotImplementedError(f"Task type {task_type} not implemented")
    
    async def _execute_service_task(self, task: Dict[str, Any], context: BPMNContext) -> Any:
        """Execute a service task using AI."""
        
        # Extract task instructions from BPMN
        instructions = task.get("documentation", "")
        input_data = self._get_task_inputs(task, context)
        
        # Create prompt from BPMN task definition
        prompt = f"""
Task: {task.get('name', 'Service Task')}
Instructions: {instructions}

Input Data:
{input_data}

Context Variables:
{context.variables}

Execute this task and provide the output.
"""
        
        result = await self.agent.run(prompt)
        
        # Store result in context
        output_var = task.get("outputVariable", f"{task['id']}_output")
        context.variables[output_var] = result.data
        
        return result.data
    
    async def _execute_business_rule_task(self, task: Dict[str, Any], context: BPMNContext) -> Any:
        """Execute a business rule task."""
        
        rules = task.get("rules", [])
        input_data = self._get_task_inputs(task, context)
        
        prompt = f"""
Apply the following business rules to the input data:

Rules:
{chr(10).join(f"- {rule}" for rule in rules)}

Input Data:
{input_data}

Provide the decision result.
"""
        
        result = await self.agent.run(prompt)
        
        # Store decision in context
        decision_var = task.get("decisionVariable", f"{task['id']}_decision")
        context.variables[decision_var] = result.data
        
        return result.data
    
    async def _execute_script_task(self, task: Dict[str, Any], context: BPMNContext) -> Any:
        """Execute a script task."""
        
        script = task.get("script", "")
        
        prompt = f"""
Execute the following transformation:

Script: {script}

Context Variables:
{context.variables}

Provide the transformation result.
"""
        
        result = await self.agent.run(prompt)
        
        # Update context with script results
        if "resultVariable" in task:
            context.variables[task["resultVariable"]] = result.data
        
        return result.data
    
    def _get_task_inputs(self, task: Dict[str, Any], context: BPMNContext) -> Dict[str, Any]:
        """Extract input data for a task from context."""
        inputs = {}
        
        # Get input associations
        for input_assoc in task.get("inputAssociations", []):
            source_var = input_assoc.get("sourceRef")
            target_var = input_assoc.get("targetRef", source_var)
            
            if source_var in context.variables:
                inputs[target_var] = context.variables[source_var]
        
        return inputs


class BPMNProcessEngine:
    """
    Executes BPMN processes by orchestrating agent tasks.
    
    The process engine controls the flow - agents just execute individual tasks.
    """
    
    def __init__(self):
        self.agents: Dict[str, BPMNAgent] = {}
        self.processes: Dict[str, Dict] = {}
        self.tracer = MockTracer()
    
    def register_agent(self, agent_id: str, agent: BPMNAgent):
        """Register an agent that can execute tasks."""
        self.agents[agent_id] = agent
    
    def load_process(self, process_id: str, bpmn_definition: Union[str, Path, Dict]):
        """Load a BPMN process definition."""
        if isinstance(bpmn_definition, dict):
            # Already parsed
            self.processes[process_id] = bpmn_definition
        else:
            # Parse from file or string
            self.processes[process_id] = self._parse_bpmn(bpmn_definition)
    
    async def execute_process(self, process_id: str, initial_variables: Dict[str, Any] = None) -> BPMNContext:
        """Execute a BPMN process."""
        
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        
        process = self.processes[process_id]
        context = BPMNContext(
            process_id=process_id,
            instance_id=f"{process_id}_{asyncio.get_event_loop().time()}",
            variables=initial_variables or {}
        )
        
        with self.tracer.start_span(f"bpmn.process.{process_id}") as span:
            span.set_attribute("process.id", process_id)
            span.set_attribute("instance.id", context.instance_id)
            
            # Start from start event
            current_element = self._find_start_event(process)
            
            while current_element:
                context.execution_path.append(current_element["id"])
                
                element_type = current_element.get("type")
                
                if element_type in ["serviceTask", "userTask", "businessRuleTask", "scriptTask"]:
                    # Execute task with appropriate agent
                    agent_id = current_element.get("agent", "default")
                    agent = self.agents.get(agent_id)
                    
                    if not agent:
                        raise ValueError(f"No agent found for {agent_id}")
                    
                    await agent.execute_task(current_element, context)
                
                elif element_type == "exclusiveGateway":
                    # Evaluate conditions and choose path
                    current_element = self._evaluate_gateway(current_element, context)
                    continue
                
                elif element_type == "parallelGateway":
                    # Execute parallel branches
                    await self._execute_parallel_branches(current_element, context)
                
                elif element_type == "endEvent":
                    # Process complete
                    break
                
                # Move to next element
                current_element = self._get_next_element(current_element, process)
            
            return context
    
    def _parse_bpmn(self, bpmn_source: Union[str, Path]) -> Dict:
        """Parse BPMN XML into internal representation."""
        # Simplified parsing - in production would use full BPMN parser
        return {
            "elements": [],
            "flows": []
        }
    
    def _find_start_event(self, process: Dict) -> Optional[Dict]:
        """Find the start event in a process."""
        for element in process.get("elements", []):
            if element.get("type") == "startEvent":
                return element
        return None
    
    def _get_next_element(self, current: Dict, process: Dict) -> Optional[Dict]:
        """Get the next element in the process flow."""
        # Find outgoing flow
        for flow in process.get("flows", []):
            if flow.get("sourceRef") == current["id"]:
                target_id = flow.get("targetRef")
                # Find target element
                for element in process["elements"]:
                    if element["id"] == target_id:
                        return element
        return None
    
    def _evaluate_gateway(self, gateway: Dict, context: BPMNContext) -> Optional[Dict]:
        """Evaluate gateway conditions and return next element."""
        # Simplified condition evaluation
        conditions = gateway.get("conditions", [])
        for condition in conditions:
            if self._evaluate_condition(condition, context):
                return self._get_element_by_id(condition["targetRef"])
        return None
    
    def _evaluate_condition(self, condition: Dict, context: BPMNContext) -> bool:
        """Evaluate a gateway condition."""
        # Simplified - in production would use expression evaluator
        return True
    
    async def _execute_parallel_branches(self, gateway: Dict, context: BPMNContext):
        """Execute parallel branches concurrently."""
        branches = gateway.get("outgoing", [])
        tasks = []
        
        for branch in branches:
            # Create branch context
            branch_context = BPMNContext(
                process_id=context.process_id,
                instance_id=f"{context.instance_id}_branch_{branch}",
                variables=context.variables.copy()
            )
            # Execute branch
            tasks.append(self._execute_branch(branch, branch_context))
        
        # Wait for all branches
        results = await asyncio.gather(*tasks)
        
        # Merge results back to main context
        for result in results:
            context.variables.update(result.variables)
    
    async def _execute_branch(self, branch_id: str, context: BPMNContext) -> BPMNContext:
        """Execute a single branch of parallel execution."""
        # Simplified branch execution
        return context
    
    def _get_element_by_id(self, element_id: str) -> Optional[Dict]:
        """Get process element by ID."""
        for process in self.processes.values():
            for element in process.get("elements", []):
                if element["id"] == element_id:
                    return element
        return None


# Example BPMN process definition for code generation
EXAMPLE_CODE_GEN_PROCESS = {
    "id": "CodeGenerationProcess",
    "elements": [
        {
            "id": "start",
            "type": "startEvent",
            "name": "Receive Semantic Convention"
        },
        {
            "id": "validate",
            "type": "serviceTask",
            "name": "Validate Semantic Convention",
            "agent": "validator",
            "documentation": "Validate the semantic convention format and completeness",
            "outputVariable": "validation_result"
        },
        {
            "id": "checkValid",
            "type": "exclusiveGateway",
            "name": "Is Valid?",
            "conditions": [
                {
                    "expression": "validation_result.valid == true",
                    "targetRef": "analyze"
                },
                {
                    "expression": "validation_result.valid == false",
                    "targetRef": "error"
                }
            ]
        },
        {
            "id": "analyze",
            "type": "serviceTask",
            "name": "Analyze Semantic Structure",
            "agent": "analyzer",
            "documentation": "Analyze the semantic convention to understand its structure",
            "inputAssociations": [
                {"sourceRef": "semantic_convention", "targetRef": "convention"}
            ],
            "outputVariable": "analysis"
        },
        {
            "id": "splitLanguages",
            "type": "parallelGateway",
            "name": "Generate for Each Language",
            "outgoing": ["python_branch", "go_branch", "rust_branch"]
        },
        {
            "id": "generatePython",
            "type": "serviceTask",
            "name": "Generate Python Code",
            "agent": "python_generator",
            "branch": "python_branch",
            "documentation": "Generate Python code from the semantic convention",
            "inputAssociations": [
                {"sourceRef": "analysis", "targetRef": "semantic_analysis"}
            ],
            "outputVariable": "python_code"
        },
        {
            "id": "generateGo",
            "type": "serviceTask",
            "name": "Generate Go Code",
            "agent": "go_generator",
            "branch": "go_branch",
            "documentation": "Generate Go code from the semantic convention",
            "inputAssociations": [
                {"sourceRef": "analysis", "targetRef": "semantic_analysis"}
            ],
            "outputVariable": "go_code"
        },
        {
            "id": "generateRust",
            "type": "serviceTask",
            "name": "Generate Rust Code",
            "agent": "rust_generator",
            "branch": "rust_branch",
            "documentation": "Generate Rust code from the semantic convention",
            "inputAssociations": [
                {"sourceRef": "analysis", "targetRef": "semantic_analysis"}
            ],
            "outputVariable": "rust_code"
        },
        {
            "id": "mergeResults",
            "type": "parallelGateway",
            "name": "Merge Generated Code"
        },
        {
            "id": "validate_code",
            "type": "businessRuleTask",
            "name": "Validate Generated Code",
            "agent": "code_validator",
            "rules": [
                "Code must be syntactically valid",
                "Code must follow language conventions",
                "Code must include proper documentation"
            ],
            "outputVariable": "code_validation"
        },
        {
            "id": "success",
            "type": "endEvent",
            "name": "Code Generated Successfully"
        },
        {
            "id": "error",
            "type": "endEvent",
            "name": "Generation Failed"
        }
    ],
    "flows": [
        {"sourceRef": "start", "targetRef": "validate"},
        {"sourceRef": "validate", "targetRef": "checkValid"},
        {"sourceRef": "checkValid", "targetRef": "analyze"},
        {"sourceRef": "checkValid", "targetRef": "error"},
        {"sourceRef": "analyze", "targetRef": "splitLanguages"},
        {"sourceRef": "splitLanguages", "targetRef": "generatePython"},
        {"sourceRef": "splitLanguages", "targetRef": "generateGo"},
        {"sourceRef": "splitLanguages", "targetRef": "generateRust"},
        {"sourceRef": "generatePython", "targetRef": "mergeResults"},
        {"sourceRef": "generateGo", "targetRef": "mergeResults"},
        {"sourceRef": "generateRust", "targetRef": "mergeResults"},
        {"sourceRef": "mergeResults", "targetRef": "validate_code"},
        {"sourceRef": "validate_code", "targetRef": "success"}
    ]
}