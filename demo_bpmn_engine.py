#!/usr/bin/env python3
"""
BPMN Engine Demonstration - The Core of BPMN-First Architecture

This demonstrates that the BPMN ENGINE is the point:
- It interprets and executes BPMN processes
- It controls all flow and decisions
- Agents are just functions it calls
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time


@dataclass
class ProcessElement:
    """A BPMN process element."""
    id: str
    type: str
    name: str
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class SequenceFlow:
    """A BPMN sequence flow between elements."""
    id: str
    source: str
    target: str
    condition: Optional[str] = None


class SimpleBPMNEngine:
    """
    A simplified BPMN engine that demonstrates the core concept.
    
    THE ENGINE IS THE POINT - it interprets and executes BPMN.
    """
    
    def __init__(self):
        self.processes = {}
        self.agents = {}
        self.execution_log = []
    
    def load_process(self, process_def: Dict[str, Any]):
        """Load a BPMN process definition."""
        process_id = process_def["id"]
        self.processes[process_id] = {
            "elements": {e["id"]: ProcessElement(**e) for e in process_def["elements"]},
            "flows": [SequenceFlow(**f) for f in process_def["flows"]]
        }
        print(f"✅ Loaded process: {process_id}")
    
    def register_agent(self, agent_id: str, agent_func):
        """Register an agent function."""
        self.agents[agent_id] = agent_func
        print(f"✅ Registered agent: {agent_id}")
    
    async def execute(self, process_id: str, initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a BPMN process.
        
        THIS IS THE CORE - The engine controls everything:
        1. Reads BPMN elements
        2. Makes routing decisions
        3. Calls agents when needed
        4. Controls data flow
        """
        print(f"\n🚀 BPMN ENGINE EXECUTING: {process_id}")
        print("="*60)
        
        process = self.processes[process_id]
        context = {"data": initial_data or {}, "variables": {}}
        
        # Find start event
        current = self._find_element_by_type(process, "startEvent")
        
        while current:
            self.execution_log.append(f"Executing: {current.id} ({current.type})")
            print(f"\n📍 {current.name or current.id} [{current.type}]")
            
            # THE ENGINE DECIDES what to do based on element type
            if current.type == "startEvent":
                print("   → Starting process...")
                
            elif current.type == "serviceTask":
                # ENGINE calls the agent
                agent_id = current.attributes.get("agent")
                if agent_id and agent_id in self.agents:
                    print(f"   → ENGINE calls agent: {agent_id}")
                    result = await self.agents[agent_id](context["data"])
                    context["variables"][f"{current.id}_result"] = result
                    print(f"   ← Agent returned: {result}")
                
            elif current.type == "exclusiveGateway":
                # ENGINE makes the routing decision
                print("   → ENGINE evaluating conditions...")
                next_flow = self._evaluate_gateway(current, process, context)
                if next_flow:
                    print(f"   → ENGINE decided: take path to {next_flow.target}")
                    current = process["elements"][next_flow.target]
                    continue
                
            elif current.type == "parallelGateway":
                # ENGINE manages parallel execution
                print("   → ENGINE splitting parallel execution...")
                await self._execute_parallel_branches(current, process, context)
                
            elif current.type == "endEvent":
                print("   → Process complete!")
                break
            
            # ENGINE determines next element
            current = self._get_next_element(current, process)
        
        print("\n✅ BPMN ENGINE EXECUTION COMPLETE")
        print(f"Execution path: {' → '.join(e.split(':')[0] for e in self.execution_log)}")
        
        return context
    
    def _find_element_by_type(self, process: Dict, element_type: str) -> Optional[ProcessElement]:
        """Find first element of given type."""
        for element in process["elements"].values():
            if element.type == element_type:
                return element
        return None
    
    def _get_next_element(self, current: ProcessElement, process: Dict) -> Optional[ProcessElement]:
        """Get next element in sequence flow."""
        for flow in process["flows"]:
            if flow.source == current.id:
                return process["elements"].get(flow.target)
        return None
    
    def _evaluate_gateway(self, gateway: ProcessElement, process: Dict, context: Dict) -> Optional[SequenceFlow]:
        """Evaluate gateway conditions - ENGINE MAKES THE DECISION."""
        for flow in process["flows"]:
            if flow.source == gateway.id:
                if flow.condition:
                    # Simple condition evaluation
                    if "valid" in flow.condition and context["variables"].get("validation_result") == "valid":
                        return flow
                    elif "invalid" in flow.condition and context["variables"].get("validation_result") != "valid":
                        return flow
                else:
                    return flow  # Default flow
        return None
    
    async def _execute_parallel_branches(self, gateway: ProcessElement, process: Dict, context: Dict):
        """Execute parallel branches - ENGINE CONTROLS CONCURRENCY."""
        branches = []
        for flow in process["flows"]:
            if flow.source == gateway.id:
                target = process["elements"].get(flow.target)
                if target and target.type == "serviceTask":
                    agent_id = target.attributes.get("agent")
                    if agent_id in self.agents:
                        print(f"      → Parallel: {target.name}")
                        branches.append(self.agents[agent_id](context["data"]))
        
        # ENGINE waits for all parallel tasks
        results = await asyncio.gather(*branches)
        for i, result in enumerate(results):
            context["variables"][f"parallel_{i}"] = result


# Example agents - just simple functions
async def validator_agent(data: Dict) -> str:
    """Validation agent - just a function."""
    await asyncio.sleep(0.5)  # Simulate work
    return "valid" if data.get("semantic_convention") else "invalid"


async def analyzer_agent(data: Dict) -> Dict:
    """Analysis agent - just a function."""
    await asyncio.sleep(0.7)
    return {"attributes": ["method", "status_code"], "complexity": "moderate"}


async def python_generator_agent(data: Dict) -> str:
    """Python code generator - just a function."""
    await asyncio.sleep(1.0)
    return "class HttpAttributes:\n    method: str\n    status_code: int"


async def go_generator_agent(data: Dict) -> str:
    """Go code generator - just a function."""
    await asyncio.sleep(1.2)
    return "type HttpAttributes struct {\n    Method string\n    StatusCode int\n}"


async def main():
    """Demonstrate that the BPMN ENGINE is the point."""
    
    print("\n🎯 BPMN ENGINE DEMONSTRATION")
    print("="*60)
    print("The ENGINE interprets BPMN and controls everything")
    print("Agents are just functions - they don't control flow")
    
    # Create the engine - THIS IS THE BRAIN
    engine = SimpleBPMNEngine()
    
    # Define a BPMN process
    process_definition = {
        "id": "code_generation",
        "elements": [
            {"id": "start", "type": "startEvent", "name": "Start"},
            {"id": "validate", "type": "serviceTask", "name": "Validate Input", "attributes": {"agent": "validator"}},
            {"id": "check", "type": "exclusiveGateway", "name": "Is Valid?"},
            {"id": "analyze", "type": "serviceTask", "name": "Analyze Structure", "attributes": {"agent": "analyzer"}},
            {"id": "split", "type": "parallelGateway", "name": "Generate Languages"},
            {"id": "python", "type": "serviceTask", "name": "Generate Python", "attributes": {"agent": "python_gen"}},
            {"id": "go", "type": "serviceTask", "name": "Generate Go", "attributes": {"agent": "go_gen"}},
            {"id": "join", "type": "parallelGateway", "name": "Join Results"},
            {"id": "end", "type": "endEvent", "name": "Complete"},
            {"id": "error", "type": "endEvent", "name": "Validation Failed"}
        ],
        "flows": [
            {"id": "f1", "source": "start", "target": "validate"},
            {"id": "f2", "source": "validate", "target": "check"},
            {"id": "f3", "source": "check", "target": "analyze", "condition": "valid"},
            {"id": "f4", "source": "check", "target": "error", "condition": "invalid"},
            {"id": "f5", "source": "analyze", "target": "split"},
            {"id": "f6", "source": "split", "target": "python"},
            {"id": "f7", "source": "split", "target": "go"},
            {"id": "f8", "source": "python", "target": "join"},
            {"id": "f9", "source": "go", "target": "join"},
            {"id": "f10", "source": "join", "target": "end"}
        ]
    }
    
    # Load process into engine
    engine.load_process(process_definition)
    
    # Register agents (just functions)
    engine.register_agent("validator", validator_agent)
    engine.register_agent("analyzer", analyzer_agent)
    engine.register_agent("python_gen", python_generator_agent)
    engine.register_agent("go_gen", go_generator_agent)
    
    # Execute with data
    input_data = {
        "semantic_convention": {
            "id": "http",
            "attributes": ["method", "status_code"]
        }
    }
    
    # THE ENGINE EXECUTES THE PROCESS
    result = await engine.execute("code_generation", input_data)
    
    print("\n\n📊 EXECUTION ANALYSIS")
    print("="*60)
    print("\n1. WHO CONTROLLED THE FLOW?")
    print("   ✅ The BPMN ENGINE")
    print("   - Engine read BPMN elements")
    print("   - Engine made routing decisions")
    print("   - Engine called agents when needed")
    print("   - Engine managed parallel execution")
    
    print("\n2. WHAT DID AGENTS DO?")
    print("   ✅ Only executed their specific tasks")
    print("   - Agents didn't know about other agents")
    print("   - Agents didn't make flow decisions")
    print("   - Agents just transformed data")
    
    print("\n3. KEY INSIGHT:")
    print("   🎯 THE BPMN ENGINE IS THE POINT")
    print("   - Without the engine, BPMN is just XML")
    print("   - The engine brings BPMN to life")
    print("   - The engine IS the application logic")
    
    print("\n4. BENEFITS:")
    print("   • Change flow without changing code")
    print("   • Visual debugging (follow BPMN diagram)")
    print("   • Perfect separation of concerns")
    print("   • Process mining and optimization")


if __name__ == "__main__":
    asyncio.run(main())