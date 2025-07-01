"""
BPMN 80/20 Enhanced Integration

Integrates error boundaries and live monitoring into the Pydantic AI BPMN engine
with minimal complexity. Demonstrates the power of focused improvements.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console

from .pydantic_ai_bpmn_engine import PydanticAIBPMNEngine, PydanticAIContext
from .bpmn_error_boundaries import BPMNErrorBoundary, ErrorBoundaryConfig, with_error_boundary, BPMNCompensationFlow
from .bpmn_live_monitor import BPMNLiveMonitor, BPMNMonitorContext


class EnhancedPydanticAIBPMNEngine(PydanticAIBPMNEngine):
    """
    Enhanced BPMN engine with 80/20 improvements:
    - Error boundaries for robust execution
    - Live monitoring for real-time visibility
    - Compensation flows for rollback
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", use_mock: bool = True):
        super().__init__(model_name, use_mock)
        
        # Initialize enhancements
        self.error_boundary = BPMNErrorBoundary()
        self.compensation_flow = BPMNCompensationFlow()
        self.monitor: Optional[BPMNLiveMonitor] = None
        
        # Register compensation handlers
        self._register_compensations()
        
    def _register_compensations(self):
        """Register compensation handlers for tasks"""
        
        # Define compensation for each critical task
        compensations = {
            "Task_GenerateModels": self._compensate_models,
            "Task_GenerateAgents": self._compensate_agents,
            "Task_GenerateOutput": self._compensate_output
        }
        
        for task, handler in compensations.items():
            self.error_boundary.register_compensation(task, handler)
            self.compensation_flow.register(task, handler)
            
    async def _compensate_models(self, context: Dict[str, Any], error: Any):
        """Compensate for model generation failure"""
        return {
            "action": "cleanup_models",
            "removed": len(context.get("generated_models", [])),
            "reason": str(error)
        }
        
    async def _compensate_agents(self, context: Dict[str, Any], error: Any):
        """Compensate for agent generation failure"""
        return {
            "action": "cleanup_agents", 
            "removed": len(context.get("generated_agents", [])),
            "reason": str(error)
        }
        
    async def _compensate_output(self, context: Dict[str, Any], error: Any):
        """Compensate for output generation failure"""
        output_dir = Path(context.get("output_dir", ""))
        if output_dir.exists():
            # In real implementation, would clean up files
            return {
                "action": "cleanup_output",
                "directory": str(output_dir),
                "reason": str(error)
            }
        return {"action": "none_needed"}
        
    async def execute_workflow_enhanced(
        self, 
        workflow_name: str, 
        context: PydanticAIContext,
        enable_monitoring: bool = True
    ) -> Dict[str, Any]:
        """
        Execute workflow with 80/20 enhancements.
        
        Features:
        - Live monitoring visualization
        - Error boundaries with retry
        - Compensation on failure
        """
        
        # Setup live monitoring if enabled
        if enable_monitoring:
            self.monitor = BPMNLiveMonitor(workflow_name)
            
            # Register all tasks for monitoring
            for task_name in self.service_tasks.keys():
                self.monitor.register_task(task_name.lower(), task_name)
                
            # Start monitor in background
            monitor_task = asyncio.create_task(self.monitor.start_live_monitor())
        
        try:
            # Execute with enhanced error handling
            result = await self._execute_with_boundaries(workflow_name, context)
            
            # Mark workflow complete
            if self.monitor:
                self.monitor.stop()
                
            return result
            
        except Exception as e:
            # Execute compensation flow on failure
            self.console.print(f"[red]Workflow failed: {e}[/red]")
            
            compensation_results = await self.compensation_flow.compensate_all(
                context.model_dump(), 
                error=e
            )
            
            return {
                "success": False,
                "error": str(e),
                "compensations": compensation_results,
                "partial_results": {
                    "models_generated": len(context.generated_models),
                    "agents_generated": len(context.generated_agents)
                }
            }
            
        finally:
            if enable_monitoring and 'monitor_task' in locals():
                await monitor_task
                
    async def _execute_with_boundaries(
        self, 
        workflow_name: str, 
        context: PydanticAIContext
    ) -> Dict[str, Any]:
        """Execute workflow with error boundaries"""
        
        # Define task execution order (simplified from BPMN)
        task_sequence = [
            "Task_LoadSemantics",
            "Task_ValidateInput",
            "Task_GenerateModels",
            "Task_GenerateAgents",
            "Task_GenerateValidators",
            "Task_ValidateModels",
            "Task_TestAgents",
            "Task_TestValidators",
            "Task_Integration",
            "Task_GenerateOutput",
            "Task_CaptureSpans"
        ]
        
        context.execution_trace = []
        
        for task_name in task_sequence:
            if task_name in self.service_tasks:
                # Execute with monitoring context
                if self.monitor:
                    async with BPMNMonitorContext(self.monitor, task_name.lower()):
                        # Execute with error boundary
                        result = await self.error_boundary.execute_with_boundary(
                            task_name=task_name,
                            task_func=lambda ctx: self.service_tasks[task_name](context),
                            context=context.model_dump()
                        )
                        
                        # Mark task complete in compensation flow
                        self.compensation_flow.mark_completed(task_name)
                        
                        # Update monitor with result
                        if self.monitor:
                            self.monitor.tasks[task_name.lower()].result = result
                else:
                    # Execute without monitoring
                    result = await self.error_boundary.execute_with_boundary(
                        task_name=task_name,
                        task_func=lambda ctx: self.service_tasks[task_name](context),
                        context=context.model_dump()
                    )
                    
                context.execution_trace.append(f"Enhanced: {task_name}")
                
        # Calculate final results
        quality_score = self._calculate_quality_score(context)
        
        return {
            "success": True,
            "spans": context.spans,
            "agents_generated": len(context.generated_agents),
            "models_generated": len(context.generated_models),
            "validation_passed": quality_score >= context.quality_threshold,
            "quality_score": quality_score,
            "execution_trace": context.execution_trace,
            "error_summary": self.error_boundary.get_error_summary()
        }


async def run_enhanced_pydantic_ai_workflow(
    semantic_file: str,
    output_dir: str,
    enable_monitoring: bool = True,
    use_mock: bool = True
) -> Dict[str, Any]:
    """
    Run Pydantic AI workflow with 80/20 enhancements.
    
    Features:
    - Live terminal monitoring
    - Automatic error recovery
    - Compensation on failure
    """
    
    console = Console()
    
    # Show startup banner
    console.print("""
[bold blue]╔═══════════════════════════════════════════╗
║     🚀 Enhanced BPMN + Pydantic AI        ║  
║        with 80/20 Improvements            ║
╚═══════════════════════════════════════════╝[/bold blue]
""")
    
    # Initialize enhanced engine
    engine = EnhancedPydanticAIBPMNEngine(use_mock=use_mock)
    
    # Create context
    context = PydanticAIContext(
        semantic_file=semantic_file,
        output_dir=output_dir,
        agent_roles=["analyst", "coordinator", "validator", "facilitator"]
    )
    
    # Execute with enhancements
    result = await engine.execute_workflow_enhanced(
        workflow_name="EnhancedPydanticAIGeneration",
        context=context,
        enable_monitoring=enable_monitoring
    )
    
    # Display results
    if result["success"]:
        console.print("\n[bold green]✅ Workflow completed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Workflow failed but compensations executed[/bold red]")
        
    # Show error summary if any
    error_summary = result.get("error_summary", {})
    if error_summary.get("total_errors", 0) > 0:
        console.print(f"\n[yellow]⚠️  Errors encountered: {error_summary['total_errors']}[/yellow]")
        for severity, count in error_summary.get("by_severity", {}).items():
            console.print(f"  - {severity}: {count}")
            
    return result


# Example usage
if __name__ == "__main__":
    # Run the enhanced workflow
    asyncio.run(run_enhanced_pydantic_ai_workflow(
        semantic_file="semantic_conventions/test.yaml",
        output_dir="enhanced_output",
        enable_monitoring=True,
        use_mock=True
    ))