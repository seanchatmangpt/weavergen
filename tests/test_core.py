"""Tests for WeaverGen core functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from weavergen.core import WeaverGen, WeaverGenError, WeaverNotFoundError
from weavergen.models import GenerationConfig, WeaverConfig


class TestWeaverGen:
    """Test cases for WeaverGen class."""
    
    def test_init_with_config(self):
        """Test WeaverGen initialization with configuration."""
        config = GenerationConfig(
            registry_url="https://example.com/registry",
            language="python"
        )
        
        with patch.object(WeaverGen, '_ensure_weaver_binary'):
            weaver = WeaverGen(config)
            assert weaver.config == config
    
    def test_init_without_config(self):
        """Test WeaverGen initialization without configuration."""
        with patch.object(WeaverGen, '_ensure_weaver_binary'):
            weaver = WeaverGen()
            assert weaver.config is None
    
    @patch('shutil.which')
    def test_ensure_weaver_binary_found_in_path(self, mock_which):
        """Test finding weaver binary in PATH."""
        mock_which.return_value = "/usr/local/bin/weaver"
        
        weaver = WeaverGen()
        assert weaver._weaver_config.weaver_path == Path("/usr/local/bin/weaver")
    
    @patch('shutil.which')
    def test_ensure_weaver_binary_not_found(self, mock_which):
        """Test error when weaver binary is not found."""
        mock_which.return_value = None
        
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(WeaverNotFoundError):
                WeaverGen()
    
    def test_generation_config_validation(self):
        """Test GenerationConfig validation."""
        config = GenerationConfig(
            registry_url="https://example.com/registry",
            output_dir="./output",
            language="python"
        )
        
        assert isinstance(config.output_dir, Path)
        assert config.language == "python"
    
    def test_weaver_config_defaults(self):
        """Test WeaverConfig default values."""
        config = WeaverConfig()
        
        assert config.cache_dir == Path.home() / ".weavergen" / "cache"
        assert config.weaver_path is None
        assert config.template_dir is None


class TestGenerationConfig:
    """Test cases for GenerationConfig model."""
    
    def test_valid_config(self):
        """Test valid configuration creation."""
        config = GenerationConfig(
            registry_url="https://github.com/open-telemetry/semantic-conventions.git",
            output_dir=Path("./generated"),
            language="python"
        )
        
        assert config.registry_url.startswith("https://")
        assert isinstance(config.output_dir, Path)
        assert config.language == "python"
    
    def test_path_conversion(self):
        """Test automatic path conversion."""
        config = GenerationConfig(
            registry_url="file:///local/registry",
            output_dir="./string_path",
            template_dir="./template_string"
        )
        
        assert isinstance(config.output_dir, Path)
        assert isinstance(config.template_dir, Path)
    
    def test_default_values(self):
        """Test default configuration values."""
        config = GenerationConfig(registry_url="test://url")
        
        assert config.output_dir == Path("./generated")
        assert config.language == "python"
        assert config.force is False
        assert config.verbose is False


# Integration tests would go here if we had access to actual weaver binary
@pytest.mark.integration
class TestWeaverGenIntegration:
    """Integration tests requiring actual weaver binary."""
    
    @pytest.mark.skip(reason="Requires weaver binary installation")
    def test_generate_from_real_registry(self):
        """Test generating code from real semantic convention registry."""
        config = GenerationConfig(
            registry_url="https://github.com/open-telemetry/semantic-conventions.git",
            output_dir=Path("./test_output"),
            language="python"
        )
        
        weaver = WeaverGen(config)
        result = weaver.generate()
        
        assert result.success
        assert len(result.files) > 0
    
    @pytest.mark.skip(reason="Requires weaver binary installation")
    def test_validate_real_registry(self):
        """Test validating real semantic convention registry."""
        weaver = WeaverGen()
        result = weaver.validate_registry(
            Path("./test_registry"),
            strict=True
        )
        
        assert result.valid or len(result.errors) > 0  # Either valid or has specific errors
