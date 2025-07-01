# 🔄 WEAVERGEN V2: BPMN-FIRST ARCHITECTURE DESIGN

**Design Date:** 2025-07-01  
**Scope:** Complete BPMN workflow specifications for all Weaver operations  
**Framework:** SpiffWorkflow + OpenTelemetry + Pydantic AI  

---

## 🎯 BPMN-FIRST DESIGN PRINCIPLES

### 1. **Every Operation = BPMN Workflow**
```
No direct Python function calls in CLI
All operations execute through BPMN workflows
Visual workflow diagrams for all processes
SpiffWorkflow engine handles execution
```

### 2. **Service Task Registry Pattern**
```python
# Service tasks map to Python functions with span capture
SERVICE_TASK_REGISTRY = {
    "weaver.registry.check": WeaverRegistryService.check,
    "weaver.registry.generate": WeaverRegistryService.generate,
    "ai.template.optimize": AITemplateService.optimize,
    "pydantic.model.generate": PydanticModelService.generate,
    "validation.span.capture": ValidationService.capture_spans
}
```

### 3. **Span-Instrumented Execution**
```python
# Every BPMN service task captures spans
async def execute_service_task(task_name: str, context: dict) -> TaskResult:
    with tracer.start_as_current_span(f"bpmn.service.{task_name}") as span:
        span.set_attributes({
            "bpmn.workflow": context["workflow_name"],
            "bpmn.task": task_name,
            "bpmn.execution_id": context["execution_id"]
        })
        return await SERVICE_TASK_REGISTRY[task_name](context)
```

---

## 🏗️ CORE BPMN WORKFLOWS

### 1. **Registry Check Workflow** (`registry_check.bpmn`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn:process id="registry_check" isExecutable="true">
    
    <!-- Start Event -->
    <bpmn:startEvent id="start_check" name="Start Registry Check"/>
    
    <!-- Load Registry -->
    <bpmn:serviceTask id="load_registry" name="Load Registry" 
                      camunda:delegateExpression="weaver.registry.load"/>
    
    <!-- Validate Registry -->
    <bpmn:serviceTask id="validate_registry" name="Validate Registry"
                      camunda:delegateExpression="weaver.registry.validate"/>
    
    <!-- Policy Validation Gateway -->
    <bpmn:exclusiveGateway id="policy_gateway" name="Policies Provided?"/>
    
    <!-- Policy Validation -->
    <bpmn:serviceTask id="validate_policies" name="Validate Policies"
                      camunda:delegateExpression="weaver.policy.validate"/>
    
    <!-- AI Analysis -->
    <bpmn:serviceTask id="ai_analysis" name="AI Registry Analysis"
                      camunda:delegateExpression="ai.registry.analyze"/>
    
    <!-- Format Output -->
    <bpmn:serviceTask id="format_output" name="Format Output"
                      camunda:delegateExpression="output.format"/>
    
    <!-- End Event -->
    <bpmn:endEvent id="end_check" name="Check Complete"/>
    
  </bpmn:process>
</bpmn:definitions>
```

**Service Task Implementations:**
```python
class WeaverRegistryService:
    @staticmethod
    async def load(context: dict) -> dict:
        with tracer.start_as_current_span("weaver.registry.load") as span:
            registry_url = context["registry"]
            span.set_attribute("registry.url", registry_url)
            
            # Load registry from local/git/archive
            registry_data = await load_registry_source(registry_url)
            return {"registry_data": registry_data}
    
    @staticmethod
    async def validate(context: dict) -> dict:
        with tracer.start_as_current_span("weaver.registry.validate") as span:
            registry_data = context["registry_data"]
            
            # Execute weaver registry check
            result = await execute_weaver_command(
                ["registry", "check", "--registry", context["registry"]]
            )
            
            span.set_attributes({
                "validation.success": result.success,
                "validation.errors": len(result.errors),
                "validation.warnings": len(result.warnings)
            })
            
            return {"validation_result": result}
```

### 2. **Multi-Language Generation Workflow** (`registry_generate.bpmn`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn:process id="registry_generate" isExecutable="true">
    
    <!-- Start Event -->
    <bpmn:startEvent id="start_generate" name="Start Generation"/>
    
    <!-- Load Registry -->
    <bpmn:serviceTask id="load_registry" name="Load Registry"
                      camunda:delegateExpression="weaver.registry.load"/>
    
    <!-- AI Template Optimization -->
    <bpmn:serviceTask id="optimize_templates" name="AI Template Optimization"
                      camunda:delegateExpression="ai.template.optimize"/>
    
    <!-- Parallel Gateway for Multi-Language -->
    <bpmn:parallelGateway id="parallel_generate" name="Parallel Generation"/>
    
    <!-- Python Generation -->
    <bpmn:serviceTask id="generate_python" name="Generate Python"
                      camunda:delegateExpression="weaver.generate.python"/>
    
    <!-- Rust Generation -->
    <bpmn:serviceTask id="generate_rust" name="Generate Rust"
                      camunda:delegateExpression="weaver.generate.rust"/>
    
    <!-- Go Generation -->
    <bpmn:serviceTask id="generate_go" name="Generate Go"
                      camunda:delegateExpression="weaver.generate.go"/>
    
    <!-- Join Gateway -->
    <bpmn:parallelGateway id="join_generate" name="Join Results"/>
    
    <!-- Pydantic Model Generation -->
    <bpmn:serviceTask id="generate_pydantic" name="Generate Pydantic Models"
                      camunda:delegateExpression="pydantic.model.generate"/>
    
    <!-- Validation -->
    <bpmn:serviceTask id="validate_output" name="Validate Generated Code"
                      camunda:delegateExpression="validation.code.validate"/>
    
    <!-- End Event -->
    <bpmn:endEvent id="end_generate" name="Generation Complete"/>
    
  </bpmn:process>
</bpmn:definitions>
```

### 3. **Live Telemetry Validation Workflow** (`live_check.bpmn`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn:process id="live_check" isExecutable="true">
    
    <!-- Start Event -->
    <bpmn:startEvent id="start_live_check" name="Start Live Check"/>
    
    <!-- Start OTLP Server -->
    <bpmn:serviceTask id="start_otlp_server" name="Start OTLP Server"
                      camunda:delegateExpression="otlp.server.start"/>
    
    <!-- Start Admin Server -->
    <bpmn:serviceTask id="start_admin_server" name="Start Admin Server"
                      camunda:delegateExpression="admin.server.start"/>
    
    <!-- Event Subprocess for Telemetry Processing -->
    <bpmn:subProcess id="process_telemetry" name="Process Telemetry">
      
      <!-- Message Start Event -->
      <bpmn:startEvent id="telemetry_received" name="Telemetry Received"/>
      
      <!-- Validate Against Registry -->
      <bpmn:serviceTask id="validate_telemetry" name="Validate Telemetry"
                        camunda:delegateExpression="telemetry.validate"/>
      
      <!-- AI Quality Assessment -->
      <bpmn:serviceTask id="ai_assessment" name="AI Quality Assessment"
                        camunda:delegateExpression="ai.telemetry.assess"/>
      
      <!-- Stream Results -->
      <bpmn:serviceTask id="stream_results" name="Stream Results"
                        camunda:delegateExpression="telemetry.stream"/>
      
    </bpmn:subProcess>
    
    <!-- Timer Event for Inactivity -->
    <bpmn:intermediateCatchEvent id="inactivity_timer" name="Inactivity Timeout">
      <bpmn:timerEventDefinition>
        <bpmn:timeDuration>PT10S</bpmn:timeDuration>
      </bpmn:timerEventDefinition>
    </bpmn:intermediateCatchEvent>
    
    <!-- Stop Servers -->
    <bpmn:serviceTask id="stop_servers" name="Stop Servers"
                      camunda:delegateExpression="servers.stop"/>
    
    <!-- End Event -->
    <bpmn:endEvent id="end_live_check" name="Live Check Complete"/>
    
  </bpmn:process>
</bpmn:definitions>
```

---

## 🎨 SPIFFWORKFLOW INTEGRATION

### Engine Configuration
```python
# v2/core/engine/spiff_engine.py
from SpiffWorkflow import Workflow
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.task import Task

class WeaverGenV2Engine:
    def __init__(self):
        self.service_registry = ServiceTaskRegistry()
        self.tracer = get_tracer("weavergen.v2.engine")
        self.serializer = WorkflowSerializer()
    
    async def execute_workflow(self, workflow_path: str, context: dict) -> WorkflowResult:
        with self.tracer.start_as_current_span("bpmn.workflow.execute") as span:
            span.set_attributes({
                "workflow.path": workflow_path,
                "workflow.context_keys": list(context.keys())
            })
            
            # Load BPMN workflow
            workflow = self.load_workflow(workflow_path)
            
            # Set initial context
            workflow.set_data(context)
            
            # Execute with span capture
            result = await self._execute_with_spans(workflow)
            
            return result
    
    async def _execute_with_spans(self, workflow: BpmnWorkflow) -> WorkflowResult:
        while not workflow.is_completed():
            # Get ready tasks
            ready_tasks = workflow.get_ready_user_tasks()
            
            for task in ready_tasks:
                await self._execute_task_with_span(task)
        
        return WorkflowResult(
            success=workflow.is_completed(),
            data=workflow.get_data(),
            execution_time=self._calculate_execution_time(workflow)
        )
    
    async def _execute_task_with_span(self, task: Task):
        task_name = task.task_spec.name
        
        with self.tracer.start_as_current_span(f"bpmn.task.{task_name}") as span:
            span.set_attributes({
                "task.name": task_name,
                "task.type": task.task_spec.__class__.__name__,
                "task.id": task.id
            })
            
            if task.task_spec.name in self.service_registry:
                # Execute service task
                result = await self.service_registry.execute(
                    task.task_spec.name, 
                    task.data
                )
                task.set_data(result)
            
            # Complete the task
            task.complete()
```

### Service Task Registry
```python
# v2/core/engine/service_registry.py
class ServiceTaskRegistry:
    def __init__(self):
        self.tasks = {}
        self._register_core_tasks()
    
    def _register_core_tasks(self):
        # Weaver operations
        self.register("weaver.registry.load", WeaverRegistryService.load)
        self.register("weaver.registry.check", WeaverRegistryService.check)
        self.register("weaver.registry.generate", WeaverRegistryService.generate)
        self.register("weaver.registry.resolve", WeaverRegistryService.resolve)
        self.register("weaver.registry.search", WeaverRegistryService.search)
        self.register("weaver.registry.stats", WeaverRegistryService.stats)
        self.register("weaver.registry.update_markdown", WeaverRegistryService.update_markdown)
        self.register("weaver.registry.json_schema", WeaverRegistryService.json_schema)
        self.register("weaver.registry.diff", WeaverRegistryService.diff)
        self.register("weaver.registry.emit", WeaverRegistryService.emit)
        self.register("weaver.registry.live_check", WeaverRegistryService.live_check)
        
        # AI operations
        self.register("ai.registry.analyze", AIRegistryService.analyze)
        self.register("ai.template.optimize", AITemplateService.optimize)
        self.register("ai.telemetry.assess", AITelemetryService.assess)
        
        # Pydantic operations
        self.register("pydantic.model.generate", PydanticModelService.generate)
        
        # Validation operations
        self.register("validation.code.validate", ValidationService.validate_code)
        self.register("validation.span.capture", ValidationService.capture_spans)
        
        # Output operations
        self.register("output.format", OutputService.format)
        self.register("output.rich.console", OutputService.rich_console)
        self.register("output.mermaid.diagram", OutputService.mermaid_diagram)
    
    def register(self, task_name: str, handler: Callable):
        self.tasks[task_name] = handler
    
    async def execute(self, task_name: str, context: dict) -> dict:
        if task_name not in self.tasks:
            raise ValueError(f"Unknown service task: {task_name}")
        
        handler = self.tasks[task_name]
        return await handler(context)
```

---

## 🔧 CLI INTEGRATION

### BPMN-Based CLI Commands
```python
# v2/cli/commands/registry.py
import typer
from rich.console import Console

app = typer.Typer(name="registry", help="Registry operations")
console = Console()

@app.command("check")
async def registry_check(
    registry: str = typer.Option("https://github.com/open-telemetry/semantic-conventions.git[model]"),
    follow_symlinks: bool = typer.Option(False),
    future: bool = typer.Option(False),
    policies: Optional[List[str]] = typer.Option(None),
    skip_policies: bool = typer.Option(False),
    diagnostic_format: str = typer.Option("ansi"),
    quiet: bool = typer.Option(False)
):
    """Validate a semantic convention registry via BPMN workflow"""
    
    # Build workflow context from CLI parameters
    context = {
        "registry": registry,
        "follow_symlinks": follow_symlinks,
        "future": future,
        "policies": policies or [],
        "skip_policies": skip_policies,
        "diagnostic_format": diagnostic_format,
        "quiet": quiet,
        "cli_command": "registry check"
    }
    
    # Execute BPMN workflow
    with console.status("🔍 Executing registry check workflow..."):
        engine = get_workflow_engine()
        result = await engine.execute_workflow("registry_check.bpmn", context)
    
    # Display results with rich formatting
    if result.success:
        console.print("✅ Registry validation completed successfully", style="green")
        
        # Display validation summary
        validation_data = result.data["validation_result"]
        console.print(f"Registry: {registry}")
        console.print(f"Errors: {len(validation_data.errors)}")
        console.print(f"Warnings: {len(validation_data.warnings)}")
        
        # AI insights if available
        if "ai_analysis" in result.data:
            console.print("\n🤖 AI Analysis:")
            console.print(result.data["ai_analysis"]["summary"])
    else:
        console.print("❌ Registry validation failed", style="red")
        console.print(result.error_message)
```

### Workflow Context Management
```python
# v2/cli/context.py
class WorkflowContext:
    """Manages context for BPMN workflow execution"""
    
    def __init__(self):
        self.base_context = {
            "execution_id": generate_execution_id(),
            "timestamp": datetime.now().isoformat(),
            "version": get_weavergen_version()
        }
    
    def build_registry_context(self, **cli_params) -> dict:
        """Build context for registry operations"""
        return {
            **self.base_context,
            **cli_params,
            "operation_type": "registry",
            "span_prefix": "weavergen.v2.registry"
        }
    
    def build_generation_context(self, target: str, **cli_params) -> dict:
        """Build context for generation operations"""
        return {
            **self.base_context,
            **cli_params,
            "target": target,
            "operation_type": "generation",
            "span_prefix": "weavergen.v2.generation"
        }
```

---

## 📊 WORKFLOW MONITORING

### Span Collection System
```python
# v2/validation/span_collector.py
class WorkflowSpanCollector:
    """Collects and analyzes spans from BPMN workflow execution"""
    
    def __init__(self):
        self.spans = []
        self.trace_processor = TraceProcessor()
    
    async def collect_workflow_spans(self, execution_id: str) -> List[Span]:
        """Collect all spans for a workflow execution"""
        spans = await self.trace_processor.get_spans_by_execution_id(execution_id)
        
        # Group by workflow steps
        workflow_spans = {}
        for span in spans:
            step_name = span.attributes.get("bpmn.task", "unknown")
            if step_name not in workflow_spans:
                workflow_spans[step_name] = []
            workflow_spans[step_name].append(span)
        
        return workflow_spans
    
    async def generate_workflow_report(self, execution_id: str) -> WorkflowReport:
        """Generate detailed workflow execution report"""
        spans = await self.collect_workflow_spans(execution_id)
        
        report = WorkflowReport(
            execution_id=execution_id,
            total_steps=len(spans),
            total_duration=sum(s.duration for step_spans in spans.values() for s in step_spans),
            success_rate=self._calculate_success_rate(spans),
            step_performance=self._analyze_step_performance(spans)
        )
        
        return report
```

### Mermaid Diagram Generation
```python
# v2/diagnostics/mermaid_generator.py
class WorkflowMermaidGenerator:
    """Generate Mermaid diagrams from workflow execution spans"""
    
    def generate_execution_diagram(self, spans: Dict[str, List[Span]]) -> str:
        """Generate Mermaid flowchart from execution spans"""
        
        mermaid = ["graph TD"]
        
        # Add nodes for each step
        for step_name, step_spans in spans.items():
            duration = sum(s.duration for s in step_spans)
            success = all(s.status == "OK" for s in step_spans)
            
            icon = "✅" if success else "❌"
            mermaid.append(f'    {self._sanitize_name(step_name)}["{icon} {step_name}<br/>{duration:.2f}ms"]')
        
        # Add connections based on execution order
        step_names = list(spans.keys())
        for i in range(len(step_names) - 1):
            current = self._sanitize_name(step_names[i])
            next_step = self._sanitize_name(step_names[i + 1])
            mermaid.append(f"    {current} --> {next_step}")
        
        return "\n".join(mermaid)
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for Mermaid syntax"""
        return name.replace(".", "_").replace(" ", "_").replace("-", "_")
```

---

## 🎯 VALIDATION INTEGRATION

### End-to-End Workflow Validation
```python
# v2/validation/workflow_validator.py
class WorkflowValidator:
    """Validates BPMN workflow execution using spans"""
    
    async def validate_registry_check_workflow(self, execution_id: str) -> ValidationResult:
        """Validate registry check workflow execution"""
        
        spans = await self.span_collector.collect_workflow_spans(execution_id)
        
        validations = []
        
        # Validate required steps
        required_steps = [
            "weaver.registry.load",
            "weaver.registry.validate",
            "output.format"
        ]
        
        for step in required_steps:
            if step in spans:
                step_spans = spans[step]
                validation = self._validate_step_execution(step, step_spans)
                validations.append(validation)
            else:
                validations.append(ValidationResult(
                    step=step,
                    success=False,
                    error="Step not executed"
                ))
        
        return WorkflowValidationResult(
            workflow="registry_check",
            execution_id=execution_id,
            step_validations=validations,
            overall_success=all(v.success for v in validations)
        )
```

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Workflow File Organization
```
v2/workflows/
├── bpmn/
│   ├── registry/
│   │   ├── registry_check.bpmn
│   │   ├── registry_generate.bpmn
│   │   ├── registry_resolve.bpmn
│   │   ├── registry_search.bpmn
│   │   ├── registry_stats.bpmn
│   │   ├── registry_update_markdown.bpmn
│   │   ├── registry_json_schema.bpmn
│   │   ├── registry_diff.bpmn
│   │   ├── registry_emit.bpmn
│   │   └── registry_live_check.bpmn
│   ├── ai/
│   │   ├── template_optimization.bpmn
│   │   ├── semantic_analysis.bpmn
│   │   └── quality_assessment.bpmn
│   ├── validation/
│   │   ├── span_validation.bpmn
│   │   └── code_validation.bpmn
│   └── utils/
│       ├── diagnostic_init.bpmn
│       └── shell_completion.bpmn
├── service_tasks/
│   ├── weaver_services.py
│   ├── ai_services.py
│   ├── pydantic_services.py
│   └── validation_services.py
└── engine/
    ├── spiff_engine.py
    ├── service_registry.py
    └── workflow_loader.py
```

---

**🎯 BPMN-FIRST DESIGN CONCLUSION**

This architecture ensures that:
- **Every CLI command executes through BPMN workflows**
- **All Weaver operations are visually represented**
- **Span-based validation captures real execution**
- **AI enhancements are integrated at the workflow level**
- **Parallel processing is orchestrated through BPMN gateways**

The design provides **complete observability**, **visual workflow management**, and **enterprise-grade orchestration** while maintaining **100% Weaver compatibility**.