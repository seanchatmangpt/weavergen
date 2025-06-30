"""Tests for semantic convention generation."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from weavergen.semantic import (
    SemanticGenerator,
    SemanticConvention,
    Group,
    Attribute,
    GroupType,
    AttributeType,
    RequirementLevel,
    Stability,
)


@pytest.fixture
def mock_ai_response():
    """Mock AI response for semantic generation."""
    return SemanticConvention(
        groups=[
            Group(
                id="test.service",
                type=GroupType.ATTRIBUTE_GROUP,
                brief="Test service attributes",
                stability=Stability.EXPERIMENTAL,
                attributes=[
                    Attribute(
                        id="test.service.name",
                        type=AttributeType.STRING,
                        requirement_level=RequirementLevel.REQUIRED,
                        brief="Service name",
                        examples=["auth-service", "payment-service"]
                    )
                ]
            ),
            Group(
                id="test.operation",
                type=GroupType.SPAN,
                extends="test.service",
                brief="Test operation span",
                stability=Stability.EXPERIMENTAL,
                attributes=[
                    Attribute(
                        id="test.operation.type",
                        type=AttributeType.STRING,
                        requirement_level=RequirementLevel.RECOMMENDED,
                        brief="Operation type",
                        examples=["create", "read", "update", "delete"]
                    )
                ]
            )
        ]
    )


class TestSemanticGenerator:
    """Test semantic convention generation."""
    
    @pytest.mark.asyncio
    async def test_generate_semantic_convention(self, mock_ai_response):
        """Test generating semantic convention from description."""
        generator = SemanticGenerator(model="gpt-4o", use_ollama=False)
        
        # Mock the agent
        mock_result = Mock()
        mock_result.data = mock_ai_response
        
        with patch.object(generator.agent, 'run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result
            
            convention = await generator.generate("Test service with CRUD operations")
            
            assert len(convention.groups) == 2
            assert convention.groups[0].id == "test.service"
            assert convention.groups[0].type == GroupType.ATTRIBUTE_GROUP
            assert convention.groups[1].id == "test.operation"
            assert convention.groups[1].type == GroupType.SPAN
    
    def test_save_to_yaml(self, tmp_path, mock_ai_response):
        """Test saving semantic convention to YAML."""
        generator = SemanticGenerator()
        output_file = tmp_path / "test_semantic.yaml"
        
        generator.save_to_yaml(mock_ai_response, output_file)
        
        assert output_file.exists()
        
        # Verify YAML content
        import yaml
        with open(output_file) as f:
            data = yaml.safe_load(f)
        
        assert "groups" in data
        assert len(data["groups"]) == 2
        assert data["groups"][0]["id"] == "test.service"
        assert data["groups"][0]["type"] == "attribute_group"
        assert data["groups"][1]["extends"] == "test.service"
    
    def test_validate_semantic_valid(self, tmp_path):
        """Test validating a valid semantic convention."""
        generator = SemanticGenerator()
        
        # Create valid YAML
        valid_yaml = tmp_path / "valid.yaml"
        valid_content = """
groups:
  - id: test.service
    type: attribute_group
    brief: Test service
    stability: experimental
    attributes:
      - id: test.service.name
        type: string
        requirement_level: required
        brief: Service name
"""
        valid_yaml.write_text(valid_content)
        
        result = generator.validate_semantic(valid_yaml)
        
        assert result.valid
        assert len(result.errors) == 0
    
    def test_validate_semantic_invalid(self, tmp_path):
        """Test validating an invalid semantic convention."""
        generator = SemanticGenerator()
        
        # Create invalid YAML (missing required fields)
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_content = """
groups:
  - id: test.service
    # Missing type field
    brief: Test service
    attributes:
      - id: test.service.name
        # Missing type field
        brief: Service name
"""
        invalid_yaml.write_text(invalid_content)
        
        result = generator.validate_semantic(invalid_yaml)
        
        assert not result.valid
        assert len(result.errors) > 0
        assert any("missing required 'type' field" in error for error in result.errors)
    
    def test_validate_semantic_invalid_type(self, tmp_path):
        """Test validating semantic with invalid attribute type."""
        generator = SemanticGenerator()
        
        invalid_yaml = tmp_path / "invalid_type.yaml"
        invalid_content = """
groups:
  - id: test.service
    type: span
    brief: Test service
    attributes:
      - id: test.service.name
        type: invalid_type
        brief: Service name
"""
        invalid_yaml.write_text(invalid_content)
        
        result = generator.validate_semantic(invalid_yaml)
        
        assert not result.valid
        assert any("invalid type: invalid_type" in error for error in result.errors)


class TestSemanticModels:
    """Test semantic convention Pydantic models."""
    
    def test_attribute_model(self):
        """Test Attribute model validation."""
        attr = Attribute(
            id="test.attribute",
            type=AttributeType.STRING,
            brief="Test attribute"
        )
        
        assert attr.id == "test.attribute"
        assert attr.type == AttributeType.STRING
        assert attr.requirement_level == RequirementLevel.RECOMMENDED  # default
    
    def test_group_model(self):
        """Test Group model validation."""
        group = Group(
            id="test.group",
            type=GroupType.SPAN,
            brief="Test group"
        )
        
        assert group.id == "test.group"
        assert group.type == GroupType.SPAN
        assert group.stability == Stability.EXPERIMENTAL  # default
    
    def test_semantic_convention_model(self):
        """Test SemanticConvention model validation."""
        convention = SemanticConvention(
            groups=[
                Group(
                    id="test.group",
                    type=GroupType.SPAN,
                    brief="Test group"
                )
            ]
        )
        
        assert len(convention.groups) == 1
        assert convention.groups[0].id == "test.group"