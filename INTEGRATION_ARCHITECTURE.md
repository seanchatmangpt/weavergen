# WeaverGen Integration Architecture

## Overview
Integration of prototype capabilities into main project with modular, extensible design.

## Architecture Principles

1. **Backward Compatibility** - Existing CLI commands remain unchanged
2. **Modular Design** - New features as separate, importable modules  
3. **OTel-First** - All operations instrumented with OpenTelemetry
4. **Type Safety** - Comprehensive Pydantic models throughout
5. **Async-Ready** - Built for concurrent operations

## Module Structure

```
src/weavergen/
├── __init__.py           # Main exports
├── cli.py               # Enhanced CLI with new subcommands
├── core.py              # Existing core functionality
├── models.py            # Existing base models
│
├── agents/              # AI Agent System
│   ├── __init__.py      # Agent exports
│   ├── base.py          # OTelAgent base class
│   ├── chair.py         # ChairAgent for meetings
│   ├── scrum.py         # ScrumMasterAgent
│   ├── dev.py           # DevTeamAgent
│   └── communication.py # OTel communication bus
│
├── meetings/            # Meeting Framework
│   ├── __init__.py      # Meeting exports
│   ├── base.py          # BaseMeeting interface
│   ├── roberts.py       # Roberts Rules implementation
│   ├── scrum.py         # Scrum of Scrums
│   └── dev.py           # Dev team meetings
│
├── models/              # Enhanced Data Models
│   ├── __init__.py      # Model exports
│   ├── parliament.py    # Roberts Rules models
│   ├── agents.py        # Agent communication models
│   ├── meetings.py      # Meeting state models
│   └── benchmarks.py    # Performance models
│
├── benchmarks/          # Performance Testing
│   ├── __init__.py      # Benchmark exports
│   ├── ollama.py        # LLM performance testing
│   ├── concurrent.py    # System concurrency tests
│   └── gpu.py           # GPU/Metal acceleration
│
├── quine/               # Semantic Quine System
│   ├── __init__.py      # Quine exports
│   ├── generator.py     # Self-generation logic
│   ├── validator.py     # Quine validation
│   └── demo.py          # Demonstration framework
│
└── otel/                # OpenTelemetry Utilities
    ├── __init__.py      # OTel exports
    ├── instrumentation.py # Enhanced instrumentation
    ├── spans.py         # Span utilities
    └── communication.py # Span-based messaging
```

## Integration Strategy

### Phase 1: Core Infrastructure
1. **OTel Utilities** - Enhanced instrumentation and span communication
2. **Base Models** - Parliament, agents, communication models
3. **Agent Framework** - OTelAgent base class and communication bus

### Phase 2: Meeting System
1. **Roberts Rules** - Parliamentary procedure implementation
2. **Meeting Framework** - Base meeting interface and specialized types
3. **Agent Specialization** - Chair, Scrum Master, Dev Team agents

### Phase 3: Advanced Features
1. **Benchmarking** - Ollama GPU testing and performance metrics
2. **Quine System** - Self-generation and validation
3. **CLI Enhancement** - New subcommand groups

### Phase 4: Integration & Testing
1. **Comprehensive Tests** - All integrated functionality
2. **Documentation** - Usage examples and API docs
3. **Performance Optimization** - Concurrent operation tuning

## Key Dependencies

```toml
[project]
dependencies = [
    "typer",           # Existing CLI framework
    "rich",            # Enhanced console interface  
    "pydantic",        # Data validation and models
    "opentelemetry-api",
    "opentelemetry-sdk",
    "opentelemetry-instrumentation",
    "aiohttp",         # Async HTTP for Ollama
    "pyyaml",          # YAML processing
]

[project.optional-dependencies]
ai = [
    "pydantic-ai",     # AI agent framework
    "ollama",          # LLM integration
]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
]
```

## CLI Command Structure

```
weavergen
├── generate           # Existing: Basic code generation
├── validate           # Existing: Registry validation
├── templates          # Existing: Template management  
├── config             # Existing: Configuration
│
├── agents             # NEW: Agent operations
│   ├── communicate    # Start agent communication
│   ├── analyze        # File analysis by agents
│   └── status         # Agent system status
│
├── meetings           # NEW: Meeting framework
│   ├── roberts        # Roberts Rules parliamentary
│   ├── scrum          # Scrum of Scrums
│   ├── dev            # Dev team with analysis
│   └── list           # List active meetings
│
├── benchmark          # NEW: Performance testing
│   ├── ollama         # LLM performance testing
│   ├── concurrent     # Concurrent operation testing
│   └── gpu            # GPU acceleration testing
│
└── demo               # NEW: Demonstrations
    ├── quine          # Semantic quine demo
    ├── full           # Full system demo
    └── validate       # Validation demos
```

## Integration Points

### 1. Enhanced Models
- Extend existing `models.py` with imports from new model modules
- Maintain backward compatibility for existing GenerationConfig, etc.
- Add comprehensive type hints throughout

### 2. CLI Extensions  
- Add new Typer sub-applications to existing CLI
- Preserve existing command behavior
- Add Rich console enhancements for progress and interaction

### 3. OTel Integration
- Enhance existing core.py with OTel instrumentation
- Add span-based communication throughout agent system
- Maintain performance while adding observability

### 4. Async Support
- Add async variants of existing synchronous operations
- Enable concurrent validation and generation
- Support multi-agent coordination

## Implementation Order

1. **OTel Utilities** (`src/weavergen/otel/`)
2. **Enhanced Models** (`src/weavergen/models/`) 
3. **Agent Framework** (`src/weavergen/agents/`)
4. **Meeting System** (`src/weavergen/meetings/`)
5. **CLI Enhancement** (`src/weavergen/cli.py`)
6. **Benchmarking** (`src/weavergen/benchmarks/`)
7. **Quine System** (`src/weavergen/quine/`)
8. **Integration Tests** (`tests/`)

This architecture provides a clean integration path that preserves existing functionality while adding the comprehensive prototype capabilities in a modular, maintainable way.