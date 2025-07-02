# Weaver Forge Maturity Matrix

This matrix defines the maturity levels for various aspects of the Weaver Forge project, from initial implementation to advanced, optimized states.

## 1. Code Generation Maturity

| Level | Description |
| :---- | :---------- |
| **Level 1: Basic Boilerplate** | Generates simple, functional code for core components (e.g., basic Pydantic models, minimal decorators). Limited customization. |
| **Level 2: Spec-Driven & Typed** | Code generation is fully driven by YAML/BPMN specs. Includes type-safe Pydantic models, basic CLI commands, and simple BPMN task stubs. |
| **Level 3: Comprehensive & Idiomatic** | Generates idiomatic code across all specified targets (Python, CLI, BPMN). Includes advanced features like enum generation, error handling, and context propagation. |
| **Level 4: Extensible & Self-Optimizing** | Supports custom templates, filters, and plugins. Generated code can be optimized based on runtime feedback (e.g., AI-assisted template evolution, live-reload). |

## 2. Observability (OpenTelemetry) Maturity

| Level | Description |
| :---- | :---------- |
| **Level 1: Basic Tracing** | Generates simple spans with basic attributes. Manual setup of `TracerProvider` and `ConsoleSpanExporter`. |
| **Level 2: Standardized Instrumentation** | Auto-generates `instrumentation.py` with OTLP exporter, Prometheus metrics, and basic logging integration. Spans include standard semantic conventions. |
| **Level 3: Advanced Observability** | Full "Three Pillars" (traces, metrics, logs) integration. Includes baggage propagation, resource detection, custom span processors, and advanced sampling. |
| **Level 4: Predictive & Adaptive** | Integrates distributed profiling. Telemetry-driven template suggestions and adaptive sampling based on real-time performance. |

## 3. CLI Generation Maturity

| Level | Description |
| :---- | :---------- |
| **Level 1: Basic Typer Commands** | Generates simple Typer commands with fixed arguments. Limited input validation. |
| **Level 2: Spec-Driven CLI** | CLI commands are fully defined by `cli_spec.yaml`. Includes Pydantic-based input validation, basic options, and arguments. |
| **Level 3: Robust & Instrumented CLI** | Generates comprehensive Typer CLIs with subcommands, enums, and default values. Each command is automatically instrumented with OpenTelemetry spans. |
| **Level 4: Workflow-Driven CLI** | CLI commands directly orchestrate BPMN workflows, passing arguments as process inputs. Full lifecycle instrumentation from CLI invocation to workflow completion. |

## 4. BPMN Workflow Integration Maturity

| Level | Description |
| :---- | :---------- |
| **Level 1: Basic Workflow Execution** | Generates simple SpiffWorkflow runners for basic BPMN files. Service tasks are minimal stubs. |
| **Level 2: Data-Driven Workflows** | BPMN processes define data objects, and generated runners include Pydantic models for process I/O. Service tasks are instrumented. |
| **Level 3: Advanced Task Management** | Generated service tasks include robust error handling, metrics, and context propagation. Supports complex BPMN constructs (e.g., multi-instance loops). |
| **Level 4: Dynamic & Self-Optimizing Workflows** | BPMN processes can be dynamically updated. Integration with external systems for task execution. Workflow optimization based on observed performance. |

## 5. Developer Experience Maturity

| Level | Description |
| :---- | :---------- |
| **Level 1: Manual Generation** | Developers manually run `weaver generate` after every spec/template change. |
| **Level 2: Automated Generation** | Integration with pre-commit hooks and CI/CD pipelines for automated code generation. |
| **Level 3: Enhanced Tooling** | Provides a Python wrapper CLI and API. Includes default templates and configurations for quick starts. |
| **Level 4: Intelligent & Interactive** | Features like live-reload, LSP integration (autocomplete, diagnostics), AI-assisted template evolution, and a blueprint diff tool. |

## 6. Maintainability & Governance Maturity

| Level | Description |
| :---- | :---------- |
| **Level 1: Basic Version Control** | Specs and templates are in version control. Generated code is committed. |
| **Level 2: Automated Sync & Testing** | Automated synchronization of semantic conventions. Comprehensive test harness for generated code. |
| **Level 3: Standardized Packaging** | Generated code adheres to Python packaging standards. Clear separation of concerns between specs, templates, and generated code. |
| **Level 4: Extensible Ecosystem** | Plugin architecture for custom filters/templates. Version compatibility checks between Weaver components. Clear documentation and examples. |
