#!/usr/bin/env python3
"""Quick test of SpiffWorkflow integration."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_spiff_components():
    """Test SpiffWorkflow components individually."""
    
    print("🔧 Testing SpiffWorkflow Integration Components")
    print("=" * 50)
    
    # Test 1: SpiffWorkflow availability
    print("\n1. Testing SpiffWorkflow availability...")
    try:
        import SpiffWorkflow
        print("✅ SpiffWorkflow imported successfully")
    except ImportError as e:
        print(f"❌ SpiffWorkflow import failed: {e}")
        return
    
    # Test 2: BPMN loader
    print("\n2. Testing BPMN workflow loader...")
    try:
        from weavergen.workflows.bpmn import BPMNWorkflowLoader
        loader = BPMNWorkflowLoader()
        workflows = loader.load_workflows()
        summary = loader.get_workflow_summary()
        print(f"✅ Loaded {summary['total_workflows']} workflows")
        
        for name, info in summary["workflows"].items():
            print(f"   📋 {name}: {info['service_tasks']} tasks")
            
    except Exception as e:
        print(f"❌ BPMN loader failed: {e}")
    
    # Test 3: Agent service
    print("\n3. Testing agent workflow service...")
    try:
        from weavergen.workflows.agents import AgentWorkflowService
        agent_service = AgentWorkflowService()
        available_tasks = agent_service.get_available_tasks()
        print(f"✅ Agent service initialized with {len(available_tasks)} tasks")
        
        for task in available_tasks[:3]:  # Show first 3 tasks
            print(f"   🤖 {task}")
            
    except Exception as e:
        print(f"❌ Agent service failed: {e}")
    
    # Test 4: Workflow engine
    print("\n4. Testing workflow engine...")
    try:
        from weavergen.workflows.engine import WorkflowEngine
        from weavergen.layers.contracts import (
            GenerationRequest, ExecutionContext, TargetLanguage, SemanticConvention
        )
        
        engine = WorkflowEngine()
        
        # Create test request
        semantic_convention = SemanticConvention(
            id="test.spiff",
            brief="Test semantic convention for SpiffWorkflow"
        )
        
        request = GenerationRequest(
            semantic_convention=semantic_convention,
            target_languages=[TargetLanguage.PYTHON],
            output_directory=Path("./test_output")
        )
        
        execution_context = ExecutionContext(
            working_directory=Path.cwd(),
            debug_mode=True,
            parallel_execution=False
        )
        
        print("✅ Workflow engine initialized")
        print(f"   📋 Test request: {semantic_convention.id}")
        print(f"   🎯 Target: {request.target_languages[0].value}")
        
    except Exception as e:
        print(f"❌ Workflow engine failed: {e}")
    
    # Test 5: OpenTelemetry integration
    print("\n5. Testing OpenTelemetry span management...")
    try:
        from weavergen.workflows.otel import WorkflowSpanManager
        span_manager = WorkflowSpanManager()
        print("✅ Span manager initialized")
        print(f"   📊 Active workflows: {len(span_manager.get_active_workflows())}")
        
    except Exception as e:
        print(f"❌ Span manager failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 SpiffWorkflow component testing complete!")


async def test_simple_workflow():
    """Test a simple workflow execution."""
    
    print("\n🔄 Testing Simple Workflow Execution")
    print("=" * 50)
    
    try:
        from weavergen.workflows.engine import WorkflowEngine
        from weavergen.workflows.agents import AgentWorkflowService
        from weavergen.workflows.otel import get_span_manager
        from weavergen.layers.contracts import (
            GenerationRequest, ExecutionContext, TargetLanguage, SemanticConvention
        )
        from weavergen.agents.multi_agent_ollama import WeaverGenAgentContext
        from uuid import uuid4
        
        # Initialize components
        engine = WorkflowEngine()
        agent_service = AgentWorkflowService()
        span_manager = get_span_manager()
        
        # Create simple test request
        semantic_convention = SemanticConvention(
            id="simple.test",
            brief="Simple test for workflow execution"
        )
        
        request = GenerationRequest(
            semantic_convention=semantic_convention,
            target_languages=[TargetLanguage.PYTHON],
            output_directory=Path("./simple_test_output")
        )
        
        execution_context = ExecutionContext(
            working_directory=Path.cwd(),
            debug_mode=True,
            parallel_execution=False
        )
        
        print("📋 Executing simple workflow...")
        
        # Execute workflow with timeout
        workflow_context = await asyncio.wait_for(
            engine.execute_generation_workflow(request, execution_context),
            timeout=60  # 1 minute timeout
        )
        
        print("✅ Workflow completed successfully!")
        print(f"   ⏱️ Execution time: {workflow_context.total_execution_time:.2f}s")
        print(f"   📊 Task results: {len(workflow_context.task_results)}")
        print(f"   ❌ Errors: {len(workflow_context.errors)}")
        
        # Show task results
        for task_name, result in workflow_context.task_results.items():
            status = "✅" if result["status"] == "success" else "❌"
            time_ms = result.get("execution_time_ms", 0)
            print(f"   {status} {task_name}: {time_ms:.0f}ms")
        
    except asyncio.TimeoutError:
        print("❌ Workflow timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")


async def main():
    """Run all tests."""
    
    print("🎯 WeaverGen SpiffWorkflow Integration Tests")
    print("=" * 60)
    
    try:
        # Test components
        await test_spiff_components()
        
        # Test simple workflow
        await test_simple_workflow()
        
        print("\n🎉 All tests completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())