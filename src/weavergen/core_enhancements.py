"""Enhanced core functionality to add to WeaverGen.

This file shows the methods that need to be added to core.py
"""

import yaml
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from .models import ValidationResult, TemplateInfo


class CoreEnhancements:
    """Methods to add to the WeaverGen class in core.py"""
    
    def _find_weaver_binary(self) -> Optional[Path]:
        """Find the Weaver binary."""
        # Try configured path first
        if self._weaver_config.weaver_path and self._weaver_config.weaver_path.exists():
            return self._weaver_config.weaver_path
        
        # Try PATH
        weaver_path = shutil.which("weaver")
        if weaver_path:
            return Path(weaver_path)
        
        # Check common locations
        common_paths = [
            Path.home() / ".cargo" / "bin" / "weaver",
            Path("/usr/local/bin/weaver"),
            Path("/opt/homebrew/bin/weaver"),
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        return None
    
    def get_weaver_info(self) -> Dict[str, str]:
        """Get information about the Weaver binary."""
        weaver_path = self._find_weaver_binary()
        if not weaver_path:
            raise WeaverNotFoundError("Weaver binary not found")
        
        # Get version
        import subprocess
        result = subprocess.run(
            [str(weaver_path), "--version"],
            capture_output=True,
            text=True
        )
        
        version = result.stdout.strip() if result.returncode == 0 else "unknown"
        
        return {
            "path": str(weaver_path),
            "version": version
        }
    
    def list_templates(self, language_filter: Optional[str] = None) -> List[TemplateInfo]:
        """List available templates.
        
        Args:
            language_filter: Filter by language
            
        Returns:
            List of available templates
        """
        templates = []
        
        # Check built-in templates
        builtin_path = Path(__file__).parent / "templates"
        if builtin_path.exists():
            for lang_dir in builtin_path.iterdir():
                if lang_dir.is_dir():
                    if language_filter and lang_dir.name != language_filter:
                        continue
                    
                    # Read weaver.yaml for template info
                    weaver_yaml = lang_dir / "weaver.yaml"
                    if weaver_yaml.exists():
                        with open(weaver_yaml) as f:
                            data = yaml.safe_load(f)
                        
                        templates.append(TemplateInfo(
                            name=lang_dir.name,
                            language=lang_dir.name,
                            description=data.get("description", "No description"),
                            version=data.get("version", "1.0.0"),
                            path=lang_dir
                        ))
        
        # Check custom templates
        if self.config and self.config.template_dir:
            custom_path = self.config.template_dir
            if custom_path.exists():
                # Similar logic for custom templates
                pass
        
        return templates
    
    def registry_check(self, registry_path: str) -> ValidationResult:
        """Check a semantic convention registry for validity.
        
        Args:
            registry_path: Path to registry
            
        Returns:
            Validation result
        """
        from .models import WeaverCommand
        
        command = WeaverCommand(
            command="weaver",
            args=["registry", "check", "-r", registry_path],
        )
        
        try:
            result = self._run_weaver_command(command)
            
            return ValidationResult(
                valid=result.returncode == 0,
                errors=result.stderr.splitlines() if result.stderr else [],
                warnings=[],
                checked_files=[registry_path]
            )
        except Exception as e:
            raise WeaverGenError(f"Registry check failed: {e}")
    
    def registry_resolve(self, registry_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Resolve a semantic convention registry.
        
        Args:
            registry_path: Path to registry
            output_path: Optional output path for resolved registry
            
        Returns:
            Resolved registry data
        """
        from .models import WeaverCommand
        
        cmd_args = ["registry", "resolve", "-r", registry_path]
        if output_path:
            cmd_args.extend(["-o", output_path])
        
        command = WeaverCommand(
            command="weaver",
            args=cmd_args,
        )
        
        result = self._run_weaver_command(command)
        
        if output_path and Path(output_path).exists():
            with open(output_path) as f:
                return yaml.safe_load(f)
        return {"success": result.returncode == 0}
    
    def registry_stats(self, registry_path: str) -> Dict[str, Any]:
        """Get statistics about a registry.
        
        Args:
            registry_path: Path to registry
            
        Returns:
            Registry statistics
        """
        from .models import WeaverCommand
        
        command = WeaverCommand(
            command="weaver",
            args=["registry", "stats", "-r", registry_path],
        )
        
        result = self._run_weaver_command(command)
        
        # Parse stats from output
        stats = {}
        if result.stdout:
            for line in result.stdout.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    stats[key.strip()] = value.strip()
        
        return stats
    
    def _create_registry_structure(self, semantic_file: Path) -> Path:
        """Create temporary registry structure for single YAML files.
        
        Args:
            semantic_file: Path to semantic YAML file
            
        Returns:
            Path to temporary registry
        """
        temp_dir = tempfile.mkdtemp()
        registry_dir = Path(temp_dir) / "registry"
        groups_dir = registry_dir / "groups"
        groups_dir.mkdir(parents=True)
        
        # Copy semantic file to groups directory
        target = groups_dir / semantic_file.name
        shutil.copy(semantic_file, target)
        
        # Create registry manifest
        manifest = {
            "registry": {
                "groups": [str(semantic_file.name)]
            }
        }
        
        manifest_path = registry_dir / "registry_manifest.yaml"
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f)
        
        return registry_dir