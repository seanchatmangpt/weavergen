"""Generated semantic convention attributes for WeaverGen."""


# Core WeaverGen system telemetry attributes
COMPONENT_TYPE = "weavergen.component.type"

# Values for weavergen.component.type
COMPONENT_TYPE__AGENT = "agent"
COMPONENT_TYPE__WORKFLOW = "workflow"
COMPONENT_TYPE__GENERATOR = "generator"
COMPONENT_TYPE__VALIDATOR = "validator"

GENERATION_SOURCE = "weavergen.generation.source"
GENERATION_TARGET = "weavergen.generation.target"

# AI agent specific attributes
ROLE = "agent.role"

# Values for agent.role
ROLE__COORDINATOR = "coordinator"
ROLE__ANALYST = "analyst"
ROLE__FACILITATOR = "facilitator"
ROLE__GENERATOR = "generator"

LLM_MODEL = "agent.llm.model"
STRUCTURED_OUTPUT = "agent.structured.output"
INTERACTION_COUNT = "agent.interaction.count"

# Workflow orchestration attributes
ENGINE = "workflow.engine"
STEPS_TOTAL = "workflow.steps.total"
STEPS_COMPLETED = "workflow.steps.completed"
SUCCESS_RATE = "workflow.success.rate"

# Code generation specific attributes
LANGUAGE = "generation.language"
TEMPLATE_ENGINE = "generation.template.engine"
FILES_GENERATED = "generation.files.generated"
SEMANTIC_COMPLIANCE = "generation.semantic.compliance"

# Validation and quality assurance attributes
METHOD = "validation.method"

# Values for validation.method
METHOD__SPAN = "span"
METHOD__CONTRACT = "contract"
METHOD__SEMANTIC = "semantic"

HEALTH_SCORE = "validation.health.score"
QUINE_COMPLIANT = "validation.quine.compliant"
