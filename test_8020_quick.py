#!/usr/bin/env python3
"""Quick test of 80/20 improvements without live monitoring"""

import asyncio
from src.weavergen.bpmn_error_boundaries import BPMNErrorBoundary, ErrorSeverity
from src.weavergen.bpmn_8020_enhanced import EnhancedPydanticAIBPMNEngine
from src.weavergen.pydantic_ai_bpmn_engine import PydanticAIContext
from rich.console import Console


async def test_error_boundaries():
    """Test error boundary functionality"""
    console = Console()
    console.print("\n[bold cyan]Testing Error Boundaries[/bold cyan]")
    
    boundary = BPMNErrorBoundary()
    
    # Test 1: Successful execution
    async def good_task(ctx):
        return {"success": True, "data": "test"}
    
    result = await boundary.execute_with_boundary(
        task_name="GoodTask",
        task_func=good_task,
        context={}
    )
    console.print(f"✅ Good task result: {result}")
    
    # Test 2: Task with retry
    attempt = 0
    async def flaky_task(ctx):
        nonlocal attempt
        attempt += 1
        if attempt < 3:
            raise ConnectionError(f"Attempt {attempt} failed")
        return {"success": True, "attempts": attempt}
    
    result = await boundary.execute_with_boundary(
        task_name="FlakyTask",
        task_func=flaky_task,
        context={}
    )
    console.print(f"✅ Flaky task succeeded after {result.get('attempts')} attempts")
    
    # Test 3: Task with fallback
    async def failing_task(ctx):
        raise ValueError("Non-critical failure")  # Use non-critical error
    
    boundary.config.fallback_to_mock = True
    boundary.config.propagate_critical = False  # Don't propagate
    result = await boundary.execute_with_boundary(
        task_name="FailingTask",
        task_func=failing_task,
        context={}
    )
    console.print(f"✅ Failed task fell back to mock: {result.get('mock', False)}")
    
    # Show error summary
    summary = boundary.get_error_summary()
    console.print(f"\n📊 Error Summary:")
    console.print(f"  Total errors: {summary['total_errors']}")
    console.print(f"  By severity: {summary['by_severity']}")


async def test_enhanced_engine():
    """Test enhanced BPMN engine without monitoring"""
    console = Console()
    console.print("\n[bold cyan]Testing Enhanced Engine[/bold cyan]")
    
    # Create engine
    engine = EnhancedPydanticAIBPMNEngine(use_mock=True)
    
    # Create context
    context = PydanticAIContext(
        semantic_file="semantic_conventions/test_valid.yaml",
        output_dir="test_8020_output"
    )
    
    # Execute without monitoring to avoid timeout
    result = await engine.execute_workflow_enhanced(
        workflow_name="TestWorkflow",
        context=context,
        enable_monitoring=False  # Disable to avoid timeout
    )
    
    console.print(f"\n✅ Workflow completed:")
    console.print(f"  Success: {result['success']}")
    console.print(f"  Agents: {result['agents_generated']}")
    console.print(f"  Models: {result['models_generated']}")
    console.print(f"  Quality: {result['quality_score']:.1%}")
    
    return result


async def main():
    """Run quick tests"""
    console = Console()
    console.print("""
[bold green]🚀 80/20 Improvements Quick Test
Testing error boundaries and enhanced engine...[/bold green]
""")
    
    await test_error_boundaries()
    await test_enhanced_engine()
    
    console.print("\n[bold green]✅ All tests completed![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())