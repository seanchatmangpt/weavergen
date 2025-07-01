This Python file defines an Adaptive BPMN Engine, a self-optimizing system that learns from workflow execution patterns.
It extends `PydanticAIBPMNEngine` and incorporates `SpanValidator` for performance tracking.
Key features include automatic performance tracking, pattern discovery from execution history, dynamic optimization suggestions, and adaptive retry/timeout configurations.
`ExecutionMetrics` dataclass captures detailed metrics for each workflow run, including duration, task durations, quality score, and success status.
`TaskPattern` and `WorkflowOptimization` dataclasses represent discovered patterns and optimization recommendations, respectively.
The engine loads and saves execution history to `.weavergen/adaptive/execution_history.json` for continuous learning.
`execute_adaptive` method orchestrates workflow execution, tracking metrics and applying learned optimizations.
It analyzes execution history to identify optimization opportunities such as parallelization, task removal candidates, caching, and optimal retry limits.
Methods like `_calculate_task_statistics`, `_find_parallel_opportunities`, `_identify_bottlenecks`, and `_discover_patterns` are used for data analysis and pattern recognition.
It provides a `get_performance_report` to summarize performance and `visualize_learning_curve` for ASCII-based visualization.
`detect_performance_anomalies` identifies deviations from baseline performance using statistical methods (e.g., Z-score) and provides recommendations.
This engine represents a "next-level enhancement" for BPMN, enabling workflows to self-improve and adapt based on real-world performance data.