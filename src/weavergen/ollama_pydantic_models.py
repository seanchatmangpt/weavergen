"""
Pydantic Models for Ollama + BPMN + Weaver Forge Integration

Structured data models for AI agent orchestration, semantic convention processing,
and code generation workflows with OpenTelemetry span tracking.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator


class AgentRole(str, Enum):
    """AI agent roles in the workflow"""
    ANALYZER = "analyzer"
    GENERATOR = "generator"
    VALIDATOR = "validator"
    OPTIMIZER = "optimizer"
    REVIEWER = "reviewer"


class GenerationType(str, Enum):
    """Code generation types"""
    PYDANTIC_MODELS = "pydantic_models"
    AI_AGENTS = "ai_agents"
    VALIDATION_LOGIC = "validation_logic"
    WEAVER_TEMPLATES = "weaver_templates"
    SEMANTIC_CONVENTIONS = "semantic_conventions"


class ValidationLevel(str, Enum):
    """Validation strictness levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    AI_ENHANCED = "ai_enhanced"


class SemanticAttribute(BaseModel):
    """Individual semantic attribute definition"""
    name: str
    type: str
    description: str
    required: bool = False
    default_value: Optional[Any] = None
    examples: List[str] = Field(default_factory=list)
    stability: str = "stable"


class SemanticGroup(BaseModel):
    """Group of related semantic attributes"""
    id: str
    prefix: str
    type: str = "attribute_group"
    brief: str
    attributes: List[SemanticAttribute] = Field(default_factory=list)
    extends: Optional[str] = None


class SemanticConvention(BaseModel):
    """Complete semantic convention definition"""
    groups: List[SemanticGroup]
    version: str = "1.0.0"
    schema_url: Optional[str] = None
    
    @validator('groups')
    def validate_groups(cls, v):
        if not v:
            raise ValueError("At least one semantic group required")
        return v


class AgentCapability(BaseModel):
    """Capability definition for AI agents"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    examples: List[Dict[str, Any]] = Field(default_factory=list)


class GeneratedCode(BaseModel):
    """AI-generated code with metadata"""
    language: str
    code: str
    imports: List[str] = Field(default_factory=list)
    file_name: str
    description: str
    validation_score: float = Field(ge=0, le=1, default=0.0)
    ai_model_used: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GeneratedAgent(BaseModel):
    """AI-generated agent definition"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    role: AgentRole
    name: str
    system_prompt: str
    capabilities: List[AgentCapability] = Field(default_factory=list)
    model_name: str = "qwen3:latest"
    result_type: str = "Dict[str, Any]"
    validation_score: float = Field(ge=0, le=1, default=0.0)
    execution_spans: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValidationResult(BaseModel):
    """Validation result with detailed feedback"""
    valid: bool
    score: float = Field(ge=0, le=1)
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    validated_by: str  # AI model or validator name
    validation_level: ValidationLevel
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TemplateSelection(BaseModel):
    """AI-selected templates for code generation"""
    selected_templates: List[str]
    customizations_needed: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)
    reasoning: str
    alternative_templates: List[str] = Field(default_factory=list)


class WorkflowStepResult(BaseModel):
    """Result from a single BPMN workflow step"""
    step_name: str
    success: bool
    output: Dict[str, Any] = Field(default_factory=dict)
    agent_used: Optional[str] = None
    ai_model: Optional[str] = None
    execution_time_ms: float = 0.0
    tokens_used: int = 0
    span_id: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SemanticProcessingContext(BaseModel):
    """Complete context for semantic convention processing"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    semantic_file: str
    output_dir: str
    target_languages: List[str] = Field(default_factory=list)
    
    # Generated content
    semantic_convention: Optional[SemanticConvention] = None
    generated_agents: List[GeneratedAgent] = Field(default_factory=list)
    generated_code: List[GeneratedCode] = Field(default_factory=list)
    validation_results: List[ValidationResult] = Field(default_factory=list)
    
    # Workflow state
    current_step: str = "initialization"
    completed_steps: List[str] = Field(default_factory=list)
    workflow_state: Dict[str, Any] = Field(default_factory=dict)
    step_results: List[WorkflowStepResult] = Field(default_factory=list)
    
    # Quality metrics
    overall_quality_score: float = Field(ge=0, le=1, default=0.0)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # OpenTelemetry integration
    spans: List[Dict[str, Any]] = Field(default_factory=list)
    trace_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BPMNServiceTaskConfig(BaseModel):
    """Configuration for BPMN service tasks with AI agents"""
    task_id: str
    task_name: str
    agent_role: AgentRole
    ai_model: str = "qwen3:latest"
    result_type: str = "Dict[str, Any]"
    system_prompt: str
    input_variables: List[str] = Field(default_factory=list)
    output_variables: List[str] = Field(default_factory=list)
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    retry_attempts: int = 3
    timeout_seconds: int = 300


class MultiAgentWorkflowConfig(BaseModel):
    """Configuration for multi-agent BPMN workflows"""
    workflow_name: str
    bpmn_file: str
    service_tasks: List[BPMNServiceTaskConfig] = Field(default_factory=list)
    parallel_execution: bool = True
    quality_gate_threshold: float = Field(ge=0, le=1, default=0.8)
    span_validation_enabled: bool = True
    
    # Ollama configuration
    ollama_base_url: str = "http://localhost:11434/v1"
    default_model: str = "qwen3:latest"
    
    # Weaver Forge integration
    weaver_binary: Optional[str] = None
    registry_url: str
    template_dirs: List[str] = Field(default_factory=list)


class PipelineExecutionResult(BaseModel):
    """Complete pipeline execution result"""
    workflow_config: MultiAgentWorkflowConfig
    processing_context: SemanticProcessingContext
    
    # Execution summary
    success: bool
    total_steps: int
    completed_steps: int
    failed_steps: int = 0
    execution_time_ms: float
    
    # AI integration metrics
    total_ai_interactions: int = 0
    total_tokens_used: int = 0
    ai_models_used: List[str] = Field(default_factory=list)
    
    # Code generation metrics
    files_generated: int = 0
    languages_supported: List[str] = Field(default_factory=list)
    weaver_forge_used: bool = False
    
    # Quality metrics
    overall_quality_score: float = Field(ge=0, le=1, default=0.0)
    validation_passed: bool = False
    span_validation_score: float = Field(ge=0, le=1, default=0.0)
    
    # Error tracking
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Span tracking
    total_spans_captured: int = 0
    span_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_environment: Dict[str, str] = Field(default_factory=dict)


class AnalyzeSemanticsPrompt(BaseModel):
    """Structured prompt for semantic analysis agent"""
    semantic_file_content: str
    analysis_focus: List[str] = Field(default_factory=lambda: [
        "attribute_completeness", 
        "naming_consistency", 
        "type_accuracy",
        "description_quality"
    ])
    output_format: str = "structured_json"


class GenerateCodePrompt(BaseModel):
    """Structured prompt for code generation agent"""
    semantic_convention: SemanticConvention
    target_language: str
    generation_type: GenerationType
    template_context: Dict[str, Any] = Field(default_factory=dict)
    style_preferences: Dict[str, str] = Field(default_factory=dict)


class ValidateCodePrompt(BaseModel):
    """Structured prompt for code validation agent"""
    generated_code: str
    language: str
    validation_criteria: List[str] = Field(default_factory=lambda: [
        "syntax_correctness",
        "style_compliance", 
        "otel_convention_adherence",
        "pydantic_best_practices"
    ])
    expected_output_type: str = "ValidationResult"


# Factory functions for common configurations

def create_semantic_analyzer_config(task_id: str = "analyze_semantics") -> BPMNServiceTaskConfig:
    """Create configuration for semantic analysis service task"""
    return BPMNServiceTaskConfig(
        task_id=task_id,
        task_name="Analyze Semantic Conventions",
        agent_role=AgentRole.ANALYZER,
        system_prompt="""You are an expert semantic convention analyzer specializing in OpenTelemetry.
        
        Analyze semantic convention YAML files for:
        1. Attribute completeness and consistency
        2. Naming convention adherence  
        3. Type accuracy and validation
        4. Description quality and clarity
        5. Cross-reference accuracy
        
        Respond with structured analysis in SemanticConvention format.""",
        input_variables=["semantic_file_content"],
        output_variables=["analyzed_convention", "analysis_quality_score"],
        result_type="SemanticConvention"
    )


def create_code_generator_config(task_id: str = "generate_pydantic_models") -> BPMNServiceTaskConfig:
    """Create configuration for Pydantic model generation service task"""
    return BPMNServiceTaskConfig(
        task_id=task_id,
        task_name="Generate Pydantic Models",
        agent_role=AgentRole.GENERATOR,
        system_prompt="""You are an expert Python developer specializing in Pydantic and OpenTelemetry.
        
        Generate production-ready Pydantic models from semantic conventions:
        1. Create strongly-typed Pydantic models
        2. Add proper validation and constraints
        3. Include comprehensive docstrings
        4. Follow Python best practices
        5. Ensure OpenTelemetry compliance
        
        Respond with GeneratedCode containing complete, runnable Python code.""",
        input_variables=["semantic_convention", "target_language"],
        output_variables=["generated_models", "generation_quality_score"],
        result_type="GeneratedCode"
    )


def create_validator_config(task_id: str = "validate_generated_code") -> BPMNServiceTaskConfig:
    """Create configuration for code validation service task"""
    return BPMNServiceTaskConfig(
        task_id=task_id,
        task_name="Validate Generated Code",
        agent_role=AgentRole.VALIDATOR,
        validation_level=ValidationLevel.AI_ENHANCED,
        system_prompt="""You are an expert code reviewer specializing in Python, Pydantic, and OpenTelemetry.
        
        Validate generated code for:
        1. Syntax correctness and Python best practices
        2. Pydantic model structure and validation
        3. OpenTelemetry semantic convention compliance
        4. Code quality and maintainability
        5. Performance considerations
        
        Respond with detailed ValidationResult including scores and specific feedback.""",
        input_variables=["generated_code", "language"],
        output_variables=["validation_result", "validation_score"],
        result_type="ValidationResult"
    )


def create_default_workflow_config(
    semantic_file: str,
    output_dir: str = "generated_output"
) -> MultiAgentWorkflowConfig:
    """Create default multi-agent workflow configuration"""
    return MultiAgentWorkflowConfig(
        workflow_name="ollama_pydantic_weaver_pipeline",
        bpmn_file="src/weavergen/workflows/bpmn/ollama_pydantic_generation.bpmn",
        registry_url=semantic_file,
        service_tasks=[
            create_semantic_analyzer_config(),
            create_code_generator_config("generate_pydantic_models"),
            create_code_generator_config("generate_ai_agents"),
            create_validator_config(),
        ],
        parallel_execution=True,
        quality_gate_threshold=0.85
    )