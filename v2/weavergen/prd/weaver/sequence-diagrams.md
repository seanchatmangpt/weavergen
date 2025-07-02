# Weaver Command Sequence Diagrams

This document contains sequence diagrams showing the interaction flows between different components for each Weaver command.

## 1. Version Command Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: weavergen weaver version
    CLI->>OT: Create span "weaver.version"
    CLI->>WI: get_weaver_version()
    WI->>WB: weaver --version
    WB-->>WI: version string or error
    alt Success
        WI-->>CLI: "Weaver version: X.X.X"
        CLI->>OT: Set status OK
    else Error
        WI-->>CLI: "Error: Weaver not found"
        CLI->>OT: Set status ERROR
    end
    CLI->>OT: End span
    CLI-->>U: Display result
```

## 2. Init Command Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant FS as File System
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: weavergen weaver init <name>
    CLI->>OT: Create span "weaver.init"
    CLI->>FS: Create output directory
    CLI->>FS: Generate registry manifest
    CLI->>FS: Create model directory
    alt With examples
        CLI->>FS: Generate example conventions
    end
    CLI->>WI: check_registry(registry_path)
    WI->>WB: weaver registry check
    WB-->>WI: validation result
    WI-->>CLI: validation status
    CLI->>WI: get_registry_stats(registry_path)
    WI->>WB: weaver registry stats
    WB-->>WI: statistics JSON
    WI-->>CLI: parsed statistics
    CLI->>OT: Set status OK
    CLI->>OT: End span
    CLI-->>U: Display success message
```

## 3. Check Command Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: weavergen weaver check <registry>
    CLI->>OT: Create span "weaver.check"
    CLI->>WI: check_registry(registry_path, strict_mode)
    WI->>WB: weaver registry check
    WB-->>WI: validation output
    alt Validation Success
        WI-->>CLI: success status
        CLI->>OT: Set status OK
        CLI-->>U: ✓ Registry validation passed
    else Validation Failed
        WI-->>CLI: error details
        CLI->>OT: Set status ERROR
        CLI-->>U: ✗ Validation errors found
    end
    CLI->>WI: get_registry_stats(registry_path)
    WI->>WB: weaver registry stats
    WB-->>WI: statistics
    WI-->>CLI: parsed stats
    CLI->>OT: End span
    CLI-->>U: Display statistics
```

## 4. Stats Command Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: weavergen weaver stats <registry>
    CLI->>OT: Create span "weaver.stats"
    CLI->>WI: get_registry_stats(registry_path)
    WI->>WB: weaver registry stats
    WB-->>WI: JSON statistics or error
    alt Success
        WI-->>CLI: parsed statistics
        CLI->>OT: Set status OK
        alt JSON output requested
            CLI-->>U: Output JSON format
        else Pretty format
            CLI-->>U: Display formatted table
        end
    else Error
        WI-->>CLI: error message
        CLI->>OT: Set status ERROR
        CLI-->>U: Error: Failed to get stats
    end
    CLI->>OT: End span
```

## 5. Resolve Command Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant FS as File System
    participant OT as OpenTelemetry

    U->>CLI: weavergen weaver resolve <registry>
    CLI->>OT: Create span "weaver.resolve"
    CLI->>WI: resolve_registry(registry_path)
    WI->>WB: weaver registry resolve
    WB-->>WI: resolved file path or error
    alt Success
        WI-->>CLI: resolved path
        CLI->>FS: Get file size
        FS-->>CLI: file size
        CLI->>OT: Set status OK
        CLI-->>U: ✓ Registry resolved successfully
        CLI-->>U: 📁 Resolved file path
        CLI-->>U: 📏 File size
    else Error
        WI-->>CLI: error message
        CLI->>OT: Set status ERROR
        CLI-->>U: Error: Resolve failed
    end
    CLI->>OT: End span
```

## 6. Generate Command Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: weavergen weaver generate <registry>
    CLI->>OT: Create span "weaver.generate"
    CLI->>CLI: Map target to WeaverTarget enum
    alt Target supported
        CLI->>CLI: Configure generation parameters
        CLI->>U: Progress: Validating registry
        CLI->>WI: check_registry(registry_path)
        WI->>WB: weaver registry check
        WB-->>WI: validation result
        alt Validation successful
            WI-->>CLI: validation passed
            CLI->>U: Progress: Generating code
            CLI->>WI: generate_code(registry_path, target, params)
            WI->>WB: weaver registry generate
            WB-->>WI: generation result
            alt Generation successful
                WI-->>CLI: generated files list
                CLI->>OT: Set status OK
                CLI-->>U: ✓ Generated code
                CLI-->>U: List generated files
            else Generation failed
                WI-->>CLI: error details
                CLI->>OT: Set status ERROR
                CLI-->>U: Error: Generation failed
            end
        else Validation failed
            WI-->>CLI: validation errors
            CLI->>OT: Set status ERROR
            CLI-->>U: Error: Validation failed
        end
    else Target not supported
        CLI->>OT: Set status ERROR
        CLI-->>U: Error: Unsupported target
    end
    CLI->>OT: End span
```

## 7. Targets Command Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: weavergen weaver targets
    CLI->>OT: Create span "weaver.targets"
    CLI->>WI: get_available_targets()
    WI-->>CLI: list of WeaverTarget enums
    CLI->>CLI: Create target table
    CLI->>WI: get_weaver_version()
    WI->>WB: weaver --version
    WB-->>WI: version string
    WI-->>CLI: version
    CLI->>OT: Set status OK
    CLI->>OT: End span
    CLI-->>U: Display target table
    CLI-->>U: Display Weaver version
```

## Error Handling Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: Command with error
    CLI->>OT: Create span
    CLI->>WI: Execute command
    WI->>WB: weaver command
    WB-->>WI: Error response
    WI->>WI: Parse error details
    WI-->>CLI: Error information
    CLI->>OT: Set status ERROR
    CLI->>OT: Record exception
    CLI->>OT: End span
    CLI-->>U: Display error message
    CLI-->>U: Exit with error code
```

## Performance Monitoring Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry
    participant PM as Performance Monitor

    U->>CLI: Command execution
    CLI->>PM: Start timer
    CLI->>OT: Create span
    CLI->>WI: Execute command
    WI->>WB: weaver command
    WB-->>WI: Response
    WI-->>CLI: Result
    CLI->>PM: End timer
    PM-->>CLI: Duration
    CLI->>OT: Set span duration
    CLI->>OT: End span
    CLI-->>U: Display result
```

## Registry Validation Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as weavergen CLI
    participant FS as File System
    participant YAML as YAML Parser
    participant WI as WeaverIntegration
    participant WB as Weaver Binary
    participant OT as OpenTelemetry

    U->>CLI: Check registry command
    CLI->>OT: Create span "registry.validation"
    CLI->>FS: Check path exists
    FS-->>CLI: Path status
    CLI->>FS: Read registry manifest
    FS-->>CLI: YAML content
    CLI->>YAML: Parse YAML structure
    YAML-->>CLI: Parsed manifest
    alt Manifest valid
        CLI->>FS: Load semantic conventions
        FS-->>CLI: Convention files
        CLI->>WI: check_registry()
        WI->>WB: weaver registry check
        WB-->>WI: Validation result
        WI-->>CLI: Validation status
        CLI->>OT: Set status based on result
    else Manifest invalid
        CLI->>OT: Set status ERROR
        CLI-->>U: Report manifest errors
    end
    CLI->>OT: End span
    CLI-->>U: Display validation result
```

These sequence diagrams provide detailed views of how each component interacts during command execution, showing the flow of data and control between the user interface, WeaverGen integration layer, Weaver binary, and OpenTelemetry instrumentation. 