File: test_8020_quick.py

This module provides quick tests for the 80/20 improvements, specifically focusing on error boundaries and the enhanced BPMN engine, without live monitoring to avoid timeouts.

Key functionalities and tests:

-   **`test_error_boundaries` Function**:
    -   Demonstrates the functionality of `BPMNErrorBoundary` for handling task failures.
    -   Tests a successful task execution.
    -   Tests a flaky task that succeeds after retries.
    -   Tests a failing task that falls back to a mock result, showcasing graceful degradation.
    -   Prints an error summary, categorizing errors by severity.
-   **`test_enhanced_engine` Function**:
    -   Tests the `EnhancedPydanticAIBPMNEngine` by executing a sample workflow.
    -   Disables live monitoring to prevent timeouts during the test.
    -   Prints a summary of the workflow completion, including the number of agents and models generated, and the overall quality score.
-   **`main` Function**:
    -   Orchestrates the execution of both `test_error_boundaries` and `test_enhanced_engine`.
    -   Provides a clear indication of the start and completion of the quick tests.

The module uses `asyncio` for asynchronous test execution, `rich.console` for formatted output, and imports components from `src.weavergen.bpmn_error_boundaries`, `src.weavergen.bpmn_8020_enhanced`, and `src.weavergen.pydantic_ai_bpmn_engine` to perform its tests. It serves as a rapid verification tool for core 80/20 enhancements.