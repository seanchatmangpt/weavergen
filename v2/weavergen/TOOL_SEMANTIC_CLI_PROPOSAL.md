# WeaverGen v2 Tool-Based Semantic CLI Reorganization

## Core Principle: Tool/Concept-First Commands

Organize commands around the **core tools and concepts** that users think about:

```
weavergen <tool> <action> [options]
```

## Proposed Tool-Based Structure

### 1. **workflow** - BPMN Workflow Operations
```bash
weavergen workflow create <name>           # Create new workflow
weavergen workflow run <name>              # Execute workflow
weavergen workflow validate <file>         # Validate BPMN file
weavergen workflow list                    # List workflows
weavergen workflow debug <name>            # Debug workflow execution
weavergen workflow visualize <name>        # Generate Mermaid diagram
```

### 2. **weaver** - OTel Weaver Operations
```bash
weavergen weaver generate <semantic.yaml>  # Generate code via Weaver
weavergen weaver validate <semantic.yaml>  # Validate semantics
weavergen weaver templates                 # List Weaver templates
weavergen weaver install                   # Install/update Weaver binary
```

### 3. **forge** - Weaver Forge Advanced Operations
```bash
weavergen forge init <name>                # Initialize semantic registry
weavergen forge generate <semantic.yaml>   # Advanced generation
weavergen forge pipeline <semantic.yaml>   # Full forge pipeline
weavergen forge templates                  # Manage forge templates
```

### 4. **otel** - OpenTelemetry Operations
```bash
weavergen otel spans                       # View/analyze spans
weavergen otel trace <operation>          # Trace execution
weavergen otel export <format>            # Export telemetry data
weavergen otel metrics                    # View metrics
weavergen otel validate                   # Validate OTel compliance
```

### 5. **mermaid** - Diagram Generation
```bash
weavergen mermaid workflow <name>         # Workflow diagram
weavergen mermaid spans                   # Span flow diagram
weavergen mermaid agents                  # Agent communication diagram
weavergen mermaid lifecycle <component>   # Lifecycle diagrams
weavergen mermaid architecture            # System architecture
```

### 6. **agents** - AI Agent Operations
```bash
weavergen agents create <count>           # Create agent system
weavergen agents communicate              # Run agent communication
weavergen agents validate <semantic>      # AI-powered validation
weavergen agents visualize                # Visualize agent system
```

### 7. **semantic** - Semantic Convention Operations
```bash
weavergen semantic create <description>   # AI-generate semantics
weavergen semantic validate <file>        # Validate conventions
weavergen semantic enhance <file>         # AI-enhance existing
weavergen semantic merge <files...>       # Merge conventions
weavergen semantic convert <format>       # Convert formats
```

### 8. **spiff** - SpiffWorkflow Operations
```bash
weavergen spiff parse <bpmn>             # Parse BPMN file
weavergen spiff execute <workflow>       # Execute via SpiffWorkflow
weavergen spiff validate <bpmn>          # Validate BPMN structure
weavergen spiff serialize <instance>     # Serialize workflow state
```

### 9. **xes** - Process Mining Operations
```bash
weavergen xes convert <spans.json>       # Convert spans to XES
weavergen xes discover <xes>             # Discover process model
weavergen xes analyze <xes>              # Analyze event log patterns
weavergen xes conformance <xes> <model>  # Check conformance
weavergen xes visualize <xes>            # Create process visualizations  
weavergen xes predict <model> <prefix>   # Predict next activities
```

## Command Mapping from Current Structure

### Current → New Tool-Based

```bash
# Workflow operations
weavergen add → weavergen workflow add
weavergen run → weavergen workflow run
weavergen workflow list → weavergen workflow list
weavergen bpmn execute → weavergen workflow run

# Generation
weavergen generate code → weavergen weaver generate
weavergen forge generate → weavergen forge generate
weavergen semantic generate → weavergen semantic create

# Validation
weavergen validate semantic → weavergen semantic validate
weavergen forge validate → weavergen weaver validate
weavergen bpmn validate → weavergen workflow validate

# Visualization
weavergen debug spans → weavergen otel spans
weavergen bpmn visualize → weavergen mermaid workflow
weavergen agents visualize → weavergen mermaid agents

# Templates
weavergen templates list → weavergen weaver templates
weavergen forge templates → weavergen forge templates
```

## Benefits of Tool-Based Structure

1. **Mental Model Match**: Users think "I want to work with workflows" → `weavergen workflow`
2. **Tool Discovery**: `weavergen --help` shows all available tools
3. **Clear Ownership**: Each tool owns its commands
4. **No Duplication**: One tool, one responsibility
5. **Extensible**: Easy to add new tools or actions

## Example Usage Scenarios

### Scenario 1: Working with BPMN Workflows
```bash
# User thinks: "I need to work with workflows"
weavergen workflow create http-processing
weavergen workflow validate http-processing.bpmn
weavergen workflow run http-processing --trace
weavergen workflow debug http-processing --breakpoint Task_Validate
weavergen mermaid workflow http-processing > workflow.md
```

### Scenario 2: Using Weaver for Code Generation
```bash
# User thinks: "I need to use Weaver to generate code"
weavergen weaver validate semantic.yaml
weavergen weaver generate semantic.yaml --language python
weavergen weaver templates --language python
```

### Scenario 3: OpenTelemetry Operations
```bash
# User thinks: "I need to check my OTel spans"
weavergen otel spans --format table
weavergen otel trace my-operation
weavergen mermaid spans --last-trace > trace.md
weavergen otel export --format jaeger
```

### Scenario 4: Creating Visualizations
```bash
# User thinks: "I need a Mermaid diagram"
weavergen mermaid workflow my-process
weavergen mermaid agents --count 5
weavergen mermaid lifecycle semantic
weavergen mermaid architecture --full
```

## Implementation Strategy

### Phase 1: Create Tool Routers
```python
# Each tool gets its own command group
workflow_app = typer.Typer(help="BPMN workflow operations")
weaver_app = typer.Typer(help="OTel Weaver operations")
forge_app = typer.Typer(help="Weaver Forge operations")
otel_app = typer.Typer(help="OpenTelemetry operations")
mermaid_app = typer.Typer(help="Mermaid diagram generation")

# Register with main app
app.add_typer(workflow_app, name="workflow")
app.add_typer(weaver_app, name="weaver")
app.add_typer(forge_app, name="forge")
app.add_typer(otel_app, name="otel")
app.add_typer(mermaid_app, name="mermaid")
```

### Phase 2: Consolidate Duplicate Commands
- Move all workflow commands under `workflow`
- Move all span/trace commands under `otel`
- Move all diagram generation under `mermaid`
- Keep tool-specific commands with their tools

### Phase 3: Add Cross-Tool Integration
```bash
# Tools can reference each other
weavergen workflow run my-process --export-to otel
weavergen otel spans --visualize-with mermaid
weavergen forge generate --workflow custom-process
```

## Tool Semantic Principles

1. **Tool Identity**: Each command starts with the tool it operates on
2. **Action Clarity**: Second word is always the action (create, run, validate, etc.)
3. **Predictable Patterns**: All tools follow similar action patterns
4. **Tool Synergy**: Tools can work together but maintain clear boundaries
5. **User Intent**: Commands match how users think about the tools

This structure makes WeaverGen v2 intuitive by organizing around the actual tools and concepts users work with.