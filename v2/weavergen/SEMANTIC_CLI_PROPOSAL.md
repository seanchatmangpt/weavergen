# WeaverGen v2 Semantic CLI Reorganization Proposal

## Current Problems

1. **Massive Duplication**:
   - Workflow management in: top-level (`add`, `run`, `delete-spec`), `workflow`, and `bpmn`
   - Validation in: `validate`, `forge validate`, `bpmn validate`, `workflow validate`
   - Generation in: `generate`, `forge generate`, `semantic generate`

2. **Mixed Paradigms**:
   - Action-based: `generate`, `validate`
   - Object-based: `workflow`, `agents`, `templates`
   - Tool-based: `forge`, `bpmn`

3. **Flat Structure**: No clear hierarchy or user journey

## Proposed Semantic Structure

Organize commands around **user intent** and **workflow stages**:

```
weavergen <stage> <target> [options]
```

### Command Structure

```yaml
weavergen:
  # Stage 1: Initialize and Setup
  init:
    project:      # Initialize new WeaverGen project
    registry:     # Initialize semantic convention registry  
    workflow:     # Initialize BPMN workflow templates

  # Stage 2: Define Resources
  define:
    semantic:     # Define semantic conventions (AI or manual)
      - from-description  # AI-powered generation
      - from-template     # Template-based
      - enhance          # AI enhancement of existing
    workflow:     # Define BPMN workflows
      - from-template
      - from-semantic   # Generate workflow from semantics
    agents:       # Define agent configurations
      - roles          # Define agent roles
      - communication  # Define communication patterns

  # Stage 3: Generate Artifacts
  create:
    code:         # Generate code from semantics
      - python
      - go
      - rust
      - all
    models:       # Generate data models
      - pydantic
      - protobuf
      - dataclass
    agents:       # Generate agent implementations
    docs:         # Generate documentation
    
  # Stage 4: Validate Everything
  check:
    semantic:     # Validate semantic conventions
    workflow:     # Validate BPMN workflows
    code:         # Validate generated code
    integration:  # End-to-end validation
    
  # Stage 5: Execute/Run
  run:
    workflow:     # Execute BPMN workflow
      - interactive
      - background
    pipeline:     # Execute full pipeline
    agents:       # Run agent system
    tests:        # Run validation tests
    
  # Stage 6: Analyze Results  
  analyze:
    spans:        # OpenTelemetry span analysis
      - trace
      - performance
      - errors
    process:      # Process mining
      - discover
      - conformance
    metrics:      # System metrics
    health:       # Health checks
    
  # Stage 7: Manage Resources
  list:
    workflows:    # List workflows
    semantics:    # List semantic conventions
    agents:       # List agent configurations
    all:          # List everything
    
  manage:
    clean:        # Cleanup resources
    export:       # Export configurations
    import:       # Import configurations
    config:       # Manage settings
```

### Example Usage Comparison

#### Old (Current) Structure:
```bash
# Confusing and duplicated
weavergen add --process MyProcess --bpmn workflow.bpmn
weavergen workflow add workflow.bpmn
weavergen bpmn execute MyProcess

weavergen generate code semantic.yaml
weavergen forge generate semantic.yaml
weavergen semantic generate "HTTP metrics"

weavergen validate semantic.yaml
weavergen forge validate semantic.yaml
```

#### New Semantic Structure:
```bash
# Clear progression through stages
weavergen init project my-telemetry          # Stage 1: Initialize
weavergen define semantic http-metrics.yaml  # Stage 2: Define
weavergen create code python                 # Stage 3: Generate
weavergen check semantic                     # Stage 4: Validate
weavergen run pipeline                       # Stage 5: Execute
weavergen analyze spans                      # Stage 6: Analyze

# Clear and intuitive
weavergen define semantic from-description "HTTP server metrics"
weavergen define workflow from-semantic http-metrics.yaml
weavergen create agents --count 3 --roles analyzer,validator,generator
weavergen run workflow http-processing --trace
weavergen analyze process discover --format mermaid
```

## Benefits of Semantic Structure

1. **User Journey Aligned**: Commands follow the natural progression of work
2. **Self-Documenting**: Command structure tells the story
3. **No Duplication**: Each action has one clear path
4. **Discoverable**: Users can explore by stage
5. **Consistent**: All commands follow `stage → target → action` pattern
6. **Extensible**: Easy to add new targets or actions within stages

## Implementation Strategy

### Phase 1: Create Semantic Router
```python
# New semantic_cli.py
@app.command()
def init(ctx: Context, target: str, name: str):
    """Initialize resources"""
    if target == "project":
        # Route to project initialization
    elif target == "registry":
        # Route to forge init
    elif target == "workflow":
        # Route to workflow template init
```

### Phase 2: Map Existing Commands
```python
COMMAND_MAPPING = {
    "init.registry": "forge.init",
    "define.semantic": "semantic.generate",
    "create.code": "generate.code",
    "check.semantic": "validate.semantic",
    "run.workflow": "bpmn.execute",
    "analyze.spans": "debug.spans",
}
```

### Phase 3: Gradual Migration
1. Keep existing commands but mark as deprecated
2. Add new semantic structure alongside
3. Show migration hints when old commands are used
4. Remove old structure in v3

## Semantic Command Principles

1. **Stages Before Objects**: `weavergen create code` not `weavergen code create`
2. **Intent Over Implementation**: `check` not `validate`, `create` not `generate`
3. **Progressive Disclosure**: Simple commands reveal more options with --help
4. **Contextual Help**: Each stage shows relevant next steps
5. **Smart Defaults**: Commands work with minimal options but allow full control

## Example: Full Workflow with Semantic Commands

```bash
# 1. Initialize a new project
weavergen init project my-telemetry
cd my-telemetry

# 2. Define semantic conventions (AI-powered)
weavergen define semantic from-description \
  "HTTP server with request duration and error tracking"

# 3. Define workflow from semantics
weavergen define workflow from-semantic http-server.yaml

# 4. Create all artifacts
weavergen create all --semantic http-server.yaml

# 5. Validate everything
weavergen check integration

# 6. Run the pipeline
weavergen run pipeline --trace

# 7. Analyze results
weavergen analyze spans --format mermaid
weavergen analyze health

# 8. View what was created
weavergen list all
```

This semantic structure makes WeaverGen v2 intuitive and follows the user's mental model rather than the technical implementation.