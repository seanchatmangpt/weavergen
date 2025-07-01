This Python file defines the Operations Layer for WeaverGen, implementing its 80/20 business logic.
It explicitly states that it uses span-based validation and no Pytests.
`GenerationOperation` handles the core code generation workflow, including preparation, execution, and post-processing.
It prepares the generation environment, validates inputs, and creates language-specific project structures (e.g., `setup.py` for Python, `Cargo.toml` for Rust, `go.mod` for Go).
`ValidationOperation` orchestrates comprehensive validation workflows, including syntax, pipeline, and integration validation.
It uses `SpanBasedValidator` for span-based validation and tracks validation history.
`WorkflowOrchestrator` coordinates complex end-to-end workflows, combining generation, validation, and optional optimization.
It includes a basic code optimization function that removes blank lines from Python files.
All operations are instrumented with OpenTelemetry spans for detailed tracing and analysis.
The module includes an `validate_operations_integration` function to test the integration of these operations, saving span data and results.
This file represents the core business logic and workflow management within WeaverGen, focusing on practical, span-validated functionality.