# BPMN-First Architecture Visualization

## System Architecture

```mermaid
graph TB
    subgraph "BPMN Layer"
        B1[weavergen_orchestration.bpmn]
        B2[agent_generation.bpmn]
        B3[validation_generation.bpmn]
        B4[workflow_generation.bpmn]
    end
    
    subgraph "BPMN Engine"
        E1[BPMNFirstEngine]
        E2[Service Task Registry]
        E3[Execution Context]
        E4[Span Generator]
    end
    
    subgraph "Service Tasks"
        T1[LoadSemanticsTask]
        T2[ValidateSemanticsTask]
        T3[GenerateAgentRolesTask]
        T4[GenerateSpanValidatorTask]
        T5[GenerateHealthScoringTask]
    end
    
    subgraph "Generated System"
        G1[Agent System]
        G2[Validation Engine]
        G3[Workflow System]
        G4[Models]
    end
    
    subgraph "Observability"
        O1[OTel Spans]
        O2[Execution Reports]
        O3[Mermaid Traces]
        O4[Health Scores]
    end
    
    B1 --> E1
    B2 --> E1
    B3 --> E1
    
    E1 --> E2
    E2 --> T1
    E2 --> T2
    E2 --> T3
    E2 --> T4
    E2 --> T5
    
    T1 --> G1
    T2 --> G2
    T3 --> G1
    T4 --> G2
    T5 --> G2
    
    E1 --> E4
    E4 --> O1
    E4 --> O2
    E4 --> O3
    
    G2 --> O4
```

## BPMN Process Flow

```mermaid
graph LR
    Start((Start)) --> Load[Load Semantics]
    Load --> Validate[Validate]
    Validate --> Split{Parallel Split}
    
    Split --> A[Generate Agents]
    Split --> W[Generate Workflows]
    Split --> V[Generate Validation]
    Split --> M[Generate Models]
    
    A --> Join{Parallel Join}
    W --> Join
    V --> Join
    M --> Join
    
    Join --> Test[Integration Test]
    Test --> Check{All Pass?}
    
    Check -->|Yes| Report[Generate Report]
    Check -->|No| Fix[AI Fix Generation]
    
    Fix --> Apply[Apply Fixes]
    Apply --> Report
    
    Report --> End((End))
```

## Service Task Execution

```mermaid
sequenceDiagram
    participant BPMN as BPMN Process
    participant Engine as BPMN Engine
    participant Task as Service Task
    participant Span as OTel Span
    participant System as Generated System
    
    BPMN->>Engine: Execute Task
    Engine->>Task: Create Instance
    Task->>Span: Start Span
    activate Span
    
    Task->>Task: Load Context
    Task->>Task: Execute Logic
    Task->>System: Generate Code
    System-->>Task: Code Ready
    
    Task->>Span: Set Attributes
    Task->>Span: End Span
    deactivate Span
    
    Task-->>Engine: Return Result
    Engine-->>BPMN: Task Complete
```

## Span Hierarchy

```mermaid
graph TD
    R[bpmn.execute.WeaverGenOrchestration]
    R --> L[bpmn.load_semantics]
    R --> V[bpmn.validate_semantics]
    R --> AG[bpmn.execute.AgentGeneration]
    R --> VG[bpmn.execute.ValidationGeneration]
    
    AG --> EA[bpmn.extract_agent_semantics]
    AG --> GR[bpmn.generate_agent_roles]
    AG --> AC[bpmn.agent.create_classes]
    
    VG --> VS[bpmn.generate_span_validator]
    VG --> HS[bpmn.generate_health_scoring]
    
    style R fill:#f9f,stroke:#333,stroke-width:4px
    style AG fill:#bbf,stroke:#333,stroke-width:2px
    style VG fill:#bbf,stroke:#333,stroke-width:2px
```

## Data Flow

```mermaid
graph LR
    subgraph "Input"
        S[Semantic YAML]
    end
    
    subgraph "BPMN Processing"
        S --> P1[Parse & Validate]
        P1 --> P2[Extract Components]
        P2 --> P3[Generate Code]
        P3 --> P4[Add Instrumentation]
    end
    
    subgraph "Output"
        P4 --> A[agents/]
        P4 --> W[workflows/]
        P4 --> V[validation/]
        P4 --> M[models/]
    end
    
    subgraph "Validation"
        A --> T[Test Execution]
        W --> T
        V --> T
        M --> T
        T --> R[Report]
    end
```

## Key Innovations

1. **BPMN as Code**: Workflows are the source of truth
2. **Visual Programming**: Design workflows in BPMN editors
3. **Full Observability**: Every task generates spans
4. **Parallel Execution**: Built-in concurrent processing
5. **AI Integration**: Service tasks can use LLMs
6. **Self-Validating**: System validates its own generation

This architecture enables teams to:
- Design complex workflows visually
- Execute them with full observability
- Scale through parallel processing
- Debug with visual traces
- Maintain with standard BPMN tools