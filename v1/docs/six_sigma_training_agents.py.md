File: six_sigma_training_agents.py

This module defines AI-powered training agents for the Six Sigma DMEDI (Define, Measure, Explore, Develop, Implement) methodology. Each agent specializes in a specific DMEDI phase and provides interactive learning experiences.

Key components and functionalities:

- **DMEDIPhase Enum**: Defines the five phases of the DMEDI methodology.
- **TrainingSession Model**: Represents a Six Sigma training session, tracking participant, phase, module, completion, and assessment.
- **Phase-Specific Data Models**: Pydantic models (`DefinePhaseData`, `MeasurePhaseData`, `ExplorePhaseData`, `DevelopPhaseData`, `ImplementPhaseData`) to capture specific data relevant to each DMEDI phase.
- **CapstoneProject Model**: Represents a DMEDI capstone project, tracking its ID, industry domain, completed phases, final score, and certification status.
- **SixSigmaInstructor (Base Class)**: A base class for Six Sigma training instructors, defining common attributes like agent ID, DMEDI phase, and AI model.
- **Phase-Specific Instructor Agents**: Classes like `DefinePhaseInstructor`, `MeasurePhaseInstructor`, `ExplorePhaseInstructor`, `DevelopPhaseInstructor`, and `ImplementPhaseInstructor` inherit from `SixSigmaInstructor`. Each is an AI agent (`pydantic_ai.Agent`) with a specialized system prompt for its respective DMEDI phase. They offer methods to teach specific topics (e.g., `teach_project_charter`, `teach_voice_of_customer`, `teach_triz_methodology`, `design_experiment`, `plan_implementation`) and assess progress.
- **CapstoneProjectCoach**: An AI coach for DMEDI capstone projects, responsible for evaluating projects against Black Belt certification standards.
- **SixSigmaTrainingOrchestrator**: Orchestrates the entire Six Sigma training experience, managing instructors for each phase and the capstone coach. It can conduct personalized training sessions and assess participant progress.
- **`demo_six_sigma_training` function**: Demonstrates the end-to-end functionality of the Six Sigma AI training system, including session creation, training, assessment, and capstone evaluation.

The module uses `pydantic` for data modeling, `pydantic_ai` for AI agent creation, and `asyncio` for asynchronous operations.