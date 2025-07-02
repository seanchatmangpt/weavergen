# WeaverGen v2 - AI Agent System Product Requirements Document (PRD)

## 1. Overview

This document outlines the product requirements for the AI Agent System in WeaverGen v2. This system is built on a **BPMN-first architecture**, where all operations are orchestrated by BPMN workflows. It leverages a multi-agent system, powered by `pydantic-ai` and Ollama, to automate tasks related to semantic convention analysis, code generation, validation, and Six Sigma process improvement.

## 2. Core Features

### 2.1. BPMN-Driven Workflow Orchestration

*   **Feature:** All system operations are defined and executed as BPMN workflows.
*   **Implementation:** The `bpmn_first_engine.py` and `bpmn_orchestrator.py` modules provide the core workflow execution capabilities. The system uses SpiffWorkflow to execute BPMN 2.0 compliant workflows.
*   **User Story:** As a developer, I want to define and visualize my development workflows using industry-standard BPMN diagrams, ensuring clarity, consistency, and auditability.
*   **Acceptance Criteria:**
    *   The system can execute a BPMN workflow from a `.bpmn` file.
    *   The CLI commands trigger the execution of specific BPMN workflows.
    *   The workflow execution is instrumented with OpenTelemetry for observability.

### 2.2. Multi-Agent System

*   **Feature:** A sophisticated multi-agent system for collaborative task execution.
*   **Implementation:** The `agents/multi_agent_ollama.py` module implements a multi-agent system with the following patterns:
    *   **Agent Delegation:** Agents can delegate tasks to other specialized agents.
    *   **Programmatic Hand-off:** Agents can sequentially hand off tasks to one another.
    *   **Graph-based Control Flow:** Complex workflows can be orchestrated using a graph-based control flow.
*   **User Story:** As a developer, I want to leverage a team of AI agents to automate complex tasks, such as code generation, validation, and analysis.
*   **Acceptance Criteria:**
    *   The `agents communicate` command can simulate a conversation between multiple agents.
    *   The system can orchestrate a multi-agent workflow to generate and validate code.
    *   The agent interactions are instrumented with OpenTelemetry.

### 2.3. AI-Powered Semantic Convention Analysis and Code Generation

*   **Feature:** An AI-powered system for analyzing semantic conventions and generating code.
*   **Implementation:** The `bpmn_weaver_forge.py` and `six_sigma_bpmn_service_tasks.py` modules provide service tasks for these functions. The system uses `pydantic-ai` with an Ollama backend to perform the analysis and generation.
*   **User Story:** As a developer, I want to automatically analyze my semantic convention files for quality and compliance, and then generate code from them in multiple languages.
*   **Acceptance Criteria:**
    *   The system can analyze a semantic convention file and provide a quality score and recommendations.
    *   The system can generate code from a semantic convention file in Python and other languages.
    *   The AI interactions are instrumented with the `@ai_validation` decorator.

### 2.4. Six Sigma Integration

*   **Feature:** A set of tools and workflows for applying Six Sigma methodologies to software development.
*   **Implementation:** The `six_sigma_bpmn_service_tasks.py` module provides service tasks for various Six Sigma phases (Define, Measure, Analyze, Improve, Control). The `six_sigma_qwen3_training.bpmn` workflow defines a complete Six Sigma training process.
*   **User Story:** As a quality engineer, I want to use Six Sigma principles to improve the quality and efficiency of my development processes, guided by AI-powered tools.
*   **Acceptance Criteria:**
    *   The system can execute a Six Sigma BPMN workflow.
    *   The system provides AI-powered tools for each phase of the DMAIC and DMEDI cycles.
    *   The Six Sigma workflows are instrumented with OpenTelemetry.

## 3. Architecture

*   **BPMN-First:** The system is architected around a BPMN workflow engine. All business logic is defined in BPMN 2.0 diagrams and executed by the engine.
*   **CLI:** The `weavergen` CLI is the primary user interface. Each CLI command triggers a corresponding BPMN workflow.
*   **Service Tasks:** The actual work is performed by Python functions (service tasks) that are decorated with `@semantic_span` and `@ai_validation` for observability and AI instrumentation. These service tasks are called from the BPMN workflows.
*   **AI Integration:** The system uses `pydantic-ai` to interact with LLMs through an Ollama backend. The `@ai_validation` decorator provides a standardized way to instrument and validate AI interactions.
*   **Pydantic Models:** All data structures are defined using Pydantic models, ensuring data validation and consistency.

## 4. Non-Functional Requirements

*   **Extensibility:** The system is designed to be easily extensible with new BPMN workflows, service tasks, and AI agents.
*   **Observability:** All operations are instrumented with OpenTelemetry, providing deep visibility into the system's behavior.
*   **Robustness:** The system is designed to be resilient to errors, with fallback mechanisms for when AI models are unavailable.
*   **Performance:** The use of parallel gateways in the BPMN workflows allows for concurrent execution of tasks, improving performance.

## 5. Future Work

*   **Full Implementation of all CLI commands:** While the core workflows are implemented, some CLI commands are still placeholders.
*   **More Sophisticated AI Capabilities:** The AI capabilities could be extended with more advanced features, such as self-healing workflows and autonomous agent orchestration.
*   **Support for More BPMN Engines:** The system could be extended to support other BPMN engines besides SpiffWorkflow.
*   **Web-based UI:** A web-based UI could be created for visualizing and interacting with the BPMN workflows and agent systems.