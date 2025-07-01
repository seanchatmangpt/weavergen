#!/usr/bin/env python3
"""
Working SpiffWorkflow Example - Showing the Engine in Action

This demonstrates SpiffWorkflow as THE engine that executes BPMN.
"""

import asyncio
from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser


# Create a simple BPMN process programmatically
def create_code_generation_process():
    """Create a BPMN process specification programmatically."""
    
    # Create parser
    parser = BpmnParser()
    
    # Add process with inline BPMN
    bpmn_xml = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:camunda="http://camunda.org/schema/1.0/bpmn"
                  id="Definitions_1">
                  
  <bpmn:process id="CodeGeneration" name="Code Generation Process" isExecutable="true">
    
    <bpmn:startEvent id="Start" name="Start">
      <bpmn:outgoing>Flow1</bpmn:outgoing>
    </bpmn:startEvent>
    
    <bpmn:serviceTask id="ValidateInput" name="Validate Input">
      <bpmn:incoming>Flow1</bpmn:incoming>
      <bpmn:outgoing>Flow2</bpmn:outgoing>
    </bpmn:serviceTask>
    
    <bpmn:exclusiveGateway id="IsValid" name="Is Valid?">
      <bpmn:incoming>Flow2</bpmn:incoming>
      <bpmn:outgoing>FlowValid</bpmn:outgoing>
      <bpmn:outgoing>FlowInvalid</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    
    <bpmn:serviceTask id="AnalyzeStructure" name="Analyze Structure">
      <bpmn:incoming>FlowValid</bpmn:incoming>
      <bpmn:outgoing>Flow3</bpmn:outgoing>
    </bpmn:serviceTask>
    
    <bpmn:serviceTask id="GenerateCode" name="Generate Code">
      <bpmn:incoming>Flow3</bpmn:incoming>
      <bpmn:outgoing>Flow4</bpmn:outgoing>
    </bpmn:serviceTask>
    
    <bpmn:endEvent id="EndSuccess" name="Success">
      <bpmn:incoming>Flow4</bpmn:incoming>
    </bpmn:endEvent>
    
    <bpmn:endEvent id="EndError" name="Error">
      <bpmn:incoming>FlowInvalid</bpmn:incoming>
    </bpmn:endEvent>
    
    <!-- Sequence Flows -->
    <bpmn:sequenceFlow id="Flow1" sourceRef="Start" targetRef="ValidateInput"/>
    <bpmn:sequenceFlow id="Flow2" sourceRef="ValidateInput" targetRef="IsValid"/>
    <bpmn:sequenceFlow id="FlowValid" sourceRef="IsValid" targetRef="AnalyzeStructure">
      <bpmn:conditionExpression>is_valid == True</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="FlowInvalid" sourceRef="IsValid" targetRef="EndError">
      <bpmn:conditionExpression>is_valid == False</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow3" sourceRef="AnalyzeStructure" targetRef="GenerateCode"/>
    <bpmn:sequenceFlow id="Flow4" sourceRef="GenerateCode" targetRef="EndSuccess"/>
    
  </bpmn:process>
</bpmn:definitions>"""
    
    # Parse the BPMN
    parser.add_bpmn_xml(bpmn_xml, filename="code_generation.bpmn")
    
    # Get the process specification
    spec = parser.get_spec("CodeGeneration")
    
    return parser, spec


# Agent functions - these are called BY SpiffWorkflow
async def validate_input_handler(task):
    """Handler for ValidateInput service task."""
    print("   🤖 AGENT: Validating input...")
    
    # Simulate validation
    await asyncio.sleep(0.5)
    
    # Check if we have semantic convention data
    is_valid = "semantic_convention" in task.data
    task.data["is_valid"] = is_valid
    
    print(f"   ✅ AGENT: Validation {'passed' if is_valid else 'failed'}")
    return task.data


async def analyze_structure_handler(task):
    """Handler for AnalyzeStructure service task."""
    print("   🤖 AGENT: Analyzing structure...")
    
    await asyncio.sleep(0.7)
    
    task.data["analysis"] = {
        "attributes": ["method", "status_code"],
        "complexity": "moderate"
    }
    
    print("   ✅ AGENT: Analysis complete")
    return task.data


async def generate_code_handler(task):
    """Handler for GenerateCode service task."""
    print("   🤖 AGENT: Generating code...")
    
    await asyncio.sleep(1.0)
    
    task.data["generated_code"] = {
        "python": "class HttpAttributes:\n    method: str\n    status_code: int",
        "go": "type HttpAttributes struct {\n    Method string\n    StatusCode int\n}"
    }
    
    print("   ✅ AGENT: Code generated")
    return task.data


# Service task handlers mapping
SERVICE_HANDLERS = {
    "ValidateInput": validate_input_handler,
    "AnalyzeStructure": analyze_structure_handler,
    "GenerateCode": generate_code_handler
}


async def execute_with_spiffworkflow():
    """Execute BPMN process using SpiffWorkflow as the engine."""
    
    print("\n🚀 SPIFFWORKFLOW ENGINE EXECUTION")
    print("="*60)
    
    # Create process specification
    parser, spec = create_code_generation_process()
    
    # Create workflow instance - SpiffWorkflow manages everything
    workflow = BpmnWorkflow(spec)
    
    # Set initial data
    workflow.data = {
        "semantic_convention": {
            "id": "http",
            "attributes": ["method", "status_code"]
        }
    }
    
    print("\n📋 Starting workflow with SpiffWorkflow engine...")
    print(f"   Initial data: {workflow.data}")
    
    # SPIFFWORKFLOW EXECUTES THE PROCESS
    step = 1
    while not workflow.is_completed():
        # Get tasks that are ready to execute
        ready_tasks = workflow.get_ready_user_tasks()
        
        for task in ready_tasks:
            print(f"\n{step}. SpiffWorkflow at: {task.task_spec.name}")
            print(f"   State: {task.get_state_name()}")
            
            # If it's a service task, SpiffWorkflow calls our handler
            if task.task_spec.name in SERVICE_HANDLERS:
                print("   → SpiffWorkflow calling agent handler...")
                handler = SERVICE_HANDLERS[task.task_spec.name]
                
                # Execute the handler
                await handler(task)
                
                # Complete the task in SpiffWorkflow
                workflow.complete_task_from_id(task.id)
                print("   ← SpiffWorkflow received result")
            else:
                # For non-service tasks, just complete them
                workflow.complete_task_from_id(task.id)
            
            step += 1
    
    print("\n✅ SpiffWorkflow completed the workflow!")
    
    # Show final state
    print("\n📊 FINAL WORKFLOW STATE:")
    print(f"   Completed: {workflow.is_completed()}")
    print(f"   Last task: {workflow.last_task.task_spec.name if workflow.last_task else 'None'}")
    
    # Show task execution history
    print("\n📜 TASK EXECUTION HISTORY:")
    for task in workflow.get_tasks():
        if task.state == TaskState.COMPLETED:
            print(f"   ✓ {task.task_spec.name}")
    
    return workflow.data


def explain_spiffworkflow_control():
    """Explain how SpiffWorkflow controls everything."""
    
    print("\n\n🎯 HOW SPIFFWORKFLOW CONTROLS EVERYTHING")
    print("="*60)
    
    print("\n1. WORKFLOW CREATION:")
    print("   workflow = BpmnWorkflow(spec)")
    print("   → SpiffWorkflow creates task instances from BPMN")
    
    print("\n2. TASK STATE MANAGEMENT:")
    print("   States: FUTURE → WAITING → READY → COMPLETED")
    print("   → SpiffWorkflow manages all state transitions")
    
    print("\n3. EXECUTION CONTROL:")
    print("   while not workflow.is_completed():")
    print("       ready_tasks = workflow.get_ready_user_tasks()")
    print("   → SpiffWorkflow determines what's ready to run")
    
    print("\n4. AGENT INVOCATION:")
    print("   handler = get_handler(task.name)")
    print("   await handler(task)")
    print("   → SpiffWorkflow calls agents at the right time")
    
    print("\n5. FLOW DECISIONS:")
    print("   Gateway conditions evaluated by SpiffWorkflow")
    print("   → SpiffWorkflow chooses the path, not agents")
    
    print("\n6. DATA MANAGEMENT:")
    print("   task.data flows through the process")
    print("   → SpiffWorkflow manages data between tasks")


async def main():
    """Run the SpiffWorkflow demonstration."""
    
    print("\n" + "⚙️ "*20)
    print("SPIFFWORKFLOW: THE ENGINE IN ACTION")
    print("⚙️ "*20)
    
    print("\nThis demonstrates that SpiffWorkflow IS the engine.")
    print("It controls the flow, manages state, and calls agents.")
    
    # Execute with SpiffWorkflow
    result = await execute_with_spiffworkflow()
    
    # Explain the control
    explain_spiffworkflow_control()
    
    # Show results
    print("\n\n📤 EXECUTION RESULTS:")
    print("="*60)
    print(f"Validation: {'✅ Passed' if result.get('is_valid') else '❌ Failed'}")
    if "analysis" in result:
        print(f"Analysis: {result['analysis']}")
    if "generated_code" in result:
        print("Generated code:")
        for lang, code in result["generated_code"].items():
            print(f"\n{lang}:")
            print(code)
    
    print("\n\n🎉 KEY TAKEAWAY:")
    print("="*60)
    print("SpiffWorkflow transformed BPMN from a diagram to a running application!")
    print("The engine orchestrated everything - agents just executed when called.")
    print("\n🚀 This is the power of BPMN-first architecture with SpiffWorkflow!")


if __name__ == "__main__":
    asyncio.run(main())