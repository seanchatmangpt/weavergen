# WeaverGen v2 CLI Commands

This directory contains the modular command structure for WeaverGen v2, following an 80/20 implementation approach focusing on the most valuable features.

## Command Structure

The CLI is organized into logical command groups, each in its own module:

### Core Commands

- **`forge`** - Weaver Forge lifecycle commands (init, generate, validate, templates, full-pipeline)
- **`generate`** - Code generation commands (code, models, forge, smart)
- **`validate`** - Validation commands (semantic, code, multi, compliance)
- **`bpmn`** - BPMN workflow execution (execute, orchestrate, list, validate, monitor, debug)

### AI/Agent Commands

- **`agents`** - AI agent operations (communicate, validate, analyze, orchestrate, forge-to-agents)
- **`semantic`** - AI-powered semantic generation (generate, enhance, analyze, merge)

### Analysis & Debugging

- **`debug`** - Debugging and diagnostics (spans, health, inspect, trace, performance)
- **`mining`** - Process mining and XES conversion (convert, discover, analyze, conformance, visualize, predict)

### Configuration & Templates

- **`templates`** - Template management (list, generate, create, validate, install)

## Usage Examples

```bash
# Initialize a new semantic convention registry
weavergen forge init my-registry

# Generate code from semantic conventions
weavergen generate code semantic.yaml --language python

# Validate semantic conventions
weavergen validate semantic registry/

# Execute BPMN workflow
weavergen bpmn execute CodeGeneration --trace

# Run AI agent validation
weavergen agents validate semantic.yaml --agents 5

# Debug with OpenTelemetry spans
weavergen debug spans --format mermaid

# Process mining from spans
weavergen mining convert spans.json --output process.xes

# AI-powered semantic generation
weavergen semantic generate "HTTP server metrics" --model gpt-4

# Full pipeline execution
weavergen full-pipeline semantic.yaml --agents 3
```

## Architecture

Each command module follows a consistent pattern:

1. **Typer App**: Each module exports a Typer app (e.g., `forge_app`, `generate_app`)
2. **OpenTelemetry Tracing**: All commands are instrumented with spans
3. **Rich UI**: Beautiful terminal output using the Rich library
4. **Error Handling**: Consistent error handling and exit codes
5. **Progress Indicators**: Long-running operations show progress
6. **Type Safety**: Full typing annotations

## Adding New Commands

To add a new command:

1. Create a new module in `src/commands/`
2. Define a Typer app for the command group
3. Implement command functions with proper decorators
4. Add OpenTelemetry tracing
5. Import and register in `__init__.py`
6. Add to main CLI in `main.py`

Example structure:
```python
from typer import Typer
from rich.console import Console
from opentelemetry import trace

mycommand_app = Typer(help="My command group")
console = Console()
tracer = trace.get_tracer(__name__)

@mycommand_app.command()
def action(arg: str):
    """Perform an action."""
    with tracer.start_as_current_span("mycommand.action"):
        console.print(f"Performing action: {arg}")
```

## Integration with v2 Engine

The commands are designed to integrate with the WeaverGen v2 engine:

- BPMN workflows can be triggered from any command
- Service tasks are registered for semantic operations
- AI agents can be orchestrated through workflows
- All operations are traced with OpenTelemetry

## Global Options

The main CLI supports global options that affect all commands:

- `--verbose/-v`: Enable verbose output
- `--trace/-t`: Enable OpenTelemetry tracing
- `--quiet/-q`: Suppress non-essential output

These are passed through the context to all subcommands.