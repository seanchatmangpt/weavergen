This Python file defines a `WorkflowStudio` class, which provides visual tools for designing, debugging, and monitoring BPMN workflows within the WeaverGen unified engine.
It aims to make BPMN accessible and user-friendly.
Key components include:
- **`WorkflowDesigner`**: Responsible for creating workflow templates (e.g., basic generation, AI-enhanced, validation-only, custom) and displaying a categorized task palette.
- **`VisualDebugger`**: Enables interactive debugging of workflow execution with step-through capabilities, breakpoints, and a variable inspector.
- **`ExecutionMonitor`**: Provides real-time monitoring of workflow execution, including performance dashboards, task performance breakdowns, and performance recommendations.
The `WorkflowStudio` integrates these components to offer a comprehensive visual environment.
It includes an `launch_interactive_studio` method that presents a menu-driven interface for users to choose between different studio functionalities (task palette, design, debug, monitor, visualize, export).
The studio leverages `rich` for rich console output, providing visually appealing and informative displays.
This module is a significant step towards a more intuitive and interactive experience for managing complex BPMN workflows in WeaverGen.