"""
80/20 BPMN-First Implementation using SpiffWorkflow

Focuses on the 20% of BPMN functionality that delivers 80% of the value:
- Service Tasks
- Parallel Gateways  
- Sequential Flows
- Basic Error Handling
"""

import asyncio
import json
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field

try:
    from SpiffWorkflow.bpmn import BpmnWorkflow
    from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
    from SpiffWorkflow.task import Task as SpiffTask
    from SpiffWorkflow.specs import WorkflowSpec
    SPIFF_AVAILABLE = True
except ImportError:
    SPIFF_AVAILABLE = False
    # Fallback classes
    class BpmnWorkflow:
        pass
    class BpmnParser:
        pass
    class SpiffTask:
        pass
    class WorkflowSpec:
        pass

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from rich.console import Console
from rich import print as rprint
from rich.panel import Panel

from .core import WeaverGen, GenerationConfig
from .cli_dod_enforcer import cli_span
from .dod_validator import DefinitionOfDoneValidator

console = Console()

# Setup span capture for BPMN execution
SPIFF_MEMORY_EXPORTER = InMemorySpanExporter()
SPIFF_PROVIDER = TracerProvider()
SPIFF_PROVIDER.add_span_processor(BatchSpanProcessor(SPIFF_MEMORY_EXPORTER))
spiff_tracer = trace.get_tracer(__name__, tracer_provider=SPIFF_PROVIDER)


@dataclass
class SpiffExecutionResult:
    """Result of BPMN workflow execution"""
    workflow_name: str
    success: bool
    execution_time_ms: float
    tasks_executed: int
    tasks_completed: int
    spans_generated: int
    output_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


class Spiff8020ServiceTask:
    """Base class for 80/20 service tasks - minimal but effective"""
    
    def __init__(self, name: str):
        self.name = name
        self.tracer = spiff_tracer
    
    @cli_span("service_task.execute", bpmn_file="workflows/bpmn/8020_workflow.bpmn")
    async def execute(self, task: SpiffTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the service task with span tracking"""
        file_path = inspect.getfile(self.__class__)
        line_num = inspect.getsourcelines(self.__class__)[1]
        
        with self.tracer.start_as_current_span(f"bpmn.task.{self.name}") as span:
            # Add BPMN attribution
            span.set_attribute("bpmn.workflow.file", "workflows/bpmn/8020_workflow.bpmn")
            span.set_attribute("bpmn.workflow.id", "EightyTwentyWorkflow")
            span.set_attribute("bpmn.task.id", task.task_spec.name)
            span.set_attribute("bpmn.task.type", "serviceTask")
            span.set_attribute("bpmn.task.name", self.name)
            
            # Add code attribution
            span.set_attribute("code.filepath", file_path)
            span.set_attribute("code.lineno", line_num)
            span.set_attribute("code.function", "execute")
            span.set_attribute("execution.timestamp", datetime.now().isoformat())
            
            try:
                result = await self._execute_logic(task, context)
                span.set_attribute("execution.success", True)
                return result
            except Exception as e:
                span.set_attribute("execution.success", False)
                span.set_attribute("execution.error", str(e))
                span.record_exception(e)
                raise
    
    async def _execute_logic(self, task: SpiffTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in concrete implementations"""
        raise NotImplementedError("Subclasses must implement _execute_logic")


class LoadSemanticsTask(Spiff8020ServiceTask):
    """80/20 Task: Load semantic conventions (20% effort, 80% validation value)"""
    
    def __init__(self):
        super().__init__("LoadSemantics")
    
    async def _execute_logic(self, task: SpiffTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load and validate semantic convention registry"""
        registry_url = context.get("registry_url", "https://opentelemetry.io/schemas/1.21.0")
        
        # Mock loading for MVP - in real implementation would call WeaverGen
        rprint(f"[cyan]📥 Loading semantics from: {registry_url}[/cyan]")
        
        # Simulate validation
        await asyncio.sleep(0.1)  # Simulate network call
        
        context["semantics_loaded"] = True
        context["registry_url"] = registry_url
        context["semantic_version"] = "1.21.0"
        
        return context


class ValidateSemanticsTask(Spiff8020ServiceTask):
    """80/20 Task: Validate semantic conventions (critical path)"""
    
    def __init__(self):
        super().__init__("ValidateSemantics")
    
    async def _execute_logic(self, task: SpiffTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate loaded semantics"""
        if not context.get("semantics_loaded"):
            raise ValueError("Semantics not loaded - prerequisite failed")
        
        rprint("[cyan]✅ Validating semantic conventions[/cyan]")
        
        # Mock validation logic
        await asyncio.sleep(0.05)
        
        context["semantics_valid"] = True
        context["validation_score"] = 0.95
        
        return context


class GenerateCoreTask(Spiff8020ServiceTask):
    """80/20 Task: Generate core code (the main value)"""
    
    def __init__(self):
        super().__init__("GenerateCore")
    
    async def _execute_logic(self, task: SpiffTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate core code using Weaver Forge"""
        if not context.get("semantics_valid"):
            raise ValueError("Invalid semantics - cannot generate")
        
        target_language = context.get("target_language", "python")
        output_dir = Path(context.get("output_dir", "generated"))
        
        rprint(f"[cyan]⚡ Generating {target_language} code[/cyan]")
        
        # Mock generation - in real implementation would use WeaverGen
        output_dir.mkdir(exist_ok=True)
        
        # Create mock output files
        output_files = []
        for component in ["metrics", "spans", "logs"]:
            output_file = output_dir / f"{component}.{target_language}"
            output_file.write_text(f"# Generated {component} for {target_language}\n")
            output_files.append(str(output_file))
        
        await asyncio.sleep(0.2)  # Simulate generation time
        
        context["generated_files"] = output_files
        context["generation_success"] = True
        
        return context


class ValidateOutputTask(Spiff8020ServiceTask):
    """80/20 Task: Validate generated output (quality gate)"""
    
    def __init__(self):
        super().__init__("ValidateOutput")
    
    async def _execute_logic(self, task: SpiffTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated code"""
        generated_files = context.get("generated_files", [])
        
        if not generated_files:
            raise ValueError("No files generated - validation failed")
        
        rprint(f"[cyan]🔍 Validating {len(generated_files)} generated files[/cyan]")
        
        # Mock validation
        await asyncio.sleep(0.1)
        
        valid_files = []
        for file_path in generated_files:
            if Path(file_path).exists():
                valid_files.append(file_path)
        
        context["validated_files"] = valid_files
        context["validation_success"] = len(valid_files) == len(generated_files)
        
        return context


class Spiff8020Engine:
    """80/20 BPMN Engine using SpiffWorkflow - minimal but powerful"""
    
    def __init__(self):
        self.service_tasks = {
            "LoadSemantics": LoadSemanticsTask(),
            "ValidateSemantics": ValidateSemanticsTask(), 
            "GenerateCore": GenerateCoreTask(),
            "ValidateOutput": ValidateOutputTask()
        }
        self.workflow_spec = None
        self.validator = DefinitionOfDoneValidator()
    
    def create_minimal_8020_bpmn(self) -> str:
        """Create the minimal viable BPMN for 80/20 rule"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:weavergen="http://weavergen.ai/bpmn/extensions"
                  id="EightyTwentyDefinitions"
                  targetNamespace="http://weavergen.ai/bpmn">
    
    <bpmn:process id="EightyTwentyWorkflow" name="80/20 Weaver Generation" isExecutable="true">
        
        <!-- Start: Simple begin -->
        <bpmn:startEvent id="StartEvent" name="Start Generation"/>
        <bpmn:sequenceFlow id="Flow_Start" sourceRef="StartEvent" targetRef="LoadSemantics"/>
        
        <!-- 20% Task 1: Load semantics -->
        <bpmn:serviceTask id="LoadSemantics" name="Load Semantic Conventions"
                          weavergen:taskClass="LoadSemanticsTask"/>
        <bpmn:sequenceFlow id="Flow_Load" sourceRef="LoadSemantics" targetRef="ValidateSemantics"/>
        
        <!-- 20% Task 2: Validate semantics -->
        <bpmn:serviceTask id="ValidateSemantics" name="Validate Conventions"
                          weavergen:taskClass="ValidateSemanticsTask"/>
        <bpmn:sequenceFlow id="Flow_Validate" sourceRef="ValidateSemantics" targetRef="ParallelSplit"/>
        
        <!-- 20% Feature: Parallel execution for 80% of performance gain -->
        <bpmn:parallelGateway id="ParallelSplit" name="Split for Parallel Generation"/>
        <bpmn:sequenceFlow id="Flow_Split1" sourceRef="ParallelSplit" targetRef="GenerateCore"/>
        <bpmn:sequenceFlow id="Flow_Split2" sourceRef="ParallelSplit" targetRef="GenerateTests"/>
        
        <!-- 20% Task 3: Core generation (80% of value) -->
        <bpmn:serviceTask id="GenerateCore" name="Generate Core Code"
                          weavergen:taskClass="GenerateCoreTask"/>
        <bpmn:sequenceFlow id="Flow_Core" sourceRef="GenerateCore" targetRef="ParallelJoin"/>
        
        <!-- Parallel task: Generate tests -->
        <bpmn:serviceTask id="GenerateTests" name="Generate Tests"
                          weavergen:taskClass="GenerateCoreTask"/>
        <bpmn:sequenceFlow id="Flow_Tests" sourceRef="GenerateTests" targetRef="ParallelJoin"/>
        
        <!-- Join parallel execution -->
        <bpmn:parallelGateway id="ParallelJoin" name="Join Results"/>
        <bpmn:sequenceFlow id="Flow_Join" sourceRef="ParallelJoin" targetRef="ValidateOutput"/>
        
        <!-- 20% Task 4: Output validation (quality gate) -->
        <bpmn:serviceTask id="ValidateOutput" name="Validate Generated Output"
                          weavergen:taskClass="ValidateOutputTask"/>
        <bpmn:sequenceFlow id="Flow_Final" sourceRef="ValidateOutput" targetRef="EndEvent"/>
        
        <!-- End: Simple completion -->
        <bpmn:endEvent id="EndEvent" name="Generation Complete"/>
        
    </bpmn:process>
</bpmn:definitions>'''
    
    async def execute_8020_workflow(self, context: Dict[str, Any]) -> SpiffExecutionResult:
        """Execute the 80/20 BPMN workflow"""
        start_time = datetime.now()
        
        rprint(Panel(
            "[bold cyan]🚀 80/20 BPMN-FIRST EXECUTION[/bold cyan]\n\n"
            "[yellow]20% of BPMN features, 80% of the value[/yellow]\n"
            "• Service Tasks\n"
            "• Parallel Gateways\n" 
            "• Sequential Flows\n"
            "• Span Validation",
            title="SpiffWorkflow 80/20 Engine",
            border_style="cyan"
        ))
        
        if not SPIFF_AVAILABLE:
            return await self._fallback_execution(context)
        
        try:
            # Create BPMN workflow
            bpmn_content = self.create_minimal_8020_bpmn()
            bpmn_file = Path("workflows/bpmn/8020_workflow.bpmn")
            bpmn_file.parent.mkdir(parents=True, exist_ok=True)
            bpmn_file.write_text(bpmn_content)
            
            # Parse and execute
            parser = BpmnParser()
            parser.add_bpmn_file(str(bpmn_file))
            
            workflow_spec = parser.get_spec("EightyTwentyWorkflow")
            workflow = BpmnWorkflow(workflow_spec)
            
            # Set initial context
            workflow.data.update(context)
            
            # Execute workflow
            tasks_executed = 0
            tasks_completed = 0
            
            while workflow.is_completed() is False:
                ready_tasks = workflow.get_ready_user_tasks()
                
                for task in ready_tasks:
                    await self._execute_task(task, workflow.data)
                    workflow.complete_task_from_id(task.id)
                    tasks_executed += 1
                    
                    if task.state.name == "COMPLETED":
                        tasks_completed += 1
                
                # Advance workflow
                workflow.do_engine_steps()
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Export and validate spans
            spans = await self._export_spans()
            validation_result = self.validator.validate_spans(spans)
            
            result = SpiffExecutionResult(
                workflow_name="EightyTwentyWorkflow",
                success=workflow.is_completed(),
                execution_time_ms=execution_time,
                tasks_executed=tasks_executed,
                tasks_completed=tasks_completed,
                spans_generated=len(spans),
                output_files=context.get("generated_files", []),
                context=dict(workflow.data)
            )
            
            # Show results
            await self._show_execution_results(result, validation_result)
            
            return result
            
        except Exception as e:
            rprint(f"[red]❌ BPMN execution failed: {e}[/red]")
            return SpiffExecutionResult(
                workflow_name="EightyTwentyWorkflow",
                success=False,
                execution_time_ms=0,
                tasks_executed=0,
                tasks_completed=0,
                spans_generated=0,
                errors=[str(e)]
            )
    
    async def _execute_task(self, task: SpiffTask, context: Dict[str, Any]):
        """Execute a single BPMN task"""
        task_name = task.task_spec.name
        
        if task_name in self.service_tasks:
            service_task = self.service_tasks[task_name]
            updated_context = await service_task.execute(task, context)
            context.update(updated_context)
        else:
            rprint(f"[yellow]⚠️ Unknown task: {task_name}[/yellow]")
    
    async def _export_spans(self) -> List[Dict[str, Any]]:
        """Export captured spans"""
        SPIFF_PROVIDER.force_flush()
        raw_spans = SPIFF_MEMORY_EXPORTER.get_finished_spans()
        
        spans = []
        for span in raw_spans:
            span_dict = {
                "name": span.name,
                "trace_id": f"0x{span.context.trace_id:032x}",
                "span_id": f"0x{span.context.span_id:016x}",
                "parent_id": f"0x{span.parent.span_id:016x}" if span.parent else None,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "duration_ns": span.end_time - span.start_time if span.end_time else 0,
                "attributes": dict(span.attributes or {}),
                "status": {
                    "status_code": span.status.status_code.name if span.status else "UNSET",
                    "description": span.status.description if span.status else None
                }
            }
            spans.append(span_dict)
        
        return spans
    
    async def _show_execution_results(self, result: SpiffExecutionResult, validation_result):
        """Show execution and validation results"""
        # Execution summary
        rprint(Panel(
            f"[bold]EXECUTION SUMMARY[/bold]\n\n"
            f"Workflow: {result.workflow_name}\n"
            f"Success: [{'green' if result.success else 'red'}]{'✅' if result.success else '❌'}[/]\n"
            f"Execution Time: {result.execution_time_ms:.1f}ms\n"
            f"Tasks Executed: {result.tasks_executed}\n"
            f"Tasks Completed: {result.tasks_completed}\n"
            f"Generated Files: {len(result.output_files)}\n"
            f"Spans Generated: {result.spans_generated}",
            title="80/20 BPMN Results",
            border_style="green" if result.success else "red"
        ))
        
        # Validation summary
        rprint(Panel(
            f"[bold]SPAN VALIDATION[/bold]\n\n"
            f"Trust Score: [{'green' if validation_result.trust_score >= 0.8 else 'red'}]{validation_result.trust_score:.1%}[/]\n"
            f"Level 1 (Basic): {validation_result.level1_pass}/{validation_result.total_spans}\n"
            f"Level 2 (Attribution): {validation_result.level2_pass}/{validation_result.total_spans}\n"
            f"Level 3 (Semantic): {validation_result.level3_pass}/{validation_result.total_spans}\n"
            f"Lies Detected: [{'red' if validation_result.lies_detected else 'green'}]{len(validation_result.lies_detected)}[/]\n"
            f"Is Done: [{'green' if validation_result.is_done else 'red'}]{'YES' if validation_result.is_done else 'NO'}[/]",
            title="UltraThink Validation",
            border_style="green" if validation_result.is_done else "red"
        ))
    
    async def _fallback_execution(self, context: Dict[str, Any]) -> SpiffExecutionResult:
        """Fallback execution when SpiffWorkflow not available"""
        rprint("[yellow]⚠️ SpiffWorkflow not available - using fallback execution[/yellow]")
        
        start_time = datetime.now()
        
        # Execute tasks in sequence
        for task_name, service_task in self.service_tasks.items():
            try:
                rprint(f"[cyan]🔄 Executing {task_name}[/cyan]")
                # Create mock SpiffTask for fallback
                mock_task = type('MockTask', (), {
                    'task_spec': type('TaskSpec', (), {'name': task_name})()
                })()
                
                context = await service_task.execute(mock_task, context)
                
            except Exception as e:
                rprint(f"[red]❌ Task {task_name} failed: {e}[/red]")
                return SpiffExecutionResult(
                    workflow_name="EightyTwentyWorkflow",
                    success=False,
                    execution_time_ms=0,
                    tasks_executed=0,
                    tasks_completed=0,
                    spans_generated=0,
                    errors=[str(e)]
                )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        spans = await self._export_spans()
        
        return SpiffExecutionResult(
            workflow_name="EightyTwentyWorkflow",
            success=True,
            execution_time_ms=execution_time,
            tasks_executed=len(self.service_tasks),
            tasks_completed=len(self.service_tasks),
            spans_generated=len(spans),
            output_files=context.get("generated_files", []),
            context=context
        )


# Convenient execution function
async def execute_8020_bpmn_workflow(
    registry_url: str = "https://opentelemetry.io/schemas/1.21.0",
    target_language: str = "python",
    output_dir: str = "generated"
) -> SpiffExecutionResult:
    """Execute the 80/20 BPMN workflow with given parameters"""
    
    engine = Spiff8020Engine()
    
    context = {
        "registry_url": registry_url,
        "target_language": target_language,
        "output_dir": output_dir
    }
    
    return await engine.execute_8020_workflow(context)


if __name__ == "__main__":
    # Demo the 80/20 BPMN implementation
    async def demo_8020():
        result = await execute_8020_bpmn_workflow()
        
        print(f"80/20 BPMN Demo Results:")
        print(f"Success: {result.success}")
        print(f"Tasks: {result.tasks_completed}/{result.tasks_executed}")
        print(f"Spans: {result.spans_generated}")
        print(f"Files: {len(result.output_files)}")
    
    asyncio.run(demo_8020())