#!/usr/bin/env python3
"""
Demonstrate SpiffWorkflow as the BPMN Engine using existing integration.

Shows that SpiffWorkflow IS the point - it controls everything.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weavergen.workflows.engine import WorkflowEngine
from weavergen.workflows.agents import AgentWorkflowService
from weavergen.layers.contracts import (
    GenerationRequest, ExecutionContext, TargetLanguage, SemanticConvention
)


async def demonstrate_spiff_engine():
    """
    Demonstrate that SpiffWorkflow is the engine that controls everything.
    """
    
    print("\n🎯 SPIFFWORKFLOW AS THE BPMN ENGINE")
    print("="*60)
    print("SpiffWorkflow interprets BPMN and orchestrates execution")
    print("Agents are just service tasks that SpiffWorkflow calls")
    
    # 1. Create the workflow engine (SpiffWorkflow wrapper)
    print("\n1. CREATING WORKFLOW ENGINE")
    print("-"*40)
    engine = WorkflowEngine()
    print("✅ WorkflowEngine created (wraps SpiffWorkflow)")
    
    # 2. Show available workflows
    print("\n2. AVAILABLE BPMN WORKFLOWS")
    print("-"*40)
    workflows = engine.get_available_workflows()
    for name, info in workflows.items():
        print(f"📋 {name}:")
        print(f"   - Tasks: {info.get('task_count', 0)}")
        print(f"   - Service tasks: {info.get('service_task_count', 0)}")
        print(f"   - Gateways: {info.get('gateway_count', 0)}")
    
    # 3. Show how agents are registered as service tasks
    print("\n3. AGENTS AS SERVICE TASKS")
    print("-"*40)
    agent_service = engine.agent_service
    available_tasks = agent_service.get_available_tasks()
    print(f"Registered service tasks: {len(available_tasks)}")
    for i, task in enumerate(available_tasks[:5], 1):
        print(f"   {i}. {task}")
    
    # 4. Create a test request
    print("\n4. EXECUTING BPMN WORKFLOW")
    print("-"*40)
    
    semantic_convention = SemanticConvention(
        id="http.server",
        brief="HTTP server semantic conventions"
    )
    
    request = GenerationRequest(
        semantic_convention=semantic_convention,
        target_languages=[TargetLanguage.PYTHON],
        output_directory=Path("./demo_output")
    )
    
    context = ExecutionContext(
        working_directory=Path.cwd(),
        debug_mode=True,
        parallel_execution=False
    )
    
    print("📄 Input:")
    print(f"   - Semantic convention: {semantic_convention.id}")
    print(f"   - Target languages: {[lang.value for lang in request.target_languages]}")
    
    print("\n🚀 SpiffWorkflow executing BPMN process...")
    print("   (Using mock workflow since no BPMN file loaded)")
    
    # Execute with timeout
    try:
        workflow_context = await asyncio.wait_for(
            engine.execute_generation_workflow(request, context),
            timeout=10  # Short timeout for demo
        )
        
        print("\n✅ Workflow completed!")
        print(f"   - Instance ID: {workflow_context.instance_id}")
        print(f"   - Tasks executed: {len(workflow_context.task_results)}")
        print(f"   - Total time: {workflow_context.total_execution_time:.2f}s")
        
        # Show task execution order
        print("\n📊 TASK EXECUTION (controlled by SpiffWorkflow):")
        for task_name, result in workflow_context.task_results.items():
            status = "✅" if result["status"] == "success" else "❌"
            print(f"   {status} {task_name}")
            
    except asyncio.TimeoutError:
        print("\n⏱️ Execution timed out (expected for demo)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # 5. Explain the architecture
    print("\n\n🏗️ SPIFFWORKFLOW ARCHITECTURE")
    print("="*60)
    
    print("\n1. BPMN PROCESS DEFINITION:")
    print("   ```xml")
    print("   <serviceTask id='validate' name='Validate Input'>")
    print("     <extensionElements>")
    print("       <weaver:agent>validator</weaver:agent>")
    print("     </extensionElements>")
    print("   </serviceTask>")
    print("   ```")
    
    print("\n2. SPIFFWORKFLOW EXECUTES:")
    print("   - Parses BPMN XML")
    print("   - Creates workflow instance")
    print("   - Manages task states")
    print("   - Evaluates gateway conditions")
    print("   - Calls service tasks (agents)")
    
    print("\n3. AGENTS ARE JUST FUNCTIONS:")
    print("   ```python")
    print("   async def validate_task(context):")
    print("       # Agent doesn't know about workflow")
    print("       # Just processes input and returns output")
    print("       return validation_result")
    print("   ```")
    
    print("\n4. KEY INSIGHTS:")
    print("   🎯 SpiffWorkflow IS the application engine")
    print("   🎯 BPMN is executable, not just documentation")
    print("   🎯 Agents don't orchestrate - SpiffWorkflow does")
    print("   🎯 Flow changes = BPMN changes, not code changes")
    
    print("\n5. BENEFITS OF SPIFFWORKFLOW:")
    print("   • Industry-standard BPMN 2.0 support")
    print("   • Visual process design and debugging")
    print("   • Built-in state management")
    print("   • Parallel execution support")
    print("   • Event handling and timers")
    print("   • Process versioning")
    
    print("\n6. THE PARADIGM SHIFT:")
    print("   Traditional: Code → Calls functions → Returns result")
    print("   SpiffWorkflow: BPMN → SpiffWorkflow → Calls agents → Manages flow")
    print("\n   🚀 Your application logic lives in BPMN, not code!")


async def show_spiff_internals():
    """Show SpiffWorkflow internals."""
    
    print("\n\n🔍 SPIFFWORKFLOW INTERNALS")
    print("="*60)
    
    try:
        from SpiffWorkflow import TaskState
        from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
        
        print("\n✅ SpiffWorkflow is installed!")
        print("\nKey SpiffWorkflow concepts:")
        
        print("\n1. TASK STATES:")
        for state in TaskState:
            print(f"   - {state.name}: {state.value}")
        
        print("\n2. WORKFLOW LIFECYCLE:")
        print("   1. Parse BPMN → Create workflow spec")
        print("   2. Create workflow instance from spec")
        print("   3. Get ready tasks")
        print("   4. Execute tasks (call agents)")
        print("   5. Complete tasks")
        print("   6. Repeat until workflow complete")
        
        print("\n3. HOW IT CONTROLS AGENTS:")
        print("   ```python")
        print("   # SpiffWorkflow finds ready service tasks")
        print("   ready_tasks = workflow.get_ready_user_tasks()")
        print("   ")
        print("   # For each service task, call the agent")
        print("   for task in ready_tasks:")
        print("       agent = get_agent(task.task_spec.name)")
        print("       result = await agent.execute(task.data)")
        print("       task.complete(result)")
        print("   ```")
        
    except ImportError:
        print("\n⚠️  SpiffWorkflow not installed")
        print("   Install with: pip install SpiffWorkflow")
        print("\n   But the concept remains the same:")
        print("   The BPMN engine controls everything!")


async def main():
    """Run the demonstration."""
    
    print("\n" + "="*60)
    print("SPIFFWORKFLOW: THE BPMN ENGINE THAT CONTROLS EVERYTHING")
    print("="*60)
    
    # Main demonstration
    await demonstrate_spiff_engine()
    
    # Show internals
    await show_spiff_internals()
    
    print("\n\n🎯 CONCLUSION")
    print("="*60)
    print("SpiffWorkflow transforms BPMN from documentation to APPLICATION")
    print("The engine orchestrates everything - agents just execute tasks")
    print("This is the future of visual, process-driven development!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())