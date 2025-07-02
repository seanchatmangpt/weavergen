# Weaver CLI Generation Demonstration

## Concept: Tool-Based Semantic CLI Structure

Based on the semantic conventions in `weavergen_tool_cli.yaml`, Weaver would generate a CLI organized around **tools**:

```
weavergen <tool> <action> [options]
```

## Generated CLI Structure

### 1. **workflow** - BPMN Operations (replaces current workflow + bpmn commands)

```bash
# Generated from cli.tool.workflow semantic conventions
weavergen workflow create my-process --template semantic-processing
weavergen workflow run my-process --data input.json --trace
weavergen workflow validate process.bpmn
weavergen workflow list
weavergen workflow debug my-process --breakpoint Task_Validate
weavergen workflow visualize my-process --style flow
```

**Consolidates**:
- Current: `weavergen add`, `weavergen run`, `weavergen workflow run`, `weavergen bpmn execute`
- New: Single `weavergen workflow` tool with clear actions

### 2. **weaver** - OTel Weaver Operations

```bash
# Generated from cli.tool.weaver semantic conventions
weavergen weaver generate semantic.yaml --language python
weavergen weaver validate semantic.yaml --strict
weavergen weaver templates --language go
weavergen weaver install --version latest
weavergen weaver check --registry ./semantic_conventions
```

**Consolidates**:
- Current: `weavergen generate code`, `weavergen validate semantic`, scattered template commands
- New: All Weaver operations under one tool

### 3. **forge** - Advanced Forge Operations

```bash
# Generated from cli.tool.forge semantic conventions  
weavergen forge init my-registry --template enterprise
weavergen forge pipeline semantic.yaml --agents 5 --languages python,go
weavergen forge agents semantic.yaml --count 3
weavergen forge optimize --target single-binary
```

**Consolidates**:
- Current: `weavergen forge init`, `weavergen forge generate`, etc.
- New: Focused on advanced/pipeline operations

### 4. **otel** - OpenTelemetry Operations

```bash
# Generated from cli.tool.otel semantic conventions
weavergen otel spans --format mermaid --live
weavergen otel trace my-operation --detailed
weavergen otel metrics --component all
weavergen otel export --format jaeger
weavergen otel validate --compliance otel-1.27
```

**Consolidates**:
- Current: `weavergen debug spans`, scattered telemetry commands
- New: All OTel operations in one place

### 5. **mermaid** - Diagram Generation

```bash
# Generated from cli.tool.mermaid semantic conventions
weavergen mermaid workflow my-process --style sequence
weavergen mermaid spans --trace-id abc123
weavergen mermaid agents --count 5 --style communication
weavergen mermaid lifecycle semantic --component validation
weavergen mermaid architecture --full-system
```

**Consolidates**:
- Current: Visualization scattered across debug, bpmn, agents commands
- New: All Mermaid generation centralized

### 6. **agents** - AI Agent Operations

```bash
# Generated from cli.tool.agents semantic conventions
weavergen agents create semantic.yaml --count 5 --roles analyzer,validator
weavergen agents communicate --mode enhanced --rounds 10
weavergen agents validate semantic.yaml --deep
weavergen agents visualize --style hierarchy
```

**Consolidates**:
- Current: `weavergen agents communicate`, `weavergen forge-to-agents`
- New: Complete agent lifecycle under one tool

### 7. **xes** - Process Mining Operations

```bash
# Generated from cli.tool.xes semantic conventions
weavergen xes convert spans.json --output process.xes --filter-noise
weavergen xes discover process.xes --algorithm alpha --output-format bpmn
weavergen xes analyze process.xes --metrics performance,bottlenecks
weavergen xes conformance process.xes model.bpmn --method token-replay
weavergen xes visualize process.xes --viz-type process-map --interactive
weavergen xes predict model.pkl "Task_A,Task_B" --top-k 3
```

**Consolidates**:
- Current: `weavergen mining spans-to-xes`, `weavergen mining analyze-xes`, etc.
- New: Complete process mining pipeline under XES tool

## Example Generated Command: `workflow run`

From semantic convention:
```yaml
- id: cli.tool.workflow.run
  type: command
  brief: "Execute BPMN workflow"
  attributes:
    - id: name
      value: "run"
    - id: help
      value: "Execute a BPMN workflow with full telemetry"
    - id: arguments
      value:
        - name: "workflow"
          type: "str" 
          help: "Workflow name or file"
    - id: options
      value:
        - name: "data"
          type: "Optional[Path]"
          default: "null"
          short: "-d"
          help: "Input data file (JSON/YAML)"
```

Weaver generates:
```python
@workflow_app.command()
def run(
    workflow: str = typer.Argument(..., help="Workflow name or file"),
    data: Optional[Path] = typer.Option(None, "-d", help="Input data file (JSON/YAML)"),
    trace: bool = typer.Option(False, "-t", help="Enable execution tracing"),
    output: Optional[Path] = typer.Option(None, "-o", help="Output directory for results"),
) -> None:
    """Execute a BPMN workflow with full telemetry"""
    with tracer.start_as_current_span("workflow.run") as span:
        # Implementation injected from templates
        from ..engine.simple_engine import SimpleBpmnEngine
        # ... actual implementation
```

## Benefits of Weaver-Generated Tool Structure

1. **Eliminates Duplication**: No more workflow commands in 3 different places
2. **Semantic Source of Truth**: CLI structure defined in semantic conventions
3. **Consistent Patterns**: All tools follow same command patterns
4. **Auto-Generated Help**: Descriptions come from semantic conventions
5. **Built-in Telemetry**: Spans and metrics automatically instrumented
6. **Type Safety**: Generated with proper TypeScript/Python types

## User Mental Model Alignment

Users think:
- "I want to work with **workflows**" → `weavergen workflow`
- "I need to use **Weaver**" → `weavergen weaver`  
- "I want **OpenTelemetry** data" → `weavergen otel`
- "I need a **Mermaid** diagram" → `weavergen mermaid`

## Migration Strategy

1. **Generate new structure** alongside current CLI
2. **Add deprecation warnings** to old commands with new equivalents
3. **Provide migration guide** showing old → new mappings
4. **Remove old structure** in v3.0

## Command Comparison

| Current (Confusing) | New Tool-Based (Clear) |
|---------------------|-------------------------|
| `weavergen add --process MyProcess` | `weavergen workflow create MyProcess` |
| `weavergen run MyProcess` | `weavergen workflow run MyProcess` |
| `weavergen bpmn execute MyProcess` | `weavergen workflow run MyProcess` |
| `weavergen generate code semantic.yaml` | `weavergen weaver generate semantic.yaml` |
| `weavergen debug spans --format mermaid` | `weavergen mermaid spans` |
| `weavergen mining spans-to-xes spans.json` | `weavergen xes convert spans.json` |
| `weavergen mining analyze-xes process.xes` | `weavergen xes analyze process.xes` |
| `weavergen agents communicate` | `weavergen agents communicate` |

The tool-based structure makes WeaverGen v2 intuitive and eliminates the current confusion from having the same functionality scattered across multiple command groups.