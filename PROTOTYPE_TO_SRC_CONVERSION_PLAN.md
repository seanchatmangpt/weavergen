# Prototype to src/weavergen Conversion Plan

## Overview
This document outlines the plan to convert the prototype code in `./prototype/` to the production-ready structure in `./src/weavergen/`.

## Core Components to Migrate

### 1. Weaver CLI Wrapper (High Priority)
**Prototype Files:**
- `prototype/weaver_wrapper.py` - Core wrapper functionality
- `prototype/test_weaver_wrapper.py` - Tests

**Target:** `src/weavergen/core.py`

**Changes Needed:**
- Integrate WeaverWrapper methods into existing WeaverGen class
- Add methods for:
  - `registry_check()`
  - `registry_resolve()`
  - `registry_stats()`
  - Enhance existing `generate()` with prototype's robust parameter handling

### 2. Semantic Generation with LLMs (High Priority)
**Prototype Files:**
- `prototype/semantic-generator.py` - LLM-based semantic generation
- `prototype/forge_mvp.py` - MVP semantic generation logic

**Target:** New file `src/weavergen/semantic.py`

**Components:**
- SemanticGenerator class with async LLM support
- Pydantic models for semantic conventions
- Support for multiple LLM providers (Ollama, OpenAI, etc.)

### 3. 4-Layer Architecture Support (Medium Priority)
**Prototype Structure:**
- Commands Layer - OpenTelemetry instrumentation
- Operations Layer - Business logic
- Runtime Layer - External tool integration
- Contracts Layer - Runtime validation

**Target:** New module `src/weavergen/layers/`
```
src/weavergen/layers/
├── __init__.py
├── commands.py
├── operations.py
├── runtime.py
└── contracts.py
```

### 4. Enhanced Template System (Medium Priority)
**Prototype Files:**
- `prototype/templates/` - Template directory structure
- Registry templates with Jinja2 + JQ expressions

**Target:** `src/weavergen/templates/` (new directory)

**Features to Add:**
- Multi-language template support
- Template validation
- Custom template loading

### 5. Models Enhancement (High Priority)
**Prototype Models:**
- Semantic convention models (Group, Attribute, etc.)
- Forge-specific models
- Validation results

**Target:** `src/weavergen/models.py` (extend existing)

**New Models:**
```python
- SemanticConvention
- Group
- Attribute
- ForgeResult
- LayerConfig
```

### 6. CLI Enhancements (Low Priority)
**New Commands:**
- `weavergen semantic` - Generate semantic conventions
- `weavergen forge` - Run Forge operations
- `weavergen validate-otel` - Validate with OpenTelemetry

**Target:** `src/weavergen/cli.py` (extend existing)

## Migration Steps

### Phase 1: Core Infrastructure (Week 1)
1. **Extend models.py** with semantic convention models
2. **Enhance core.py** with prototype's WeaverWrapper methods
3. **Create semantic.py** for LLM-based generation
4. **Update tests** with prototype test cases

### Phase 2: Advanced Features (Week 2)
1. **Implement 4-layer architecture** in `layers/` module
2. **Migrate template system** with multi-language support
3. **Add OpenTelemetry integration** for validation
4. **Implement semantic quine functionality**

### Phase 3: Polish & Integration (Week 3)
1. **Update CLI** with new commands
2. **Add comprehensive tests** from prototype
3. **Documentation updates**
4. **Performance optimization**

## Key Features to Preserve

1. **Semantic Quine Capability**: System can regenerate itself from semantic conventions
2. **LLM Integration**: Support for multiple LLM providers for semantic generation
3. **4-Layer Architecture**: Clear separation of concerns
4. **OpenTelemetry Validation**: Built-in telemetry and validation
5. **Multi-Language Support**: Generate code for Python, Rust, Go, Java, JS

## Testing Strategy

### Unit Tests
- Migrate all prototype unit tests
- Add tests for new functionality
- Maintain 80%+ coverage

### Integration Tests
- Test full workflow: semantic generation → code generation → validation
- Test semantic quine capability
- Test multi-language generation

### Files to Create/Update

```
src/weavergen/
├── __init__.py          (update)
├── cli.py               (update - new commands)
├── core.py              (update - add wrapper methods)
├── models.py            (update - new models)
├── semantic.py          (new - LLM generation)
├── layers/              (new directory)
│   ├── __init__.py
│   ├── commands.py
│   ├── operations.py
│   ├── runtime.py
│   └── contracts.py
├── templates/           (new directory - from prototype)
└── validation.py        (new - OpenTelemetry validation)

tests/
├── test_core.py         (update)
├── test_semantic.py     (new)
├── test_layers.py       (new)
├── test_integration.py  (new)
└── test_validation.py   (new)
```

## Dependencies to Add

```toml
[project.optional-dependencies]
semantic = [
    "pydantic-ai>=0.1.0",
    "ollama>=0.1.0",
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
    "icontract>=2.6.0",
]
```

## Success Criteria

1. All prototype functionality available in production code
2. Backward compatibility maintained
3. Tests passing with 80%+ coverage
4. Semantic quine demonstration working
5. Multi-language generation functional
6. Performance improvements documented

## Next Steps

1. Start with Phase 1 - Core Infrastructure
2. Create feature branches for each component
3. Implement with comprehensive tests
4. Document changes in CHANGELOG.md