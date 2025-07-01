This Python file defines the command-line interface (CLI) for WeaverGen using `typer`.
It orchestrates various functionalities including semantic generation, validation, AI agent operations, meetings, benchmarking, demonstrations, conversation systems, debugging, SpiffWorkflow integration, and process mining.
Key commands include `generate` for code generation from semantic conventions, `validate` for registry validation, and `templates` for managing templates.
It features `forge_generate` for 80/20 Weaver Forge generation and `forge_to_agents` for complete system generation from semantic YAML to working AI agents.
`generate_models` creates Pydantic models from semantic conventions.
Agent commands like `communicate` enable interaction between generated AI agents with enhanced telemetry.
Conversation commands `start` and `analyze` manage and inspect generated conversation systems.
The `full_pipeline` command executes an end-to-end process from semantic YAML to agents, conversations, and telemetry validation.
Meeting commands (`roberts`, `scrum`) simulate parliamentary and Scrum meetings.
Benchmark commands (`ollama`) assess performance.
Demo commands (`quine`, `full`) showcase system capabilities.
Debugging commands (`spans`, `health`, `inspect`, `trace`) provide insights into system behavior and health.
Spiff commands (`chain`, `workflow`, `history`, `bpmn`, `compare`) enable command chaining, workflow execution, history tracking, BPMN integration, and comparison of workflow results.
Innovation commands (`generate_smart`, `validate_multi`) offer smart dual-mode generation and multi-agent validation.
The CLI enforces a 'generated-only' philosophy for critical components, failing if manual code is detected.
It integrates with `WeaverGenWorkflowContext` and `WeaverForgeGenerator` for workflow execution and code generation.
OTel spans are extensively used for tracing and validation across various operations.