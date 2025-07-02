# BPMN-First Development Guide for AI Code Assistance

## Overview

This document provides comprehensive guidance for AI code assistance when working with BPMN-first development patterns in the WeaverGen v2 project. The project follows a strict "BPMN First or Nothing" philosophy where all business logic and workflows are defined in BPMN files and executed through a workflow engine.

## Core Philosophy: BPMN First or Nothing

### Key Principles

1. **BPMN as Source of Truth**: All business logic, workflows, and process definitions must be in BPMN files
2. **No Fallback Logic**: If BPMN workflow fails, the entire operation fails - no fallback to direct code execution
3. **Workflow Engine Execution**: All operations go through the SpiffWorkflow BPMN engine
4. **Service Task Integration**: Business logic is implemented as service tasks registered with the workflow engine
5. **Observability Integration**: All operations are instrumented with OpenTelemetry spans

### Error Handling Pattern

```python
try:
    # Execute BPMN workflow
    instance = engine.start_workflow('ProcessName')
    instance.workflow.data.update(workflow_data)
    instance.run_until_user_input_required()
    
    if instance.workflow.is_completed():
        # Success path
        result_data = instance.workflow.data.get('result_key', {})
        console.print("[green]✓[/green] Workflow completed successfully")
    else:
        # Workflow incomplete - this is an error
        console.print("[yellow]Workflow requires user input[/yellow]")
        span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
        raise typer.Exit(1)
        
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR, str(e)))
    console.print(f"[red]FATAL: Workflow failed: {e}[/red]")
    console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
    raise typer.Exit(1)
```

## BPMN File Structure and Organization

### Directory Structure

```
src/workflows/bpmn/
├── agents/           # AI agent workflows
│   ├── agent_analysis.bpmn
│   ├── agent_communication.bpmn
│   └── agent_generation.bpmn
├── forge/            # Code generation workflows
│   └── forge_init.bpmn
└── xes/              # Process mining workflows
    └── xes_analysis.bpmn
```

### BPMN File Naming Conventions

- **Process ID**: `{Domain}Process` (e.g., `ForgeInitProcess`, `AgentAnalysisProcess`)
- **File Name**: `{domain}_{operation}.bpmn` (e.g., `forge_init.bpmn`, `agent_analysis.bpmn`)
- **Namespace**: `http://weavergen.com/{domain}`

### BPMN Element Naming

- **Tasks**: `Task_{Operation}` (e.g., `Task_ValidateInput`, `Task_CreateDirectories`)
- **Gateways**: `Gateway_{Purpose}` (e.g., `Gateway_CheckExamples`, `Gateway_Validation`)
- **Flows**: `Flow_{From}_{To}` (e.g., `Flow_ToValidateInput`, `Flow_YesExamples`)

## Service Task Implementation Patterns

### 1. Service Task Registration

```python
def register_domain_tasks(environment):
    """Register all domain service tasks with the BPMN environment."""
    tasks = DomainServiceTasks()
    
    # Access environment globals
    if hasattr(environment, 'globals'):
        globals_dict = environment.globals
    elif hasattr(environment, '_globals'):
        globals_dict = environment._globals
    else:
        globals_dict = environment._TaskDataEnvironment__globals
    
    # Register task functions
    globals_dict['domain_validate_params'] = tasks.validate_params
    globals_dict['domain_create_files'] = tasks.create_files
    globals_dict['domain_process_data'] = tasks.process_data
```

### 2. Service Task Implementation

```python
class DomainServiceTasks:
    """Service task implementations for domain workflows."""
    
    @staticmethod
    @create_workflow_task
    def validate_params(data: Dict[str, Any]) -> None:
        """Validate workflow parameters."""
        with tracer.start_as_current_span("domain.service.validate_params") as span:
            # Validate required parameters
            if not data.get('required_param'):
                raise ValueError("Required parameter is missing")
            
            # Set defaults
            data.setdefault('optional_param', 'default_value')
            
            # Add span attributes
            span.set_attribute("param.required", data.get('required_param'))
            span.set_attribute("param.optional", data.get('optional_param'))
    
    @staticmethod
    @create_workflow_task
    def create_files(data: Dict[str, Any]) -> None:
        """Create files and directories."""
        with tracer.start_as_current_span("domain.service.create_files") as span:
            output_dir = Path(data['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file content
            content = f"Generated content for {data['name']}"
            file_path = output_dir / f"{data['name']}.txt"
            file_path.write_text(content)
            
            # Store results in workflow data
            data['created_files'] = [str(file_path)]
            span.set_attribute("files.created", len(data['created_files']))
```

### 3. Workflow Task Decorator

```python
def create_workflow_task(func: Callable) -> Callable:
    """Decorator to create a workflow task that accesses SpiffWorkflow data."""
    def wrapper():
        # Access the execution context to get workflow data
        import inspect
        frame = inspect.currentframe()
        
        # Walk up the stack to find the SpiffWorkflow execution context
        while frame:
            locals_dict = frame.f_locals
            
            # Look for SpiffWorkflow task data
            if 'task' in locals_dict:
                task = locals_dict['task']
                if hasattr(task, 'workflow') and hasattr(task.workflow, 'data'):
                    workflow_data = task.workflow.data
                    if isinstance(workflow_data, dict):
                        return func(workflow_data)
            
            # Alternative: look for 'data' directly in context
            if 'data' in locals_dict and isinstance(locals_dict['data'], dict):
                return func(locals_dict['data'])
            
            frame = frame.f_back
        
        # Fallback if no data found
        console.print("[red]Warning: No workflow data found in execution context[/red]")
        return func({})
    
    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
```

## BPMN Engine Integration

### 1. Engine Initialization

```python
def get_bpmn_engine():
    """Get or create BPMN engine with domain tasks registered."""
    global _engine, _environment
    if _engine is None:
        _environment = WeaverGenServiceEnvironment()
        register_domain_tasks(_environment)
        _engine = SimpleBpmnEngine(_environment)
        
        # Load domain workflows
        workflow_dir = Path(__file__).parent.parent.parent / "workflows" / "bpmn" / "domain"
        if workflow_dir.exists():
            for bpmn_file in workflow_dir.glob("*.bpmn"):
                try:
                    _engine.parser.add_bpmn_file(str(bpmn_file))
                    for process_id in _engine.parser.get_process_ids():
                        spec = _engine.parser.get_spec(process_id)
                        _engine.specs[process_id] = spec
                        console.print(f"[green]✓[/green] Loaded domain workflow: {process_id}")
                except Exception as e:
                    console.print(f"[red]ERROR: Could not load {bpmn_file}: {e}[/red]")
    
    return _engine, _environment
```

### 2. Workflow Execution

```python
def execute_workflow(process_name: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a BPMN workflow with given data."""
    engine, environment = get_bpmn_engine()
    
    # Start workflow
    instance = engine.start_workflow(process_name)
    instance.workflow.data.update(workflow_data)
    
    # Run to completion
    instance.run_until_user_input_required()
    
    if instance.workflow.is_completed():
        return instance.workflow.data
    else:
        raise RuntimeError(f"Workflow {process_name} did not complete")
```

## BPMN File Patterns

### 1. Basic Workflow Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" 
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" 
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI" 
                  id="Definitions_Domain" 
                  targetNamespace="http://weavergen.com/domain">
  
  <bpmn:process id="DomainProcess" name="Domain Operation" isExecutable="true">
    
    <bpmn:startEvent id="StartEvent" name="Start Operation">
      <bpmn:outgoing>Flow_ToValidate</bpmn:outgoing>
    </bpmn:startEvent>
    
    <bpmn:scriptTask id="Task_Validate" name="Validate Input">
      <bpmn:incoming>Flow_ToValidate</bpmn:incoming>
      <bpmn:outgoing>Flow_ToProcess</bpmn:outgoing>
      <bpmn:script>domain_validate_params()</bpmn:script>
    </bpmn:scriptTask>
    
    <bpmn:scriptTask id="Task_Process" name="Process Data">
      <bpmn:incoming>Flow_ToProcess</bpmn:incoming>
      <bpmn:outgoing>Flow_ToEnd</bpmn:outgoing>
      <bpmn:script>domain_process_data()</bpmn:script>
    </bpmn:scriptTask>
    
    <bpmn:endEvent id="EndEvent" name="Operation Complete">
      <bpmn:incoming>Flow_ToEnd</bpmn:incoming>
    </bpmn:endEvent>
    
    <!-- Sequence Flows -->
    <bpmn:sequenceFlow id="Flow_ToValidate" sourceRef="StartEvent" targetRef="Task_Validate"/>
    <bpmn:sequenceFlow id="Flow_ToProcess" sourceRef="Task_Validate" targetRef="Task_Process"/>
    <bpmn:sequenceFlow id="Flow_ToEnd" sourceRef="Task_Process" targetRef="EndEvent"/>
    
  </bpmn:process>
</bpmn:definitions>
```

### 2. Conditional Workflow with Gateway

```xml
<bpmn:exclusiveGateway id="Gateway_CheckCondition" name="Check Condition?">
  <bpmn:incoming>Flow_ToGateway</bpmn:incoming>
  <bpmn:outgoing>Flow_YesCondition</bpmn:outgoing>
  <bpmn:outgoing>Flow_NoCondition</bpmn:outgoing>
</bpmn:exclusiveGateway>

<bpmn:scriptTask id="Task_ProcessYes" name="Process Yes Path">
  <bpmn:incoming>Flow_YesCondition</bpmn:incoming>
  <bpmn:outgoing>Flow_ToJoin</bpmn:outgoing>
  <bpmn:script>domain_process_yes_path()</bpmn:script>
</bpmn:scriptTask>

<bpmn:scriptTask id="Task_ProcessNo" name="Process No Path">
  <bpmn:incoming>Flow_NoCondition</bpmn:incoming>
  <bpmn:outgoing>Flow_ToJoin</bpmn:outgoing>
  <bpmn:script>domain_process_no_path()</bpmn:script>
</bpmn:scriptTask>

<bpmn:parallelGateway id="Gateway_Join" name="Join Paths">
  <bpmn:incoming>Flow_ToJoin</bpmn:incoming>
  <bpmn:incoming>Flow_ToJoin</bpmn:incoming>
  <bpmn:outgoing>Flow_ToEnd</bpmn:outgoing>
</bpmn:parallelGateway>
```

### 3. Parallel Processing

```xml
<bpmn:parallelGateway id="Gateway_ParallelStart" name="Start Parallel">
  <bpmn:incoming>Flow_ToParallel</bpmn:incoming>
  <bpmn:outgoing>Flow_ToTask1</bpmn:outgoing>
  <bpmn:outgoing>Flow_ToTask2</bpmn:outgoing>
</bpmn:parallelGateway>

<bpmn:scriptTask id="Task_Parallel1" name="Parallel Task 1">
  <bpmn:incoming>Flow_ToTask1</bpmn:incoming>
  <bpmn:outgoing>Flow_FromTask1</bpmn:outgoing>
  <bpmn:script>domain_parallel_task_1()</bpmn:script>
</bpmn:scriptTask>

<bpmn:scriptTask id="Task_Parallel2" name="Parallel Task 2">
  <bpmn:incoming>Flow_ToTask2</bpmn:incoming>
  <bpmn:outgoing>Flow_FromTask2</bpmn:outgoing>
  <bpmn:script>domain_parallel_task_2()</bpmn:script>
</bpmn:scriptTask>

<bpmn:parallelGateway id="Gateway_ParallelJoin" name="Join Parallel">
  <bpmn:incoming>Flow_FromTask1</bpmn:incoming>
  <bpmn:incoming>Flow_FromTask2</bpmn:incoming>
  <bpmn:outgoing>Flow_ToEnd</bpmn:outgoing>
</bpmn:parallelGateway>
```

## CLI Command Integration

### 1. Command Structure

```python
@domain_app.command()
def operation(
    input_file: Path = typer.Argument(..., help="Input file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Execute domain operation through BPMN workflow."""
    
    with cli_command_span("domain.operation") as span:
        span.set_attribute("input_file", str(input_file))
        span.set_attribute("output_file", str(output) if output else "none")
        span.set_attribute("verbose", verbose)
        
        try:
            # Get BPMN engine
            engine, environment = get_bpmn_engine()
            
            # Prepare workflow data
            workflow_data = {
                'input_file': str(input_file),
                'output_file': str(output) if output else None,
                'verbose': verbose
            }
            
            # Execute BPMN workflow
            console.print(f"[cyan]Executing domain workflow: DomainProcess[/cyan]")
            
            instance = engine.start_workflow('DomainProcess')
            instance.workflow.data.update(workflow_data)
            
            # Run workflow to completion
            instance.run_until_user_input_required()
            
            if instance.workflow.is_completed():
                # Get results from workflow
                result_data = instance.workflow.data.get('operation_result', {})
                console.print("[green]✓[/green] Domain operation completed successfully")
                
                # Display results
                _display_operation_results(result_data)
                
                span.set_status(Status(StatusCode.OK))
            else:
                console.print("[yellow]Workflow requires user input[/yellow]")
                span.set_status(Status(StatusCode.ERROR, "Workflow incomplete"))
                raise typer.Exit(1)
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            console.print(f"[red]FATAL: Domain operation workflow failed: {e}[/red]")
            console.print("[red]NO FALLBACK - BPMN FIRST OR NOTHING[/red]")
            raise typer.Exit(1)
```

### 2. Error Handling Pattern

```python
def _display_operation_results(result_data: Dict[str, Any]) -> None:
    """Display operation results."""
    if result_data.get('success'):
        console.print(f"[green]✓[/green] Operation successful")
        if result_data.get('output_files'):
            console.print(f"Generated files: {result_data['output_files']}")
    else:
        console.print(f"[red]✗[/red] Operation failed: {result_data.get('error', 'Unknown error')}")
```

## Observability Integration

### 1. Span Creation

```python
@semantic_span("domain.operation", "execute_workflow")
def execute_domain_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute domain workflow with span tracking."""
    # Implementation here
    pass
```

### 2. Span Attributes

```python
def domain_operation(data: Dict[str, Any]) -> None:
    """Domain operation with span tracking."""
    with tracer.start_as_current_span("domain.service.operation") as span:
        # Set span attributes
        span.set_attribute("operation.type", data.get('operation_type', 'unknown'))
        span.set_attribute("input.size", len(str(data.get('input', ''))))
        span.set_attribute("output.expected", data.get('output_expected', False))
        
        # Perform operation
        result = perform_operation(data)
        
        # Add result attributes
        span.set_attribute("operation.success", result.get('success', False))
        span.set_attribute("output.size", len(str(result.get('output', ''))))
```

### 3. Event Recording

```python
def domain_process_data(data: Dict[str, Any]) -> None:
    """Process data with event recording."""
    with tracer.start_as_current_span("domain.service.process_data") as span:
        # Record start event
        span.add_event("data_processing.started", {
            "data_size": len(str(data.get('input', ''))),
            "processing_type": data.get('processing_type', 'default')
        })
        
        # Process data
        result = process_data(data)
        
        # Record completion event
        span.add_event("data_processing.completed", {
            "result_size": len(str(result)),
            "processing_time_ms": result.get('processing_time', 0)
        })
```

## Testing Patterns

### 1. BPMN Workflow Testing

```python
def test_domain_workflow():
    """Test domain BPMN workflow execution."""
    # Initialize engine
    environment = WeaverGenServiceEnvironment()
    register_domain_tasks(environment)
    engine = SimpleBpmnEngine(environment)
    
    # Load workflow
    workflow_dir = Path("src/workflows/bpmn/domain")
    for bpmn_file in workflow_dir.glob("*.bpmn"):
        engine.parser.add_bpmn_file(str(bpmn_file))
    
    # Test workflow execution
    instance = engine.start_workflow('DomainProcess')
    instance.workflow.data.update({
        'input_file': 'test_input.txt',
        'output_file': 'test_output.txt'
    })
    
    # Run workflow
    instance.run_until_user_input_required()
    
    # Assert completion
    assert instance.workflow.is_completed()
    assert 'operation_result' in instance.workflow.data
```

### 2. Service Task Testing

```python
def test_domain_service_tasks():
    """Test domain service tasks."""
    tasks = DomainServiceTasks()
    
    # Test with mock data
    test_data = {
        'input_file': 'test.txt',
        'output_file': 'output.txt'
    }
    
    # Test validation
    tasks.validate_params(test_data)
    assert 'validated' in test_data
    
    # Test processing
    tasks.process_data(test_data)
    assert 'processed' in test_data
```

## Best Practices for AI Code Assistance

### 1. Always Start with BPMN

When implementing new functionality:

1. **Design the BPMN workflow first** - Define the process flow, tasks, and decision points
2. **Create the BPMN file** - Implement the workflow in XML format
3. **Implement service tasks** - Create the Python functions that will be called by the workflow
4. **Register tasks with engine** - Connect the service tasks to the BPMN engine
5. **Create CLI command** - Implement the CLI interface that executes the workflow

### 2. Error Handling

- **No fallbacks**: If BPMN workflow fails, the entire operation fails
- **Clear error messages**: Provide specific error information for debugging
- **Span recording**: Record all errors in OpenTelemetry spans
- **Graceful degradation**: Handle workflow incompletion scenarios

### 3. Data Flow

- **Workflow data**: All data flows through the workflow's data dictionary
- **Service task access**: Use the `@create_workflow_task` decorator to access workflow data
- **Result storage**: Store results in the workflow data for access by subsequent tasks
- **Data validation**: Validate data at the beginning of workflows

### 4. Observability

- **Span creation**: Create spans for all major operations
- **Attribute setting**: Set relevant attributes on spans for monitoring
- **Event recording**: Record important events during workflow execution
- **Error tracking**: Record exceptions and error conditions

### 5. Testing

- **Workflow testing**: Test complete workflow execution
- **Service task testing**: Test individual service tasks
- **Error scenario testing**: Test workflow behavior under error conditions
- **Integration testing**: Test workflow integration with external systems

## Common Patterns and Anti-Patterns

### ✅ Good Patterns

1. **BPMN-first design**: Always start with BPMN workflow design
2. **Service task separation**: Keep business logic in service tasks
3. **Data flow through workflow**: Pass data through workflow data dictionary
4. **Comprehensive error handling**: Handle all error scenarios in BPMN
5. **Observability integration**: Instrument all operations with spans

### ❌ Anti-Patterns

1. **Direct code execution**: Implementing logic outside of BPMN workflows
2. **Fallback mechanisms**: Providing fallback logic when BPMN fails
3. **Bypassing workflow engine**: Direct function calls instead of workflow execution
4. **Missing error handling**: Not handling workflow failure scenarios
5. **Poor observability**: Not instrumenting operations with spans

## Conclusion

The BPMN-first approach in WeaverGen v2 ensures that all business logic is defined in a standardized, visual format that can be easily understood, modified, and monitored. This approach provides several benefits:

1. **Visual Process Definition**: BPMN provides a clear visual representation of business processes
2. **Standardized Execution**: All operations follow the same execution pattern through the workflow engine
3. **Comprehensive Observability**: All operations are instrumented with OpenTelemetry
4. **Error Resilience**: Consistent error handling across all operations
5. **Maintainability**: Clear separation between process definition and implementation

When providing AI code assistance for this project, always prioritize BPMN-first development and ensure that all business logic flows through the workflow engine rather than being implemented as direct code execution. 