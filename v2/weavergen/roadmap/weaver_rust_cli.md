# Weaver Rust CLI: The High-Performance Code Generation Engine

Weavergen strategically leverages the OpenTelemetry Weaver Rust CLI as its foundational, high-performance code generation engine. Our approach is a prime example of "convention over configuration" and "dogfooding," where Weavergen orchestrates this powerful binary through its own generated Python wrapper.

### Core Capabilities Provided by Weaver Rust CLI:

-   **⚡ High-Performance Semantic Processing:** The Rust CLI excels at rapidly parsing and processing complex OpenTelemetry semantic convention definitions, ensuring efficiency and scalability.

-   **✅ Robust YAML Parsing and Validation:** It handles the intricate details of YAML schema validation and data extraction, offloading this complexity from Weavergen's Python layer.

-   **🌍 Multi-Language Code Generation:** The Rust CLI provides the underlying capability to generate code across various programming languages, which Weavergen then orchestrates for specific targets like Python.

-   **⚙️ Advanced Template Rendering (Tera):** It utilizes Tera (a Jinja2-like templating engine for Rust) for efficient and flexible code rendering, driven by the `weaver-forge.yaml` configuration.

-   **💯 OTel Compliance and Updates:** By relying on the official Weaver Rust CLI, Weavergen inherently benefits from its adherence to OpenTelemetry specifications and continuous updates, ensuring generated code is always compliant.

### Weavergen's Strategic Investment & Benefit:

-   **Our Investment:** 0% in reimplementing core code generation logic. We strategically integrate and orchestrate the existing, highly optimized Rust binary.
-   **Our Benefit:** 100% reliable, high-performance semantic processing and code generation. This allows Weavergen to focus its development efforts on higher-value orchestration, advanced features, and a superior developer experience, rather than duplicating complex infrastructure.

### Integration within Weavergen's Architecture:

Weavergen's Python wrapper (`weavergen.cli_wrapper`) acts as the intelligent orchestrator, dynamically constructing and executing Weaver Rust CLI commands based on the `weaver-forge.yaml` configuration. This ensures that all code generation, from Pydantic models to OpenTelemetry instrumentation and CLI scaffolding, is driven declaratively from a single source of truth, without direct manual interaction with the Rust binary.
