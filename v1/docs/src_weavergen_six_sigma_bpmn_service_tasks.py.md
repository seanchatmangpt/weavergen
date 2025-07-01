This Python file defines Six Sigma BPMN Service Tasks, integrating `qwen3` (via Ollama) and adhering to WeaverGen's instrumentation patterns.
It extends `SpiffServiceTask` from `SpiffWorkflow` to create custom BPMN service tasks.
Key features include:
- **Structured Output Models**: Pydantic models (`SixSigmaCharterAnalysis`, `SixSigmaVOCAnalysis`, `SixSigmaTRIZSolution`, `SixSigmaDOEDesign`, `SixSigmaImplementationPlan`) define the structured outputs for each task, ensuring data consistency and machine readability.
- **`qwen3` Integration**: Each service task initializes a `pydantic_ai.Agent` with an `OpenAIModel` configured to use `qwen3:latest` via Ollama.
- **WeaverGen Instrumentation**: Decorators like `@semantic_span`, `@ai_validation`, `@layer_span`, and `@resource_span` are used to instrument the task execution with OpenTelemetry spans, capturing detailed telemetry data for observability and validation.
- **Specific Service Tasks**: The file defines several specialized service tasks for different DMEDI phases:
  - `SixSigmaCharterAnalysisTask`: Analyzes project charters.
  - `SixSigmaVOCAnalysisTask`: Conducts Voice of Customer analysis.
  - `SixSigmaTRIZInnovationTask`: Applies TRIZ methodology for innovation.
  - `SixSigmaDOEDesignTask`: Designs comprehensive experiments.
  - `SixSigmaImplementationPlanTask`: Develops implementation plans.
  - `SixSigmaTrainingAssessmentTask`: Assesses Six Sigma training progress.
Each task's `_execute_task_logic` method constructs a detailed prompt for the `qwen3` agent based on the task's input data and returns the structured output.
This module enables the execution of complex, AI-driven Six Sigma processes within a BPMN workflow, with robust instrumentation for monitoring and validation.