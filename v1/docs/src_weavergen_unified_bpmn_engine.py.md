This Python file defines the `UnifiedBPMNEngine`, a central component of WeaverGen that consolidates various BPMN engines and functionalities.
It aims to provide 100% of existing functionality with 80% improved usability.
The `UnifiedServiceRegistry` class automatically discovers and provides unified access to service tasks from different categories: Weaver, AI, Validation, BPMN orchestration, and Custom tasks.
`ServiceTaskInfo` dataclass provides self-documenting information for each service task, including inputs, outputs, and examples.
The engine initializes and registers various sub-engines (e.g., `PydanticAIBPMNEngine`, `Spiff8020Engine`, `BPMNUltralightEngine`, `WeaverForgeBPMNEngine`) for flexible execution.
`WorkflowMonitor` provides real-time workflow execution monitoring with visual feedback, including a timeline and Rich layout for live updates.
The `execute` method is the main entry point for running any BPMN workflow, with integrated monitoring and OpenTelemetry span tracking.
It includes methods for task discovery (`discover_tasks`, `search_tasks`, `get_task_info`) and for generating visual representations of workflows (Mermaid diagrams).
It can execute both real and simulated tasks, allowing for flexible testing and demonstration.
This engine is designed to simplify the interaction with complex BPMN workflows and underlying execution mechanisms, making them more accessible and observable.