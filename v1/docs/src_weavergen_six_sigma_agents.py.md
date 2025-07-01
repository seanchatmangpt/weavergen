This Python file defines AI agents for Design for Lean Six Sigma (DMEDI) training.
It implements specialized AI agents using Pydantic AI for structured outputs.
Key agents include BlackBeltTrainerAgent, MasterBlackBeltAgent, ChampionAgent, and DMEDICoachAgent.
Each agent provides expertise aligned with DMEDI phases.
Mock agent implementations are provided as a fallback when Pydantic AI is unavailable.
Agent output models define structured data for assessments, guidance, and strategic alignment.
`TrainingAssessment` captures results from Black Belt Trainer.
`ProjectGuidance` provides insights from Master Black Belt.
`StrategicAlignment` assesses project value from a Champion's perspective.
`PhaseGuidance` offers phase-specific coaching from DMEDI Coach.
A `SixSigmaAgentFactory` manages the creation of these agents.
A `SixSigmaAgentOrchestrator` coordinates multiple agents for comprehensive project reviews.
The orchestrator synthesizes recommendations from various agent inputs.
Model availability is checked, prioritizing OpenAI, then Ollama (qwen2.5 or llama3.2), then mock agents.
The module integrates with `six_sigma_models.py` for project-related data models.
This system supports a CLI-first workflow by providing structured outputs for automated processing.