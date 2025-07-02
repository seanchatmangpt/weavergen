# Weaver Command Diagrams

This document contains Mermaid diagrams for each Weaver command, showing their workflows, user interactions, and system components.

## 1. Version Command

```mermaid
flowchart TD
    A[User: weavergen weaver version] --> B[CLI: Parse command]
    B --> C[WeaverIntegration: get_weaver_version]
    C --> D[Subprocess: weaver --version]
    D --> E{Weaver Binary Available?}
    E -->|Yes| F[Return version string]
    E -->|No| G[Error: Weaver not found]
    F --> H[Display: Weaver version: X.X.X]
    G --> I[Error: Install with cargo install weaver-forge]
    H --> J[OpenTelemetry: Record span]
    I --> J
    J --> K[End]
```

## 2. Init Command

```mermaid
flowchart TD
    A[User: weavergen weaver init <name>] --> B[CLI: Parse arguments]
    B --> C[Create output directory]
    C --> D[Generate registry manifest]
    D --> E[Create model directory]
    E --> F{With examples?}
    F -->|Yes| G[Generate example semantic conventions]
    F -->|No| H[Skip example generation]
    G --> I[WeaverIntegration: check_registry]
    H --> I
    I --> J[Subprocess: weaver registry check]
    J --> K{Registry valid?}
    K -->|Yes| L[Display: Registry validation passed]
    K -->|No| M[Display: Validation warnings]
    L --> N[WeaverIntegration: get_registry_stats]
    M --> N
    N --> O[Display: Registry statistics]
    O --> P[Display: Success message]
    P --> Q[OpenTelemetry: Record span]
    Q --> R[End]
```

## 3. Check Command

```mermaid
flowchart TD
    A[User: weavergen weaver check <registry>] --> B[CLI: Parse arguments]
    B --> C[Configure validation mode]
    C --> D[WeaverIntegration: check_registry]
    D --> E[Subprocess: weaver registry check]
    E --> F{Validation successful?}
    F -->|Yes| G[Display: ✓ Registry validation passed]
    F -->|No| H[Parse error output]
    G --> I{Show warnings?}
    H --> J[Display: ✗ Validation errors found]
    I -->|Yes| K[Display warnings]
    I -->|No| L[Skip warnings]
    J --> M[Display error details]
    K --> N[WeaverIntegration: get_registry_stats]
    L --> N
    M --> N
    N --> O[Display registry statistics]
    O --> P[OpenTelemetry: Record span]
    P --> Q[End]
```

## 4. Stats Command

```mermaid
flowchart TD
    A[User: weavergen weaver stats <registry>] --> B[CLI: Parse arguments]
    B --> C[WeaverIntegration: get_registry_stats]
    C --> D[Subprocess: weaver registry stats]
    D --> E{Stats successful?}
    E -->|Yes| F[Parse JSON output]
    E -->|No| G[Error: Failed to get stats]
    F --> H{JSON output requested?}
    G --> I[Display error message]
    H -->|Yes| J[Output JSON format]
    H -->|No| K[Display pretty format]
    J --> L[Show: groups, attributes, metrics, spans, resources]
    K --> L
    I --> M[Exit with error]
    L --> N[Display detailed statistics]
    N --> O[OpenTelemetry: Record span]
    O --> P[End]
```

## 5. Resolve Command

```mermaid
flowchart TD
    A[User: weavergen weaver resolve <registry>] --> B[CLI: Parse arguments]
    B --> C[WeaverIntegration: resolve_registry]
    C --> D[Subprocess: weaver registry resolve]
    D --> E{Resolve successful?}
    E -->|Yes| F[Get resolved file path]
    E -->|No| G[Error: Resolve failed]
    F --> H[Display: ✓ Registry resolved successfully]
    G --> I[Display error message]
    H --> J[Display: 📁 Resolved file path]
    I --> K[Exit with error]
    J --> L[Calculate file size]
    L --> M[Display: 📏 File size]
    M --> N[OpenTelemetry: Record span]
    N --> O[End]
```

## 6. Generate Command

```mermaid
flowchart TD
    A[User: weavergen weaver generate <registry>] --> B[CLI: Parse arguments]
    B --> C[Map target to WeaverTarget enum]
    C --> D{Target supported?}
    D -->|No| E[Error: Unsupported target]
    D -->|Yes| F[Parse template parameters]
    E --> G[Display supported targets]
    F --> H[Configure Weaver settings]
    G --> I[Exit with error]
    H --> I[Progress: Validating registry]
    I --> J[WeaverIntegration: check_registry]
    J --> K{Validation successful?}
    K -->|No| L[Error: Validation failed]
    K -->|Yes| M[Progress: Generating code]
    L --> N[Display validation errors]
    M --> O[WeaverIntegration: generate_code]
    N --> P[Exit with error]
    O --> Q[Subprocess: weaver registry generate]
    Q --> R{Generation successful?}
    R -->|Yes| S[Display: ✓ Generated code]
    R -->|No| T[Error: Generation failed]
    S --> U[List generated files]
    T --> V[Display error details]
    U --> W[Display diagnostics]
    V --> X[Exit with error]
    W --> Y[OpenTelemetry: Record span]
    Y --> Z[End]
```

## 7. Targets Command

```mermaid
flowchart TD
    A[User: weavergen weaver targets] --> B[CLI: Parse command]
    B --> C[WeaverIntegration: get_available_targets]
    C --> D[Get list of WeaverTarget enums]
    D --> E[Create table structure]
    E --> F[Format target descriptions]
    F --> G[Display: Available Weaver Targets]
    G --> H[Show target table]
    H --> I[Get Weaver version]
    I --> J[Display: Weaver version]
    J --> K[OpenTelemetry: Record span]
    K --> L[End]
```

## System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface"
        A[weavergen CLI]
        B[Rich Console]
        C[Progress Indicators]
    end
    
    subgraph "WeaverGen Integration"
        D[WeaverIntegration Class]
        E[OpenTelemetry Spans]
        F[Error Handling]
    end
    
    subgraph "External Systems"
        G[Weaver Binary]
        H[File System]
        I[Registry Files]
    end
    
    A --> D
    B --> A
    C --> A
    D --> G
    D --> H
    D --> E
    D --> F
    G --> I
    H --> I
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Command Execution] --> B{Weaver Binary Available?}
    B -->|No| C[Installation Error]
    B -->|Yes| D[Execute Weaver Command]
    C --> E[Display: Install with cargo install weaver-forge]
    D --> F{Command Successful?}
    F -->|Yes| G[Parse Success Output]
    F -->|No| H[Parse Error Output]
    G --> I[Display Success Message]
    H --> J[Parse Error Details]
    I --> K[Record Success Span]
    J --> L[Display Error Message]
    K --> M[End Successfully]
    L --> N[Record Error Span]
    N --> O[Exit with Error Code]
```

## OpenTelemetry Instrumentation

```mermaid
flowchart TD
    A[Command Start] --> B[Create Root Span]
    B --> C[Set Span Attributes]
    C --> D[Execute Weaver Command]
    D --> E{Command Result}
    E -->|Success| F[Set Status: OK]
    E -->|Error| G[Set Status: ERROR]
    F --> H[Add Success Events]
    G --> I[Record Exception]
    H --> J[Set Span Duration]
    I --> J
    J --> K[End Span]
    K --> L[Export to Console]
```

## Registry Validation Flow

```mermaid
flowchart TD
    A[Registry Path] --> B[Validate Path Exists]
    B --> C[Check Registry Manifest]
    C --> D[Parse YAML Structure]
    D --> E{Manifest Valid?}
    E -->|No| F[Report Manifest Errors]
    E -->|Yes| G[Load Semantic Conventions]
    F --> H[Exit with Error]
    G --> I[Validate Convention Files]
    I --> J{Conventions Valid?}
    J -->|No| K[Report Convention Errors]
    J -->|Yes| L[Run Weaver Validation]
    K --> M[Exit with Error]
    L --> N{Weaver Validation Passed?}
    N -->|No| O[Report Weaver Errors]
    N -->|Yes| P[Registry Valid]
    O --> Q[Exit with Error]
    P --> R[Success]
```

## Code Generation Flow

```mermaid
flowchart TD
    A[Registry Input] --> B[Validate Registry]
    B --> C{Registry Valid?}
    C -->|No| D[Validation Error]
    C -->|Yes| E[Select Target Language]
    D --> M[Exit with Error]
    E --> F[Configure Templates]
    F --> G[Set Generation Parameters]
    G --> H[Execute Weaver Generate]
    H --> I{Generation Successful?}
    I -->|No| J[Generation Error]
    I -->|Yes| K[Collect Generated Files]
    J --> L[Display Error Details]
    K --> N[List Generated Files]
    L --> M
    N --> O[Display Statistics]
    O --> P[Success]
```

## Performance Monitoring

```mermaid
flowchart TD
    A[Command Start] --> B[Start Timer]
    B --> C[Execute Command]
    C --> D[End Timer]
    D --> E[Calculate Duration]
    E --> F{Within Limits?}
    F -->|Yes| G[Record Normal Performance]
    F -->|No| H[Record Performance Warning]
    G --> I[Continue Execution]
    H --> I
    I --> J[Log Performance Metrics]
    J --> K[End]
```

These diagrams provide a comprehensive view of how each Weaver command operates, their error handling strategies, and their integration with the broader WeaverGen ecosystem. 