File: test_next_level_8020.py

This module demonstrates "Next-Level 80/20 Enhancements" for BPMN-first architecture, focusing on self-optimizing workflows, automatic pattern discovery, and intelligent adaptation.

Key demonstrations and functionalities:

- **`demo_adaptive_learning`**: Showcases an adaptive BPMN engine that learns from multiple workflow executions. It uses `AdaptiveBPMNEngine` to run a series of executions, enabling optimization after a certain number of runs, and then reports on performance improvements and visualizes the learning curve.
- **`demo_process_mining`**: Demonstrates how process mining can discover BPMN workflows from execution spans. It loads (or generates mock) OpenTelemetry spans and uses `BPMNProcessMiner` to mine workflow patterns and generate a BPMN file from the discovered patterns.
- **`generate_mock_spans`**: A helper function to create synthetic OpenTelemetry spans for demonstration purposes when real span data is not available. It simulates various task sequences and attributes.
- **`demo_combined_intelligence`**: Integrates the adaptive learning and process mining demonstrations to show how these two capabilities work together to create self-improving workflows. It first runs the adaptive engine to generate data, then mines patterns from the generated spans, and finally provides insights into performance improvements and discovered workflow quality.
- **`main` function**: Orchestrates all the demonstrations, providing a high-level overview of the next-level enhancements and summarizing the key achievements, such as workflows that learn, automatic BPMN generation from traces, and performance optimization through adaptation.

The module leverages `src.weavergen.bpmn_adaptive_engine`, `src.weavergen.bpmn_process_miner`, and `src.weavergen.pydantic_ai_bpmn_engine` for its core functionalities. It uses `asyncio` for asynchronous operations and `rich` for enhanced console output and visualization.