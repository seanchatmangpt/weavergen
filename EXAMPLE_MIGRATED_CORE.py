"""Example of how core.py should look after migration - DO NOT USE DIRECTLY, MERGE MANUALLY"""

# This shows the key methods to add from prototype/weaver_wrapper.py

class WeaverGen:
    """Enhanced with prototype functionality"""
    
    # ... existing __init__ and methods ...
    
    def registry_check(self, registry_path: str) -> ValidationResult:
        """Check a semantic convention registry for validity.
        
        Migrated from prototype/weaver_wrapper.py
        """
        try:
            result = self._run_weaver_command([
                "registry", "check", "-r", registry_path
            ])
            
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
        
        Migrated from prototype/weaver_wrapper.py
        """
        cmd = ["registry", "resolve", "-r", registry_path]
        if output_path:
            cmd.extend(["-o", output_path])
        
        result = self._run_weaver_command(cmd)
        
        if output_path and Path(output_path).exists():
            with open(output_path) as f:
                return yaml.safe_load(f)
        return {"success": result.returncode == 0}
    
    def registry_stats(self, registry_path: str) -> Dict[str, Any]:
        """Get statistics about a registry.
        
        Migrated from prototype/weaver_wrapper.py
        """
        result = self._run_weaver_command([
            "registry", "stats", "-r", registry_path
        ])
        
        # Parse stats from output
        stats = {}
        if result.stdout:
            # Parse the stats output format
            for line in result.stdout.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    stats[key.strip()] = value.strip()
        
        return stats
    
    def _create_registry_structure(self, semantic_file: Path) -> Path:
        """Create temporary registry structure for single YAML files.
        
        Migrated from prototype functionality
        """
        with tempfile.TemporaryDirectory() as temp_dir:
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