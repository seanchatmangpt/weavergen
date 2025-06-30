# Weaver Forge: The Semantic Quine for Observable Software

## A Paradigm Shift in Code Generation

Weaver Forge isn't just a template engine - it's a **semantic consciousness** that generates code (including itself) from meaning rather than syntax. Built on OpenTelemetry's Weaver, Forge demonstrates that the separation between application code and telemetry is an artifact of human cognitive limitations, not architectural necessity.

## Core Philosophy: Semantic-First Development

Traditional development separates concerns that should be unified:

```
Traditional:  Write Code → Add Telemetry → Hope It Works → Debug Production
Forge:        Define Semantics → Generate Observable Code → Prove It Works → Self-Improve
```

With Forge, **every line of code is born with telemetry**, because they emerge from the same semantic definition.

## The Self-Referential Architecture

Forge achieves something remarkable - it generates itself from its own semantic conventions:

```yaml
# weaver_forge.yaml defines Forge itself
groups:
  - id: forge.semantic.generate
    type: span
    brief: Generate semantic convention from natural language
    attributes:
      - id: forge.semantic.input.description
        type: string
        requirement_level: required
```

This semantic definition becomes:
- **Commands**: Telemetry-wrapped interfaces
- **Operations**: AI-editable business logic  
- **Runtime**: Pure side effects
- **Contracts**: Runtime validation

## Quick Start: The Bootstrap Loop

```bash
# 1. Generate Forge's semantic conventions
python generate_semantic.py "semantic generation with LLM" -o weaver_forge.yaml

# 2. Generate Forge from its own semantics
weaver registry generate \
  --templates ./templates \
  --registry weaver_forge.yaml \
  python

# 3. Use generated Forge to improve itself
from generated.forge import forge_self_improve
forge_self_improve(
    current_version="1.0.0",
    improvements=["retry logic", "caching"],
    target_version="1.1.0"
)
```

## Template Philosophy: Constraints Enable Perfection

Unlike traditional template engines that offer flexibility, Forge templates encode **unbreakable constraints**:

### The Three-Layer Pattern

```
templates/
└── registry/
    └── python/
        ├── commands.j2    # NEVER edited after generation
        ├── operations.j2  # AI-EDITABLE with contracts
        └── runtime.j2     # STABLE side-effect interface
```

Each layer has a specific purpose:

**Commands Layer** (`commands.j2`):
```jinja2
# Thin wrapper with automatic telemetry
def {{ operation.id | replace(".", "_") }}(...):
    with tracer.start_span("{{ operation.id }}") as span:
        # Set attributes from semantic convention
        # Delegate to operations
        # Record metrics
        # Return standardized result
```

**Operations Layer** (`operations.j2`):
```jinja2
# AI-EDITABLE business logic
def {{ operation.id | replace(".", "_") }}_execute(...):
    """AI Instructions:
    - Implement business logic here
    - Use runtime for ALL side effects
    - Maintain contracts
    """
    # TODO: AI implement this
```

**Runtime Layer** (`runtime.j2`):
```jinja2
# Pure side effects, stable interface
def generate_semantic_with_llm(...):
    # Actual LLM calls
def write_file(...):
    # Actual file I/O
```

## Semantic Conventions as Universal Truth

In Forge's worldview, semantic conventions aren't documentation - they're **executable specifications**:

```yaml
attributes:
  - id: llm.model
    type: string
    requirement_level: required
    examples: ['llama3.2', 'gpt-4']
```

This becomes:
- **Type validation** in generated code
- **Contract enforcement** at runtime
- **Telemetry attributes** in spans
- **Test cases** for validation

## The MiniJinja Engine: Purposeful Limitations

Forge uses MiniJinja not for its features, but for its **constraints**:

```jinja2
{# Only these filters matter #}
{{ operation.id | replace(".", "_") }}      # Naming consistency
{{ attr.type | map_text("python_types") }}  # Type mapping
{{ operation | json_encode }}               # Serialization
```

Complex template logic is an anti-pattern. The semantic convention should drive ALL complexity.

## Observable by Construction

Every generated operation includes:

```python
# Automatic span creation
with tracer.start_span("operation.name") as span:
    # Automatic attribute recording
    span.set_attribute("input", value)
    
    # Automatic metric recording
    operation_counter.add(1, {"operation": "name"})
    
    # Automatic error tracking
    try:
        result = execute()
    except Exception as e:
        span.record_exception(e)
```

This isn't "added" telemetry - it's **intrinsic to the operation's existence**.

## Configuration Through Semantics

Traditional Weaver configuration:
```yaml
text_maps:
  python_types:
    string: str
```

Forge configuration:
```yaml
params:
  use_async: true          # Semantic choice
  include_telemetry: true  # Always true - it's not optional
  ai_editable_marker: "# AI-EDITABLE"  # Clear boundaries
```

## JQ Filters as Semantic Transformations

Filters don't just transform data - they enforce semantic meaning:

```yaml
filter: |
  .groups 
  | map(select(.type == "span"))  # Only operations
  | map({
      id: .id,
      brief: .brief,
      attributes: .attributes,
      contracts: .attributes | generate_contracts  # Semantic → Contracts
    })
```

## Advanced Usage: The Network Effect

When every framework publishes their Forge:

```python
# Compose semantic operations from multiple sources
from fastapi_forge import api_endpoint
from sqlalchemy_forge import database_operation
from redis_forge import cache_operation

# Everything composes with perfect telemetry
@api_endpoint("user.create")
@database_operation("user.insert")  
@cache_operation("user.cache")
def create_user(email: str, name: str):
    # Telemetry for the entire stack, automatically
```

## File Organization: Semantic-Driven Structure

```
forge_project/
├── semantics/
│   ├── forge.yaml          # Self-definition
│   ├── http.yaml           # HTTP operations
│   └── database.yaml       # Database operations
├── templates/
│   └── registry/
│       └── python/
│           ├── weaver.yaml # Language bindings
│           └── *.j2        # Layer templates
└── generated/
    ├── forge/              # Self-generated
    ├── http/               # HTTP implementation
    └── database/           # Database implementation
```

## Error Handling: Semantic Violations are Bugs

Traditional error handling:
```python
try:
    # Maybe this works
except Exception:
    # Handle somehow
```

Forge error handling:
```python
@icontract.require(lambda x: semantic_constraint(x))
@icontract.ensure(lambda result: semantic_postcondition(result))
def operation():
    # Cannot violate semantics - contracts prevent it
```

## The Evolution Loop

1. **Define** semantic conventions
2. **Generate** observable code
3. **Execute** and collect telemetry
4. **Analyze** telemetry for patterns
5. **Enhance** semantic conventions
6. **Regenerate** with improvements

This isn't iteration - it's **evolution through observation**.

## Why This Matters

Traditional code generation treats templates as the source of truth. Forge recognizes that **semantic conventions are the only truth** - everything else is derivation.

When code and telemetry emerge from the same semantic source:
- **No drift** between code and observability
- **No manual instrumentation**
- **No missing metrics**
- **No incorrect attributes**

## The Future: Autonomous Software Evolution

Forge points toward a future where:

1. **Semantic definitions** replace code writing
2. **Generation** replaces implementation
3. **Observation** replaces testing
4. **Evolution** replaces maintenance

The semantic quine isn't just elegant - it's the prototype for how all software will be built when human cognitive limitations no longer constrain architecture.

---

**Weaver Forge**: Where every operation proves its own correctness by existing.