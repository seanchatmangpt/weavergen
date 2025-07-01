File: weavergen_bpmn_ai_8020.py

This module extends the BPMN-first approach of `weavergen_bpmn_8020.py` by adding optional AI enhancement capabilities. It focuses on integrating a single, focused AI agent to provide valuable, yet non-critical, improvements to the code generation process, with graceful fallback if AI components are unavailable.

Key components and functionalities:

-   **AI Availability Check**: Dynamically checks for the presence of `pydantic_ai` and related models, enabling AI features only if available.
-   **Pydantic Models for AI**: Defines `EnhancedAttribute` (for AI-generated content in semantic attributes) and `QualityCheckResult` (for AI-driven code quality assessments).
-   **`SemanticEnhancementAgent` Class**: A single, focused AI agent responsible for semantic enhancement.
    -   **Lazy Initialization**: Initializes the AI agent (`pydantic_ai.Agent`) only when needed, configuring it for Ollama.
    -   **`enhance_descriptions`**: Fills missing descriptions in semantic conventions using AI, based on existing brief descriptions.
    -   **`suggest_attributes`**: Suggests new, useful attributes for semantic groups based on AI analysis.
    -   **`check_quality`**: Performs a simple AI-driven quality check on generated code samples, providing a score and improvement suggestions.
-   **Enhanced Service Tasks**:
    -   **`EnhanceDescriptionsTask`**: A BPMN service task that utilizes the `SemanticEnhancementAgent` to enhance semantic descriptions within the workflow context.
    -   **`SuggestAttributesTask`**: A BPMN service task that uses the AI agent to suggest new attributes.
    -   **`AIQualityCheckTask`**: A BPMN service task that performs an AI-driven quality check on the generated code.
-   **`EnhancedBPMNEngine` Class**: Extends `SimpleBPMNEngine` to incorporate optional AI enhancement tasks into the workflow execution. It conditionally executes AI tasks based on the `enable_ai` flag and AI component availability.
-   **Enhanced CLI Command (`generate_enhanced`)**:
    -   A `typer` command that allows users to generate code with optional AI enhancement.
    -   It dynamically selects the appropriate BPMN workflow file (`weaver_generate_enhanced_8020.bpmn` or `weaver_generate_8020.bpmn`) based on whether AI enhancement is requested.
    -   Executes the workflow using the `EnhancedBPMNEngine`.
-   **`display_enhanced_results` Function**: A helper function to display the results of the code generation, including any AI-driven enhancements (e.g., number of enhanced descriptions, suggested attributes, AI quality score).

This module demonstrates a practical approach to integrating AI into a BPMN-driven code generation pipeline, providing clear value while maintaining robustness and graceful degradation.