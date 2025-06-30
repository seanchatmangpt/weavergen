# Weaver Forge: Self-Referential Semantic Code Generation

Weaver Forge is a self-referential code generator that uses LLMs to generate OpenTelemetry semantic conventions and then generates code (including itself) from those conventions.

## 🚀 Quick Start

### Prerequisites

1. **Install Weaver CLI**:
   ```bash
   # Install from OpenTelemetry Weaver releases
   # See: https://github.com/open-telemetry/weaver/releases
   ```

2. **Install Python dependencies**:
   ```bash
   pip install typer pydantic pydantic-ai aiofiles pyyaml icontract
   ```

3. **Install Ollama** (for local LLM):
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull a model
   ollama pull llama3.2
   ```

### Bootstrap Weaver Forge

1. **Generate initial semantic convention**:
   ```bash
   python generate_semantic.py "semantic convention generation from natural language" -o weaver_forge.yaml
   ```

2. **Bootstrap Forge from its own semantics**:
   ```bash
   python bootstrap_forge.py
   ```

3. **Verify generation**:
   ```bash
   ls generated/forge/
   # Should see: commands/ operations/ runtime/ contracts/
   ```

## 📁 Project Structure

```
weaver-forge/
├── weaver_forge.yaml              # Semantic conventions for Forge itself
├── generate_semantic.py           # Initial LLM-based generator
├── bootstrap_forge.py             # Bootstrap script
├── templates/
│   └── registry/
│       └── python/
│           ├── weaver.yaml        # Weaver configuration
│           ├── commands.j2        # Commands layer template
│           ├── operations.j2      # Operations layer template
│           ├── runtime.j2         # Runtime layer template
│           └── contracts.j2       # Contracts layer template
└── generated/
    └── forge/                     # Generated Forge code
        ├── commands/              # Thin interface with telemetry
        ├── operations/            # AI-editable business logic
        ├── runtime/               # Side effects
        └── contracts/             # icontract validations
```

## 🔄 The Self-Referential Loop

### 1. Generate Semantic Conventions

```python
from generated.forge import forge_semantic_generate

# Generate any semantic convention
result = forge_semantic_generate(
    input_description="HTTP server request handling with metrics",
    output_path="http_server.yaml",
    llm_model="llama3.2",
    validation_status="pending"
)
```

### 2. Generate Code from Semantics

```python
from generated.forge import forge_code_generate

# Generate code from semantic conventions
result = forge_code_generate(
    input_semantic_path="http_server.yaml",
    target_language="python",
    template_directory="./templates",
    output_directory="./generated/http_server"
)
```

### 3. Self-Improvement

```python
from generated.forge import forge_self_improve

# Forge improves itself
result = forge_self_improve(
    current_version="1.0.0",
    improvements=["retry logic", "caching", "async support"],
    reference_depth=0,
    target_version="1.1.0"
)
```

## 🏗️ Architecture

### Three-Layer Pattern

1. **Commands Layer** (`commands/`):
   - Thin interface wrappers
   - Automatic telemetry (traces, metrics)
   - Input validation
   - Never edited after generation

2. **Operations Layer** (`operations/`):
   - Business logic implementation
   - AI-editable with clear boundaries
   - Calls runtime for side effects
   - Must satisfy contracts

3. **Runtime Layer** (`runtime/`):
   - All side effects (file I/O, LLM calls, subprocess)
   - Stable interfaces
   - Never imports from commands
   - Provides pure functions

### Contract Enforcement

Every operation has icontract-based validation:

```python
@icontract.require(lambda input_description: len(input_description) > 0)
@icontract.ensure(lambda result: result.success or result.errors)
def forge_semantic_generate_execute(...):
    # AI implements logic here
```

## 🤖 AI Development Workflow

### Editing Operations

AI systems (like Claude) can safely edit files in `operations/` following these rules:

1. **Never change function signatures**
2. **Always use runtime layer for side effects**
3. **Maintain contract compliance**
4. **Add features, validation, retry logic as needed**

Example AI instruction:
```
Improve operations/forge.py:
- Add retry logic for LLM calls
- Implement caching for repeated generations
- Add progress reporting
```

## 📊 Telemetry Integration

Every operation automatically generates:

- **Traces**: Operation duration, attributes, success/failure
- **Metrics**: Operation counts, error rates, duration histograms
- **Structured Logs**: Via span events and attributes

Access telemetry:
```python
# Traces appear in your configured OpenTelemetry backend
# Metrics available at configured metrics endpoint
```

## 🔧 Customization

### Add New Operations

1. **Update semantic convention**:
   ```yaml
   # Add to weaver_forge.yaml
   - id: forge.custom.operation
     type: span
     brief: 'My custom operation'
     attributes:
       - id: forge.custom.parameter
         type: string
         requirement_level: required
   ```

2. **Regenerate code**:
   ```bash
   weaver registry generate \
     --templates ./templates \
     --registry weaver_forge.yaml \
     python
   ```

3. **Implement in operations layer**

### Create New Language Targets

1. Create templates in `templates/registry/<language>/`
2. Add language-specific `weaver.yaml` configuration
3. Generate using: `weaver registry generate <language>`

## 🧪 Testing

```bash
# Test semantic generation
python generate_semantic.py "test operation" -o test.yaml

# Validate semantics
weaver registry check -r test.yaml

# Test code generation
weaver registry generate --templates ./templates python
```

## 🎯 Philosophy

Weaver Forge demonstrates that:

1. **Semantic conventions define everything** - structure, validation, telemetry
2. **Code generation enables perfection** - no human errors, complete consistency
3. **Self-reference is powerful** - systems that can generate and improve themselves
4. **Constraints enable AI** - clear boundaries make AI assistance reliable

## 📚 Examples

### Generate Database Semantics
```bash
python generate_semantic.py \
  "database query operations with connection pooling and prepared statements" \
  -o database.yaml
```

### Generate Microservice
```bash
# Generate semantics for a complete service
python generate_semantic.py \
  "user authentication service with login, logout, refresh tokens, and MFA" \
  -o auth_service.yaml

# Generate implementation
weaver registry generate \
  --templates ./templates \
  --registry auth_service.yaml \
  python
```

## 🚀 Future: The Network Effect

When every framework publishes their Weaver Forge:

```python
# Compose from multiple forges
from fastapi_forge import api_endpoint
from sqlalchemy_forge import database_operation  
from redis_forge import cache_operation
from openai_forge import llm_operation

# Everything integrates perfectly with automatic telemetry
```

Software development becomes semantic composition rather than code writing.

---

**The future of software**: Semantically-aware, self-generating, continuously-validating systems that prove their own correctness through observable behavior.