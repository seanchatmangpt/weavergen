"""Service tasks for Forge BPMN workflows."""

from pathlib import Path
from typing import Dict, Any, Callable
from rich.console import Console
from opentelemetry import trace

console = Console()
tracer = trace.get_tracer(__name__)


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
                # Check if task has workflow data
                if hasattr(task, 'workflow') and hasattr(task.workflow, 'data'):
                    workflow_data = task.workflow.data
                    # Just return the workflow data as-is
                    if isinstance(workflow_data, dict):
                        return func(workflow_data)
                elif hasattr(task, 'data'):
                    console.print(f"[yellow]Found task.data (checking if it has our data)[/yellow]")
                    return func(task.data)
            
            # Alternative: look for 'data' directly in context
            if 'data' in locals_dict and isinstance(locals_dict['data'], dict):
                # console.print(f"[green]Found data in locals: {locals_dict['data']}[/green]")
                return func(locals_dict['data'])
            
            # Look for context variable
            if 'context' in locals_dict and isinstance(locals_dict['context'], dict):
                if 'data' in locals_dict['context']:
                    return func(locals_dict['context']['data'])
            
            frame = frame.f_back
        
        # Fallback if no data found
        console.print("[red]Warning: No workflow data found in execution context[/red]")
        return func({})
    
    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


class ForgeServiceTasks:
    """Service task implementations for Forge workflows."""
    
    @staticmethod
    @create_workflow_task
    def validate_init_params(data: Dict[str, Any]) -> None:
        """Validate init command parameters."""
        with tracer.start_as_current_span("forge.service.validate_init_params") as span:
            span.set_attribute("registry_name", data.get('registry_name', 'unknown'))
            
            # Validate required parameters
            if not data.get('registry_name'):
                raise ValueError("Registry name is required")
            
            # Set defaults
            data.setdefault('output_dir', Path('./semantic_conventions'))
            data.setdefault('with_examples', True)
    
    @staticmethod
    @create_workflow_task
    def create_registry_dirs(data: Dict[str, Any]) -> None:
        """Create registry directory structure."""
        with tracer.start_as_current_span("forge.service.create_dirs") as span:
            output_dir = Path(data['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            model_dir = output_dir / "model"
            model_dir.mkdir(exist_ok=True)
            
            data['model_dir'] = str(model_dir)
            span.set_attribute("directories.created", 2)
    
    @staticmethod
    @create_workflow_task
    def create_manifest_yaml(data: Dict[str, Any]) -> None:
        """Create registry manifest YAML."""
        with tracer.start_as_current_span("forge.service.create_manifest") as span:
            name = data['registry_name']
            output_dir = Path(data['output_dir'])
            
            manifest_content = f"""name: {name}
description: Semantic conventions for {name} telemetry
semconv_version: 0.1.0
schema_base_url: https://{name.lower()}.com/schemas/
dependencies:
  - name: otel
    registry_path: https://github.com/open-telemetry/semantic-conventions/archive/refs/tags/v1.34.0.zip[model]
"""
            
            manifest_path = output_dir / "registry_manifest.yaml"
            manifest_path.write_text(manifest_content)
            console.print(f"[green]✓[/green] Created {manifest_path}")
            
            span.set_attribute("file.created", str(manifest_path))
            data['manifest_path'] = str(manifest_path)
    
    @staticmethod
    @create_workflow_task
    def create_example_yamls(data: Dict[str, Any]) -> None:
        """Create example semantic convention YAML files."""
        with tracer.start_as_current_span("forge.service.create_examples") as span:
            name = data['registry_name']
            model_dir = Path(data['model_dir'])
            
            # Create common attributes example
            example_content = f"""groups:
  # Example attribute group
  - id: {name.lower()}.common
    prefix: {name.lower()}
    type: attribute_group
    brief: 'Common attributes for {name} telemetry'
    attributes:
      - id: service.component
        type: string
        requirement_level: required
        brief: 'The component within the service'
        examples: ['api', 'worker', 'scheduler']
"""
            
            example_path = model_dir / f"{name.lower()}_common.yaml"
            example_path.write_text(example_content)
            console.print(f"[green]✓[/green] Created {example_path}")
            
            # Create service example
            service_content = f"""groups:
  # Service-specific spans
  - id: {name.lower()}.database
    prefix: {name.lower()}.db
    type: span
    brief: 'Database operations in {name} service'
    span_kind: client
    attributes:
      - ref: {name.lower()}.common.service.component
"""
            
            service_path = model_dir / f"{name.lower()}_service.yaml"
            service_path.write_text(service_content)
            console.print(f"[green]✓[/green] Created {service_path}")
            
            span.set_attribute("files.created", 2)
            data['example_files'] = [str(example_path), str(service_path)]
    
    @staticmethod
    @create_workflow_task
    def display_next_steps(data: Dict[str, Any]) -> None:
        """Display next steps after initialization."""
        with tracer.start_as_current_span("forge.service.display_next_steps") as span:
            output_dir = data['output_dir']
            
            console.print("\n[bold green]Semantic convention registry initialized![/bold green]")
            console.print("\nNext steps:")
            console.print(f"  1. Check your registry: [cyan]weaver registry check -r {output_dir}[/cyan]")
            console.print(f"  2. Generate code: [cyan]weaver registry generate -r {output_dir} -t <target>[/cyan]")
            console.print(f"  3. Edit the YAML files in {output_dir} to define your telemetry")
            
            span.set_attribute("workflow.completed", True)


def register_forge_tasks(environment):
    """Register all forge service tasks with the BPMN environment."""
    tasks = ForgeServiceTasks()
    
    # Update the environment's globals to include our functions
    if hasattr(environment, 'globals'):
        globals_dict = environment.globals
    elif hasattr(environment, '_globals'):
        globals_dict = environment._globals
    else:
        # Access the internal context through the parent class
        globals_dict = environment._TaskDataEnvironment__globals
    
    # Add forge service handlers
    globals_dict['forge_validate_init_params'] = tasks.validate_init_params
    globals_dict['forge_create_registry_dirs'] = tasks.create_registry_dirs
    globals_dict['forge_create_manifest_yaml'] = tasks.create_manifest_yaml
    globals_dict['forge_create_example_yamls'] = tasks.create_example_yamls
    globals_dict['forge_display_next_steps'] = tasks.display_next_steps