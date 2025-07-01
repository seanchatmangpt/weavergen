#!/usr/bin/env python3
"""
SpiffWorkflow BPMN Engine Demonstration

Shows how SpiffWorkflow acts as the BPMN engine that controls everything.
"""

import asyncio
from typing import Dict, Any
import os
import sys
from pathlib import Path

# Try to import SpiffWorkflow
try:
    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
    from SpiffWorkflow.bpmn.specs.events import StartEvent, EndEvent
    from SpiffWorkflow.bpmn.specs.user_task import UserTask
    from SpiffWorkflow.bpmn.specs.service_task import ServiceTask
    from SpiffWorkflow.bpmn.specs.exclusive_gateway import ExclusiveGateway
    from SpiffWorkflow.bpmn.specs.parallel_gateway import ParallelGateway
    from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
    from SpiffWorkflow.bpmn.parser.ProcessParser import ProcessParser
    from SpiffWorkflow.task import TaskState
    SPIFF_AVAILABLE = True
except ImportError:
    SPIFF_AVAILABLE = False
    print("⚠️  SpiffWorkflow not available. Install with: pip install SpiffWorkflow")


class SpiffBPMNEngine:
    """
    BPMN Engine using SpiffWorkflow.
    
    The engine is the brain - it executes BPMN and controls agents.
    """
    
    def __init__(self):
        self.agents = {}
        self.parser = BpmnParser() if SPIFF_AVAILABLE else None
        
    def register_agent(self, task_name: str, agent_func):
        """Register an agent function for a task."""
        self.agents[task_name] = agent_func
        print(f"✅ Registered agent for task: {task_name}")
    
    def load_process_from_xml(self, bpmn_file: str):
        """Load BPMN process from XML file."""
        if not SPIFF_AVAILABLE:
            print("❌ SpiffWorkflow not available")
            return None
            
        self.parser.add_bpmn_file(bpmn_file)
        return self.parser.get_spec(self.parser.get_process_ids()[0])
    
    def create_simple_process(self):
        """Create a simple BPMN process programmatically."""
        if not SPIFF_AVAILABLE:
            return self._create_mock_process()
        
        # Create process spec
        spec = BpmnProcessSpec(name="CodeGeneration")
        
        # Define tasks
        start = StartEvent(spec, "start", "Start Process")
        validate = ServiceTask(spec, "validate", "Validate Input")
        gateway = ExclusiveGateway(spec, "check_valid", "Is Valid?")
        analyze = ServiceTask(spec, "analyze", "Analyze Structure")
        gen_python = ServiceTask(spec, "generate_python", "Generate Python")
        gen_go = ServiceTask(spec, "generate_go", "Generate Go")
        end_success = EndEvent(spec, "end_success", "Success")
        end_error = EndEvent(spec, "end_error", "Validation Failed")
        
        # Connect tasks
        start.connect(validate)
        validate.connect(gateway)
        
        # Gateway conditions
        gateway.connect_if(lambda t: t.data.get("is_valid", False), analyze)
        gateway.connect_if(lambda t: not t.data.get("is_valid", False), end_error)
        
        analyze.connect(gen_python)
        gen_python.connect(gen_go)
        gen_go.connect(end_success)
        
        return spec
    
    def _create_mock_process(self):
        """Create a mock process when SpiffWorkflow is not available."""
        return {
            "name": "CodeGeneration",
            "tasks": [
                {"name": "start", "type": "start"},
                {"name": "validate", "type": "service", "next": "check_valid"},
                {"name": "check_valid", "type": "gateway", 
                 "true_next": "analyze", "false_next": "end_error"},
                {"name": "analyze", "type": "service", "next": "generate_python"},
                {"name": "generate_python", "type": "service", "next": "generate_go"},
                {"name": "generate_go", "type": "service", "next": "end_success"},
                {"name": "end_success", "type": "end"},
                {"name": "end_error", "type": "end"}
            ]
        }
    
    async def execute(self, process_spec, initial_data: Dict[str, Any] = None):
        """
        Execute BPMN process with SpiffWorkflow.
        
        THE ENGINE CONTROLS EVERYTHING:
        1. Reads BPMN specification
        2. Manages task execution order
        3. Evaluates gateway conditions
        4. Calls agents for service tasks
        """
        print("\n🚀 SPIFFWORKFLOW ENGINE EXECUTING")
        print("="*60)
        
        if not SPIFF_AVAILABLE:
            return await self._execute_mock(process_spec, initial_data)
        
        # Create workflow instance
        workflow = BpmnWorkflow(process_spec)
        workflow.data = initial_data or {}
        
        # Execute workflow
        while not workflow.is_completed():
            # Get ready tasks
            ready_tasks = workflow.get_ready_user_tasks()
            
            for task in ready_tasks:
                print(f"\n📍 Executing: {task.task_spec.name} [{task.task_spec.__class__.__name__}]")
                
                # SpiffWorkflow controls the flow
                if isinstance(task.task_spec, ServiceTask):
                    # Engine calls the agent
                    agent_name = task.task_spec.name
                    if agent_name in self.agents:
                        print(f"   → ENGINE calls agent: {agent_name}")
                        result = await self.agents[agent_name](task.data)
                        task.data.update(result)
                        print(f"   ← Agent returned: {result}")
                
                # Complete the task
                workflow.complete_task_from_id(task.id)
        
        print("\n✅ SPIFFWORKFLOW EXECUTION COMPLETE")
        return workflow.data
    
    async def _execute_mock(self, process_spec: Dict, initial_data: Dict[str, Any]):
        """Mock execution when SpiffWorkflow is not available."""
        print("\n⚠️  Running in mock mode (SpiffWorkflow not installed)")
        
        data = initial_data or {}
        current_task = "start"
        
        while current_task:
            task = next((t for t in process_spec["tasks"] if t["name"] == current_task), None)
            if not task:
                break
                
            print(f"\n📍 Executing: {task['name']} [{task['type']}]")
            
            if task["type"] == "service" and task["name"] in self.agents:
                print(f"   → ENGINE calls agent: {task['name']}")
                result = await self.agents[task["name"]](data)
                data.update(result)
                print(f"   ← Agent returned: {result}")
            
            # Determine next task
            if task["type"] == "gateway":
                current_task = task["true_next"] if data.get("is_valid") else task["false_next"]
            elif task["type"] == "end":
                current_task = None
            else:
                current_task = task.get("next")
        
        return data


# Agent functions - controlled by the engine
async def validate_agent(data: Dict) -> Dict:
    """Validation agent."""
    await asyncio.sleep(0.5)
    is_valid = "semantic_convention" in data
    print(f"      Validating... {'✅ Valid' if is_valid else '❌ Invalid'}")
    return {"is_valid": is_valid, "validation_result": "valid" if is_valid else "invalid"}


async def analyze_agent(data: Dict) -> Dict:
    """Analysis agent."""
    await asyncio.sleep(0.7)
    print("      Analyzing structure...")
    return {
        "analysis": {
            "attributes": ["method", "status_code"],
            "complexity": "moderate"
        }
    }


async def python_generator_agent(data: Dict) -> Dict:
    """Python generator agent."""
    await asyncio.sleep(1.0)
    print("      Generating Python code...")
    return {
        "python_code": """@dataclass
class HttpAttributes:
    method: str
    status_code: int"""
    }


async def go_generator_agent(data: Dict) -> Dict:
    """Go generator agent."""
    await asyncio.sleep(1.2)
    print("      Generating Go code...")
    return {
        "go_code": """type HttpAttributes struct {
    Method     string `json:"method"`
    StatusCode int    `json:"status_code"`
}"""
    }


async def main():
    """Demonstrate SpiffWorkflow as the BPMN engine."""
    
    print("\n🎯 SPIFFWORKFLOW BPMN ENGINE DEMONSTRATION")
    print("="*60)
    print("SpiffWorkflow is the engine that executes BPMN")
    print("Agents are just functions called by the engine")
    
    # Create engine
    engine = SpiffBPMNEngine()
    
    # Register agents
    engine.register_agent("validate", validate_agent)
    engine.register_agent("analyze", analyze_agent)
    engine.register_agent("generate_python", python_generator_agent)
    engine.register_agent("generate_go", go_generator_agent)
    
    # Create or load process
    process_spec = engine.create_simple_process()
    
    # Execute with data
    input_data = {
        "semantic_convention": {
            "id": "http",
            "attributes": ["method", "status_code"]
        }
    }
    
    # THE ENGINE EXECUTES THE PROCESS
    result = await engine.execute(process_spec, input_data)
    
    print("\n\n📊 SPIFFWORKFLOW EXECUTION ANALYSIS")
    print("="*60)
    
    print("\n1. WHAT IS SPIFFWORKFLOW?")
    print("   ✅ A BPMN 2.0 workflow engine")
    print("   - Reads and parses BPMN XML")
    print("   - Executes process definitions")
    print("   - Manages task states and data")
    print("   - Controls flow through gateways")
    
    print("\n2. HOW DOES IT CONTROL AGENTS?")
    print("   ✅ Engine calls agents for service tasks")
    print("   - Engine determines when to call each agent")
    print("   - Engine passes data to agents")
    print("   - Engine collects results from agents")
    print("   - Agents never call each other")
    
    print("\n3. KEY BENEFITS:")
    print("   • BPMN becomes executable, not just documentation")
    print("   • Process flow is visual and declarative")
    print("   • Changes to flow don't require code changes")
    print("   • Perfect for complex, evolving workflows")
    
    print("\n4. THE CRITICAL INSIGHT:")
    print("   🎯 SPIFFWORKFLOW IS THE APPLICATION")
    print("   - Your code becomes configuration (agents)")
    print("   - Business logic lives in BPMN")
    print("   - SpiffWorkflow orchestrates everything")
    
    if result:
        print("\n5. EXECUTION RESULTS:")
        print(f"   - Validation: {result.get('validation_result', 'N/A')}")
        if "python_code" in result:
            print(f"   - Generated Python: ✅")
        if "go_code" in result:
            print(f"   - Generated Go: ✅")


if __name__ == "__main__":
    asyncio.run(main())