File: mining_commands.py

This module provides CLI commands for process mining functionalities within the WeaverGen project. It integrates XES conversion, PM4Py, and process analysis.

Key functionalities include:

- `spans_to_xes`: Converts OpenTelemetry spans (JSON) into XES format, suitable for process mining tools like ProM, Celonis, or Disco.
- `analyze_xes`: Analyzes XES files to generate process insights, including statistics, variants, model discovery, performance analysis, and visualizations. It can also generate process models.
- `xes_to_bpmn`: Discovers and converts an XES execution log into a BPMN workflow model, which can be used in workflow automation engines like SpiffWorkflow.
- `mine_patterns`: Mines process patterns, sequences, and optimizations from OpenTelemetry span data, providing insights into workflow efficiency and improvement opportunities. It can also generate BPMN from discovered patterns.
- `adaptive_demo`: Demonstrates adaptive BPMN learning by running multiple workflow executions and optimizing performance over time. It tracks execution history and provides performance reports and learning curve visualizations.
- `convert_all`: Batch converts multiple span JSON files within a specified directory to XES format and can optionally analyze the converted files.
- `export_dataframe`: Exports OpenTelemetry spans into a flattened DataFrame format (CSV, Parquet, or JSON) for data analysis using tools like Excel, R, or Python pandas. It also provides a preview of the exported data.

The module uses `typer` for CLI command definition, `rich` for enhanced console output, and `pathlib` for path manipulations. It leverages `XESConverter` for XES-related operations, `BPMNProcessMiner` for pattern mining, `AdaptiveBPMNEngine` for adaptive learning, and `PydanticAIContext` for context management in the adaptive demo.