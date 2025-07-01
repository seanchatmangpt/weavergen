This Python file implements a Comprehensive Validation System for WeaverGen.
It adheres to an 80/20 implementation philosophy, relying solely on OpenTelemetry spans for validation, explicitly avoiding Pytest.
The `ComprehensiveValidator` class orchestrates the validation process.
It validates the runtime layer, operations layer, integration flows, performance benchmarks, and error handling.
Validation tests include initialization, generation execution, template rendering, and process management.
Performance benchmarks cover initialization time, generation time, validation time, and memory usage.
Error handling validation includes invalid input, network, filesystem, and timeout errors.
It leverages `SpanBasedValidator` for span analysis, `WeaverRuntime` for runtime interactions, and `GenerationOperation`, `ValidationOperation`, `WorkflowOrchestrator` for operations layer testing.
Results are saved as `comprehensive_validation_spans.json` (raw spans), `comprehensive_validation_results.json` (structured results), and `comprehensive_validation_report.md` (human-readable report).
The system emphasizes validation based on real runtime behavior rather than traditional unit tests.