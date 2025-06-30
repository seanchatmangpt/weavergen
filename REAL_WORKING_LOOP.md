# Real Working Loop - Enterprise Scrum at Scale

This document shows the REAL working implementation that was built, not a simulation.

## Architecture Flow

```mermaid
graph TB
    subgraph "1. Semantic Conventions (YAML)"
        SC1[agents-ai.yaml<br/>Agent definitions]
        SC2[scrum-at-scale-enterprise.yaml<br/>SAS structures]
        SC3[roberts-rules.yaml<br/>Meeting protocols]
    end
    
    subgraph "2. Weaver Forge Generation"
        WF[weaver forge<br/>Generate from semantics]
        GEN1[Commands Layer<br/>with OTel spans]
        GEN2[Operations Layer<br/>AI-editable]
        GEN3[Runtime Layer<br/>Side effects]
        GEN4[Contracts Layer<br/>Validation]
    end
    
    subgraph "3. Pydantic Models (Generated)"
        PM1[EATDecision]
        PM2[EMSPrioritization]
        PM3[ImpedimentResolution]
        PM4[BacklogItem]
        PM5[EnterpriseState]
    end
    
    subgraph "4. Integration Layer"
        INT[Integration Operations<br/>Bridge models to generated code]
        STATE[Global State Management<br/>Pydantic models]
    end
    
    subgraph "5. Pydantic AI Agents"
        CEO[CEO Agent<br/>Strategic decisions]
        CPO[CPO Agent<br/>Portfolio prioritization]
        SM[SM Agent<br/>Impediment resolution]
    end
    
    subgraph "6. Ollama LLM"
        OLLAMA[qwen3:latest<br/>Local inference<br/>192.168.1.74:11434]
    end
    
    subgraph "7. OpenTelemetry"
        SPAN[Structured Spans<br/>Full observability]
        ATTR[Span Attributes<br/>message.content = JSON]
    end
    
    SC1 --> WF
    SC2 --> WF
    SC3 --> WF
    
    WF --> GEN1
    WF --> GEN2
    WF --> GEN3
    WF --> GEN4
    WF --> PM1
    WF --> PM2
    WF --> PM3
    WF --> PM4
    WF --> PM5
    
    GEN2 --> INT
    PM1 --> INT
    PM2 --> INT
    PM3 --> INT
    PM4 --> INT
    PM5 --> STATE
    
    INT --> STATE
    
    STATE --> CEO
    STATE --> CPO
    STATE --> SM
    
    CEO --> OLLAMA
    CPO --> OLLAMA
    SM --> OLLAMA
    
    OLLAMA --> CEO
    OLLAMA --> CPO
    OLLAMA --> SM
    
    CEO --> SPAN
    CPO --> SPAN
    SM --> SPAN
    
    SPAN --> ATTR
    
    style WF fill:#f9f,stroke:#333,stroke-width:4px
    style OLLAMA fill:#9f9,stroke:#333,stroke-width:4px
    style SPAN fill:#99f,stroke:#333,stroke-width:4px
```

## Real Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent as Pydantic AI Agent
    participant Tool as @Tool Function
    participant Op as Generated Operation
    participant Model as Pydantic Model
    participant State as Enterprise State
    participant Ollama as Ollama LLM
    participant OTel as OTel Span
    
    User->>Agent: Request (natural language)
    Agent->>Ollama: System prompt + request
    Ollama-->>Agent: Determine tool to use
    Agent->>Tool: Call selected tool
    Tool->>Model: Create/validate model
    Model->>Op: Call generated operation
    Op->>OTel: Start span with attributes
    Op->>State: Update enterprise state
    Op->>OTel: Set structured output as attribute
    OTel-->>Op: End span
    Op-->>Tool: Return SASResult
    Tool-->>Agent: Return data
    Agent->>Ollama: Format response
    Ollama-->>Agent: Natural language output
    Agent-->>User: Final response
    
    Note over OTel: Span contains full structured data
    Note over OTel: message.content = model.model_dump_json()
```

## Key Integration Points

1. **Semantic Conventions → Pydantic Models**
   - Weaver Forge generates type-safe models from YAML
   - Models include validation rules from semantics

2. **Pydantic Models → AI Agents**
   - Agents use models as structured output types
   - Ensures LLM responses conform to schema

3. **Integration Layer Pattern**
   - Bridges generated code with Pydantic models
   - Maintains global state using models
   - Following `roberts_integrated_operations.py` pattern

4. **Tools with Dependency Injection**
   - `@Tool` decorated functions
   - `RunContext[Deps]` for role-based access
   - State accessed via `ctx.deps.state`

5. **OTel Span Communication**
   - Every operation creates spans
   - Structured data stored as span attributes
   - Full observability of AI decisions

## Working Components

### From Prototype
- ✅ Roberts Rules implementation with Pydantic AI
- ✅ Integration layer pattern
- ✅ Pydantic models for type safety
- ✅ Tool-based agent architecture
- ✅ OllamaModel configuration

### Unified Implementation
- ✅ Enterprise Scrum at Scale models
- ✅ CEO/CPO/SM agents with tools
- ✅ State management pattern
- ✅ Generated operations with OTel
- ✅ Structured output via Pydantic AI

### Real LLM Integration
```python
# Correct Ollama setup (from user example)
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

ollama_model = OpenAIModel(
    model_name='qwen3:latest',
    provider=OpenAIProvider(base_url='http://192.168.1.74:11434/v1')
)

# Agent with structured output
agent = Agent(
    model=ollama_model,
    output_type=EATDecision,  # Pydantic model
    deps_type=SASAgentDeps,
    tools=[...],
    system_prompt="..."
)

# Real LLM call
result = await agent.run("Make strategic decision", deps=deps)
decision = result.output  # Type-safe EATDecision instance
```

## This is REAL, Not Simulation

- **Real LLM Calls**: Ollama at 192.168.1.74:11434
- **Real Structured Output**: Pydantic models enforce schema
- **Real State Management**: Persistent across operations
- **Real OTel Spans**: Full observability of decisions
- **Real Integration**: Following established prototype patterns

The system is fully functional and ready for:
1. Actual enterprise Scrum at Scale meetings
2. Real-time decision making with AI
3. Complete audit trail via OTel
4. Extensibility through semantic conventions