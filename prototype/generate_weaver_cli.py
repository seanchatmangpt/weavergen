#!/usr/bin/env python3
"""
Generate Weaver CLI from semantic conventions.

This demonstrates generating a complete CLI from semantic definitions.
"""

import subprocess
import os
import sys
from pathlib import Path
import yaml

def create_temp_registry():
    """Create a temporary registry with our Weaver CLI semantics."""
    import tempfile
    import shutil
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="weaver_cli_gen_"))
    
    # Create registry structure
    registry_dir = temp_dir / "registry"
    groups_dir = registry_dir / "groups"
    groups_dir.mkdir(parents=True)
    
    # Copy our CLI semantics
    shutil.copy2("weaver-cli-semantics.yaml", groups_dir / "weaver-cli.yaml")
    
    # Create registry manifest
    manifest = {
        "name": "weaver-cli-registry",
        "semconv_version": "1.0.0", 
        "schema_base_url": "https://opentelemetry.io/schemas",
        "groups": ["groups/"]
    }
    
    manifest_path = registry_dir / "registry_manifest.yaml"
    manifest_path.write_text(yaml.dump(manifest))
    
    return registry_dir

def generate_cli_from_semantics():
    """Generate Weaver CLI from semantic conventions."""
    print("=== Generating Weaver CLI from Semantic Conventions ===\n")
    
    # Create temporary registry
    print("1. Creating temporary registry with CLI semantics...")
    registry_path = create_temp_registry()
    print(f"   ✓ Created registry at {registry_path}")
    
    # Generate using Weaver
    print("\n2. Generating CLI implementation...")
    output_dir = Path("generated_cli")
    output_dir.mkdir(exist_ok=True)
    
    cmd = [
        "weaver", "registry", "generate", "python",
        "--registry", str(registry_path),
        "--templates", "templates",
        "--param", f"output={output_dir}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ Successfully generated CLI")
            
            # Check generated files
            generated_file = output_dir / "weaver_cli_generated.py"
            if generated_file.exists():
                print(f"   ✓ Generated: {generated_file}")
                
                # Make it executable
                generated_file.chmod(0o755)
                
                # Show usage
                print("\n3. Generated CLI Usage:")
                print("   python generated_cli/weaver_cli_generated.py --help")
                print("   python generated_cli/weaver_cli_generated.py check test_registry2")
                print("   python generated_cli/weaver_cli_generated.py generate python test_registry2")
                
                return True
            else:
                print("   ✗ Generated file not found")
                return False
        else:
            print(f"   ✗ Generation failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("   ✗ Weaver CLI not found. Install with: cargo install weaver")
        return False
    finally:
        # Cleanup temp registry
        import shutil
        shutil.rmtree(registry_path.parent, ignore_errors=True)

def verify_generated_cli():
    """Verify the generated CLI works."""
    print("\n=== Verifying Generated CLI ===\n")
    
    cli_path = Path("generated_cli/weaver_cli_generated.py")
    if not cli_path.exists():
        print("✗ Generated CLI not found")
        return False
    
    # Test help command
    print("1. Testing help command...")
    result = subprocess.run(
        [sys.executable, str(cli_path), "--help"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✓ Help command works")
        # Check for expected commands
        expected_commands = ["check", "generate", "resolve", "stats"]
        found = sum(1 for cmd in expected_commands if cmd in result.stdout)
        print(f"   ✓ Found {found}/{len(expected_commands)} expected commands")
        return found == len(expected_commands)
    else:
        print(f"   ✗ Help command failed: {result.stderr}")
        return False

def show_semantic_driven_workflow():
    """Show the complete semantic-driven workflow."""
    print("\n" + "=" * 60)
    print("SEMANTIC-DRIVEN CLI GENERATION WORKFLOW")
    print("=" * 60 + "\n")
    
    print("1. Define CLI commands as semantic conventions (weaver-cli-semantics.yaml)")
    print("2. Create Jinja2 template that generates CLI from semantics (weaver_cli.j2)")
    print("3. Use Weaver to generate the CLI implementation")
    print("4. Result: Fully functional CLI with OTEL instrumentation")
    
    print("\nThis demonstrates:")
    print("✓ Commands defined declaratively in YAML")
    print("✓ Implementation generated from definitions")
    print("✓ Built-in observability from semantic conventions")
    print("✓ 80/20 coverage of Weaver functionality")

def main():
    """Run the complete generation workflow."""
    
    # Generate CLI
    success = generate_cli_from_semantics()
    
    if success:
        # Verify it works
        if verify_generated_cli():
            print("\n✅ Successfully generated working Weaver CLI from semantic conventions!")
            show_semantic_driven_workflow()
        else:
            print("\n⚠️  Generated CLI has issues")
    else:
        print("\n❌ Failed to generate CLI")
        
        # Try with mock generation
        print("\nFalling back to mock generation...")
        
        # Read semantic file
        with open("weaver-cli-semantics.yaml") as f:
            semantics = yaml.safe_load(f)
        
        # Create mock template context
        mock_ctx = semantics.get("groups", [])
        
        # Read template
        template_path = Path("templates/registry/python/weaver_cli.j2")
        if template_path.exists():
            from jinja2 import Template
            
            template_content = template_path.read_text()
            template = Template(template_content)
            
            # Mock template object
            class MockTemplate:
                def set_file_name(self, name):
                    return ""
            
            # Render
            rendered = template.render(ctx=mock_ctx, template=MockTemplate())
            
            # Write output
            output_dir = Path("generated_cli")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / "weaver_cli_generated.py"
            output_file.write_text(rendered)
            output_file.chmod(0o755)
            
            print(f"✓ Created mock-generated CLI at {output_file}")
            verify_generated_cli()

if __name__ == "__main__":
    main()