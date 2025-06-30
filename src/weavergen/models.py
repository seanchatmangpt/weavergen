"""Data models for WeaverGen."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class GenerationConfig(BaseModel):
    """Configuration for code generation."""
    
    registry_url: str = Field(..., description="URL or path to semantic convention registry")
    output_dir: Path = Field(default=Path("./generated"), description="Output directory")
    language: str = Field(default="python", description="Target language")
    template_dir: Optional[Path] = Field(None, description="Custom template directory")
    force: bool = Field(default=False, description="Overwrite existing files")
    verbose: bool = Field(default=False, description="Enable verbose output")
    
    @field_validator("output_dir", mode="before")
    @classmethod
    def ensure_path(cls, v):
        return Path(v) if not isinstance(v, Path) else v
    
    @field_validator("template_dir", mode="before")
    @classmethod
    def ensure_template_path(cls, v):
        return Path(v) if v and not isinstance(v, Path) else v


class FileInfo(BaseModel):
    """Information about a generated file."""
    
    path: Path
    size: int
    file_type: str
    
    @property
    def size_formatted(self) -> str:
        """Human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} TB"


class GenerationResult(BaseModel):
    """Result of code generation operation."""
    
    success: bool
    files: List[FileInfo] = Field(default_factory=list)
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    duration_seconds: float = 0.0


class ValidationResult(BaseModel):
    """Result of registry validation."""
    
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class TemplateInfo(BaseModel):
    """Information about an available template."""
    
    name: str
    language: str
    description: str
    version: str
    path: Path


class WeaverConfig(BaseModel):
    """WeaverGen configuration."""
    
    weaver_path: Optional[Path] = None
    template_dir: Optional[Path] = None
    cache_dir: Path = Field(default=Path.home() / ".weavergen" / "cache")
    
    @field_validator("weaver_path", "template_dir", "cache_dir", mode="before")
    @classmethod
    def ensure_paths(cls, v):
        return Path(v) if v and not isinstance(v, Path) else v


class SemanticConvention(BaseModel):
    """Semantic convention definition."""
    
    id: str
    brief: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    note: Optional[str] = None
    stability: str = "experimental"


class Registry(BaseModel):
    """Semantic convention registry."""
    
    schema_url: str
    groups: List[SemanticConvention] = Field(default_factory=list)
    version: str = "1.0.0"


class WeaverCommand(BaseModel):
    """Represents a command to execute via OTel Weaver."""
    
    command: str
    args: List[str] = Field(default_factory=list)
    cwd: Optional[Path] = None
    env: Dict[str, str] = Field(default_factory=dict)
    
    def to_command_list(self) -> List[str]:
        """Convert to command list for subprocess execution."""
        return [self.command] + self.args
