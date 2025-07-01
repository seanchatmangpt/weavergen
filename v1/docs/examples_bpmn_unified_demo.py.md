File: examples/bpmn_unified_demo.py

This module demonstrates the "BPMN Unified Engine," an enhanced BPMN-first approach designed to simplify complex functionalities and make them more accessible. It showcases how all functionalities can be integrated into a single, easy-to-use system.

Key components and functionalities:

- **`ServiceTaskInfo` Dataclass**: Represents a self-documenting service task, including its ID, category, description, inputs, and outputs. It can generate a rich panel representation for display.
- **`UnifiedServiceRegistry` Class**: Discovers and manages all available BPMN service tasks (e.g., Weaver tasks, AI tasks, Validation tasks). It allows listing tasks by category and searching for specific tasks.
- **`WorkflowMonitor` Class**: Provides real-time monitoring of workflow executions, recording start times, task durations, and statuses, and generating an execution timeline.
- **`UnifiedBPMNEngine` Class**: The core engine that unifies all functionalities:
    - Discovers available tasks using the `UnifiedServiceRegistry`.
    - Executes BPMN workflows with real-time monitoring using `WorkflowMonitor`.
    - Simulates task execution and records results.
    - Generates Mermaid diagrams for workflow visualization.
- **`WorkflowStudio` Class**: A visual workflow design and debugging tool that:
    - Displays a rich catalog of available BPMN service tasks.
    - Allows searching for tasks.
    - Visualizes workflows using Mermaid diagrams.
- **`demo` Function**: Demonstrates the end-to-end capabilities of the unified BPMN engine, including:
    - Discovering available tasks.
    - Searching for specific tasks (e.g., AI tasks).
    - Visualizing a sample workflow (`generate.bpmn`).
    - Executing the sample workflow with live display of progress and recording results.
    - Displaying execution results and a detailed timeline.

The module uses `asyncio` for asynchronous operations, `rich` for enhanced console output and live displays, `pathlib` for path manipulations, and `dataclasses` for structured data. It aims to provide a comprehensive and user-friendly experience for managing and executing BPMN-driven workflows.