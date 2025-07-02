# GEMINI.md (Weavergen v2 Development Only)

This file provides guidance to Gemini Code when working with the Weavergen v2 codebase. It outlines the architecture, development patterns, and validation strategies specific to this version.

## Project Overview

Weavergen v2 is a Python wrapper around OpenTelemetry Weaver Forge, designed for declarative, convention-over-configuration code generation. It transforms YAML semantic convention definitions, CLI specifications, and BPMN workflow models into production-ready, fully-instrumented Python code. The core principle is to leverage Weaver Forge as the primary code generation engine, orchestrated by a consolidated `weavergen` CLI.

## Architecture Overview (Weavergen v2)

### Consolidated CLI
All CLI commands are consolidated under the single `weavergen` entry point. This includes:
-   **Code Generation**: `weavergen generate` (orchestrates Weaver Forge)
-   **BPMN Workflow Management**: `weavergen bpmn`
-   **Debugging and Validation**: `weavergen debug`
-   And all other project-specific commands.

### Weaver Forge Integration
-   **Declarative Configuration**: `weaver-forge.yaml` is the central configuration file. It defines parameters, JQ-style filters, and template mappings for all code generation tasks.
-   **Python Orchestration**: The `src/weavergen/cli.py` module directly handles the orchestration of the Weaver Rust CLI. It loads `weaver-forge.yaml` and manages the code generation process.
-   **Bundled Templates**: Jinja2 templates (e.g., `pydantic_model.j2`, `decorator.j2`, `instrumentation.j2`, `cli_model.j2`, `bpmn_model.j2`) are bundled within `src/weavergen/resources/templates/python/` along with a `default-forge.yaml`.
-   **JQ-style Filters**: Placeholder modules for custom JQ-style filters (`semconv_grouped_attributes`, `cli_commands`, `spiff_bpmn`) are located in `src/weavergen/filters/`. These filters process input specifications (OpenTelemetry semantic conventions, `cli_spec.yaml`, BPMN files) into a structured JSON context suitable for Jinja2 templates.

### Span-Based Validation (Primary Validation Strategy)
-   **No Unit Tests**: Validation of generated code and overall system behavior relies exclusively on OpenTelemetry spans. This is a core tenet of v2 development.
-   **Comprehensive Instrumentation**: All generated code (Pydantic models, CLI commands, BPMN service tasks, and core instrumentation setup) is automatically instrumented with detailed spans, attributes, and events.
-   **Telemetry-Driven Verification**: The `weavergen debug spans` command (or similar telemetry analysis tools) is the primary method for verifying correctness. It ensures that the generated code produces the expected and semantically correct telemetry.
-   **Lifecycle Observability**: Spans capture the entire lifecycle of operations, from the initial `weavergen` CLI invocation through BPMN workflow execution and individual service task completion, providing end-to-end visibility.

## Key Files and Directories
-   `src/weavergen/cli.py`: The consolidated main CLI application, incorporating Weaver Forge orchestration.
-   `src/weavergen/resources/templates/python/`: Contains bundled Jinja2 templates and `default-forge.yaml`.
-   `src/weavergen/filters/`: Placeholder modules for JQ-style filters.
-   `cli_spec.yaml`: Defines the structure and parameters of `weavergen` CLI commands.
-   `processes/`: Contains BPMN workflow definitions (`.bpmn` files).
-   `weaver-forge.yaml`: The central configuration file for Weaver Forge, defining generation parameters and template mappings.
-   `telemetry/`: (Generated) Python package containing OpenTelemetry instrumentation code (e.g., Pydantic attribute models, decorators, instrumentation setup).
-   `workflow_cli/`: (Generated) Python package containing the Typer CLI application and BPMN workflow runners.

## Development Guidelines

-   **CLI-First Philosophy**: All operations are executed via `uv run weavergen` commands. Direct execution of individual Python files is generally discouraged, except for specific debugging within `prototype/` if applicable.
-   **Span-Based Validation**: Always verify changes by analyzing OpenTelemetry spans. Do not rely on traditional unit tests for generated code.
-   **Declarative Changes**: Modify `weaver-forge.yaml`, `cli_spec.yaml`, or BPMN files to effect changes in generated code. Update Jinja templates for new code patterns.
-   **Convention over Configuration**: Adhere to the established patterns for filters, templates, and configuration to maintain consistency and reduce boilerplate.