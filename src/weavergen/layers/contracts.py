"""
Contracts Layer - Data Models, Interfaces, and Type Definitions

This is the foundational layer that defines all data structures, interfaces,
and contracts used throughout the WeaverGen system. No business logic here,
only data models and type definitions.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ============================================================================
# Core Enums and Types
# ============================================================================

class TargetLanguage(str, Enum):
    """Supported target languages for code generation."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    JAVA = "java"
    CSHARP = "csharp"
    RUST = "rust"
    CPP = "cpp"


class TemplateType(str, Enum):
    """Types of templates available."""
    MODELS = "models"
    INSTRUMENTATION = "instrumentation"
    TELEMETRY = "telemetry"
    REGISTRY = "registry"
    FULL_STACK = "full_stack"


class ValidationLevel(str, Enum):
    """Levels of validation strictness."""
    BASIC = "basic"
    STRICT = "strict"
    PEDANTIC = "pedantic"


class ExecutionStatus(str, Enum):
    """Status of operation execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RequirementLevel(str, Enum):
    """OpenTelemetry requirement levels."""
    REQUIRED = "required"
    CONDITIONALLY_REQUIRED = "conditionally_required"
    RECOMMENDED = "recommended"
    OPT_IN = "opt_in"


class AttributeType(str, Enum):
    """OpenTelemetry attribute types."""
    STRING = "string"
    STRING_ARRAY = "string[]"
    INT = "int"
    INT_ARRAY = "int[]"
    DOUBLE = "double"
    DOUBLE_ARRAY = "double[]"
    BOOLEAN = "boolean"
    BOOLEAN_ARRAY = "boolean[]"


class Stability(str, Enum):
    """OpenTelemetry stability levels."""
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


# ============================================================================
# Base Contracts
# ============================================================================

class BaseContract(BaseModel):
    """Base contract with common fields."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IExecutable(ABC):
    """Interface for executable operations."""
    
    @abstractmethod
    async def execute(self) -> "ExecutionResult":
        """Execute the operation and return result."""
        raise NotImplementedError


class IValidatable(ABC):
    """Interface for validatable objects."""
    
    @abstractmethod
    def validate(self, level: ValidationLevel = ValidationLevel.BASIC) -> "ValidationResult":
        """Validate the object and return validation result."""
        raise NotImplementedError


class IConfigurable(ABC):
    """Interface for configurable components."""
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the component with given configuration."""
        raise NotImplementedError


# ============================================================================
# Semantic Convention Contracts
# ============================================================================

class AttributeDefinition(BaseModel):
    """Definition of a semantic convention attribute."""
    id: str = Field(description="Unique attribute identifier")
    type: AttributeType = Field(description="Attribute data type")
    brief: str = Field(description="Brief description")
    note: Optional[str] = Field(default=None, description="Detailed note")
    examples: List[Any] = Field(default_factory=list, description="Example values")
    requirement_level: RequirementLevel = Field(description="Requirement level")
    stability: Stability = Field(default=Stability.EXPERIMENTAL)
    deprecated: Optional[str] = Field(default=None, description="Deprecation notice")
    prefix: Optional[str] = Field(default=None, description="Attribute prefix")
    tag: Optional[str] = Field(default=None, description="Attribute tag")


class EventDefinition(BaseModel):
    """Definition of a semantic event."""
    name: str = Field(description="Event name")
    domain: str = Field(description="Event domain")
    brief: str = Field(description="Brief description")
    note: Optional[str] = Field(default=None, description="Detailed note")
    stability: Stability = Field(default=Stability.EXPERIMENTAL)
    attributes: List[AttributeDefinition] = Field(default_factory=list)


class SpanDefinition(BaseModel):
    """Definition of a semantic span."""
    span_name: str = Field(description="Span name")
    brief: str = Field(description="Brief description")
    note: Optional[str] = Field(default=None, description="Detailed note")
    stability: Stability = Field(default=Stability.EXPERIMENTAL)
    attributes: List[AttributeDefinition] = Field(default_factory=list)
    events: List[EventDefinition] = Field(default_factory=list)


class MetricDefinition(BaseModel):
    """Definition of a semantic metric."""
    metric_name: str = Field(description="Metric name")
    brief: str = Field(description="Brief description")
    note: Optional[str] = Field(default=None, description="Detailed note")
    instrument: str = Field(description="Metric instrument type")
    unit: Optional[str] = Field(default=None, description="Metric unit")
    stability: Stability = Field(default=Stability.EXPERIMENTAL)
    attributes: List[AttributeDefinition] = Field(default_factory=list)


class SemanticGroup(BaseModel):
    """A group of related semantic conventions."""
    id: str = Field(description="Group identifier")
    type: str = Field(description="Group type (e.g., 'span', 'event', 'metric')")
    brief: str = Field(description="Brief description")
    note: Optional[str] = Field(default=None, description="Detailed note")
    prefix: Optional[str] = Field(default=None, description="Common prefix")
    extends: Optional[str] = Field(default=None, description="Extended group")
    stability: Stability = Field(default=Stability.EXPERIMENTAL)
    
    # Group content
    attributes: List[AttributeDefinition] = Field(default_factory=list)
    spans: List[SpanDefinition] = Field(default_factory=list)
    events: List[EventDefinition] = Field(default_factory=list)
    metrics: List[MetricDefinition] = Field(default_factory=list)


class SemanticConvention(BaseModel):
    """Complete semantic convention definition."""
    id: str = Field(description="Convention identifier")
    brief: str = Field(description="Brief description")
    note: Optional[str] = Field(default=None, description="Detailed note")
    stability: Stability = Field(default=Stability.EXPERIMENTAL)
    groups: List[SemanticGroup] = Field(default_factory=list)


# ============================================================================
# Template Contracts
# ============================================================================

class TemplateVariable(BaseModel):
    """Template variable definition."""
    name: str = Field(description="Variable name")
    type: str = Field(description="Variable type")
    description: str = Field(description="Variable description")
    default: Optional[Any] = Field(default=None, description="Default value")
    required: bool = Field(default=True, description="Whether variable is required")


class TemplateManifest(BaseModel):
    """Template manifest describing template capabilities."""
    name: str = Field(description="Template name")
    version: str = Field(description="Template version")
    description: str = Field(description="Template description")
    author: str = Field(description="Template author")
    target_language: TargetLanguage = Field(description="Target language")
    template_type: TemplateType = Field(description="Template type")
    
    # Template configuration
    variables: List[TemplateVariable] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    output_files: List[str] = Field(default_factory=list)
    
    # Metadata
    tags: Set[str] = Field(default_factory=set)
    license: Optional[str] = Field(default=None)
    homepage: Optional[str] = Field(default=None)


class GeneratedFile(BaseModel):
    """Information about a generated file."""
    path: Path = Field(description="File path")
    content: str = Field(description="File content")
    language: TargetLanguage = Field(description="Target language")
    template_used: str = Field(description="Template that generated this file")
    checksum: Optional[str] = Field(default=None, description="Content checksum")


# ============================================================================
# Request/Response Contracts
# ============================================================================

class GenerationRequest(BaseContract):
    """Request for code generation."""
    semantic_convention: SemanticConvention = Field(description="Semantic convention to generate from")
    target_languages: List[TargetLanguage] = Field(description="Target languages")
    output_directory: Path = Field(description="Output directory")
    template_overrides: Dict[str, str] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)


class GenerationResult(BaseContract):
    """Result of code generation."""
    request_id: UUID = Field(description="Original request ID")
    status: ExecutionStatus = Field(description="Generation status")
    generated_files: List[GeneratedFile] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    execution_time_ms: int = Field(description="Execution time in milliseconds")
    templates_used: List[str] = Field(default_factory=list)


class ValidationRequest(BaseContract):
    """Request for validation."""
    target: Union[Path, SemanticConvention, str] = Field(description="Target to validate")
    validation_level: ValidationLevel = Field(default=ValidationLevel.BASIC)
    rules: List[str] = Field(default_factory=list)
    options: Dict[str, Any] = Field(default_factory=dict)


class ValidationError(BaseModel):
    """Validation error details."""
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    line: Optional[int] = Field(default=None, description="Line number")
    column: Optional[int] = Field(default=None, description="Column number")
    severity: str = Field(default="error", description="Error severity")
    rule: Optional[str] = Field(default=None, description="Validation rule")


class ValidationResult(BaseContract):
    """Result of validation."""
    request_id: UUID = Field(description="Original request ID")
    is_valid: bool = Field(description="Whether validation passed")
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)
    info: List[ValidationError] = Field(default_factory=list)
    execution_time_ms: int = Field(description="Validation time in milliseconds")


class ExecutionContext(BaseModel):
    """Context for operation execution."""
    session_id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = Field(default=None)
    working_directory: Path = Field(default_factory=Path.cwd)
    environment: Dict[str, str] = Field(default_factory=dict)
    debug_mode: bool = Field(default=False)
    dry_run: bool = Field(default=False)
    parallel_execution: bool = Field(default=True)
    max_workers: int = Field(default=4)


class ExecutionResult(BaseContract):
    """Generic execution result."""
    context: ExecutionContext = Field(description="Execution context")
    status: ExecutionStatus = Field(description="Execution status")
    output: Any = Field(default=None, description="Operation output")
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    execution_time_ms: int = Field(description="Execution time in milliseconds")
    resource_usage: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Configuration Contracts
# ============================================================================

class WeaverConfig(BaseModel):
    """WeaverGen configuration."""
    weaver_binary_path: Optional[Path] = Field(default=None)
    template_directories: List[Path] = Field(default_factory=list)
    default_language: TargetLanguage = Field(default=TargetLanguage.PYTHON)
    output_directory: Path = Field(default=Path("./generated"))
    validation_level: ValidationLevel = Field(default=ValidationLevel.BASIC)
    parallel_execution: bool = Field(default=True)
    max_workers: int = Field(default=4)
    cache_enabled: bool = Field(default=True)
    cache_directory: Path = Field(default=Path("./.weavergen_cache"))


class TemplateConfig(BaseModel):
    """Template configuration."""
    template_directory: Path = Field(description="Template directory")
    variables: Dict[str, Any] = Field(default_factory=dict)
    includes: List[str] = Field(default_factory=list)
    excludes: List[str] = Field(default_factory=list)
    preprocessing: Dict[str, Any] = Field(default_factory=dict)
    postprocessing: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Plugin Contracts
# ============================================================================

class IPlugin(ABC):
    """Interface for WeaverGen plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        raise NotImplementedError
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin."""
        raise NotImplementedError
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        raise NotImplementedError


class IGenerationPlugin(IPlugin):
    """Interface for code generation plugins."""
    
    @abstractmethod
    def supports_language(self, language: TargetLanguage) -> bool:
        """Check if plugin supports target language."""
        raise NotImplementedError
    
    @abstractmethod
    async def generate(self, request: GenerationRequest, context: ExecutionContext) -> GenerationResult:
        """Generate code for the request."""
        raise NotImplementedError


class IValidationPlugin(IPlugin):
    """Interface for validation plugins."""
    
    @abstractmethod
    def supports_target(self, target: Any) -> bool:
        """Check if plugin can validate the target."""
        raise NotImplementedError
    
    @abstractmethod
    async def validate(self, request: ValidationRequest, context: ExecutionContext) -> ValidationResult:
        """Validate the target."""
        raise NotImplementedError


class ITemplatePlugin(IPlugin):
    """Interface for template plugins."""
    
    @abstractmethod
    def get_templates(self) -> List[TemplateManifest]:
        """Get available templates."""
        raise NotImplementedError
    
    @abstractmethod
    async def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        raise NotImplementedError