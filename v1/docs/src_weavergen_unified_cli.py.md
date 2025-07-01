This Python file defines a Unified Command Line Interface (CLI) for WeaverGen, designed to simplify access to its functionalities.
It uses `typer` for CLI command definition and `rich` for enhanced console output.
The CLI provides four main commands: `run`, `studio`, `tasks`, and `visualize`.
`run`: Executes any BPMN workflow, handling input data (YAML/JSON), context, debug mode, and output formatting (rich, JSON, Mermaid).
It includes an auto-installation feature for the Weaver binary, ensuring a plug-and-play experience.
`studio`: Launches a conceptual visual workflow studio, showcasing features like drag-drop design, live task palette, real-time validation, and interactive debugging.
`tasks`: Allows browsing and searching available service tasks, with options for detailed information and catalog export.
`visualize`: Generates visual diagrams (Mermaid) of BPMN workflows and execution flows, including task details and statistics.
It also includes `install_weaver` command for manual or automatic installation/update of the OTel Weaver binary, and a `doctor` command for comprehensive system health checks.
The CLI aims to make WeaverGen's complex functionalities accessible and user-friendly, abstracting away underlying complexities.