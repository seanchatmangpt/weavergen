#!/usr/bin/env python3
"""
Bootstrap script for Weaver Forge
Generates Weaver Forge from its own semantic conventions
"""

import subprocess
import sys
from pathlib import Path
import shutil
from typing import Optional

class ForgeBootstrap:
    """Bootstrap Weaver Forge from semantic conventions"""
    
    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.semantic_file = base_dir / "weaver_forge.yaml"
        self.template_dir = base_dir / "templates" / "registry" / "python"
        self.output_dir = base_dir / "generated" / "forge"
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check if Weaver is installed
        try:
            result = subprocess.run(
                ["weaver", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("❌ Weaver CLI not found. Please install Weaver.")
                print("   See: https://github.com/open-telemetry/weaver")
                return False
            print(f"✅ Weaver installed: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Weaver CLI not found in PATH")
            return False
        
        # Check if semantic file exists
        if not self.semantic_file.exists():
            print(f"❌ Semantic file not found: {self.semantic_file}")
            print("   Please ensure weaver_forge.yaml exists")
            return False
        print(f"✅ Semantic file found: {self.semantic_file}")
        
        # Check if templates exist
        if not self.template_dir.exists():
            print(f"❌ Template directory not found: {self.template_dir}")
            return False
        
        template_files = list(self.template_dir.glob("*.j2"))
        if not template_files:
            print(f"❌ No template files found in {self.template_dir}")
            return False
        
        print(f"✅ Templates found: {len(template_files)} files")
        for tmpl in template_files:
            print(f"   - {tmpl.name}")
        
        return True
    
    def validate_semantics(self) -> bool:
        """Validate semantic conventions with Weaver"""
        print("\n📋 Validating semantic conventions...")
        
        result = subprocess.run(
            ["weaver", "registry", "check", "-r", str(self.semantic_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Semantic conventions are valid")
            return True
        else:
            print("❌ Semantic validation failed:")
            print(result.stderr or result.stdout)
            return False
    
    def generate_code(self) -> bool:
        """Generate code using Weaver"""
        print(f"\n🔨 Generating code to {self.output_dir}...")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run Weaver generate
        cmd = [
            "weaver", "registry", "generate",
            "--templates", str(self.template_dir.parent.parent),  # Point to templates/ dir
            "--param", f"output={self.output_dir}/",
            "--registry", str(self.semantic_file),
            "python"
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Code generation failed:")
            print(result.stderr or result.stdout)
            return False
        
        print("✅ Code generation complete")
        
        # List generated files
        print("\n📁 Generated files:")
        for py_file in self.output_dir.rglob("*.py"):
            print(f"   - {py_file.relative_to(self.output_dir)}")
        
        return True
    
    def create_init_files(self):
        """Create __init__.py files for Python packages"""
        print("\n📦 Creating package structure...")
        
        for subdir in ["commands", "operations", "runtime", "contracts"]:
            init_file = self.output_dir / subdir / "__init__.py"
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text(f'"""Weaver Forge {subdir} layer"""')
        
        # Create main __init__.py
        main_init = self.output_dir / "__init__.py"
        main_init.write_text('''"""
Weaver Forge - Self-referential code generator
Generated from semantic conventions
"""

from .commands.forge import (
    forge_semantic_generate,
    forge_code_generate,
    forge_self_improve
)

__all__ = [
    "forge_semantic_generate",
    "forge_code_generate", 
    "forge_self_improve"
]
''')
        print("✅ Package structure created")
    
    def test_import(self) -> bool:
        """Test if generated code can be imported"""
        print("\n🧪 Testing import...")
        
        # Add generated directory to Python path
        sys.path.insert(0, str(self.base_dir))
        
        try:
            # Try to import the generated module
            from generated.forge import forge_semantic_generate
            print("✅ Import successful!")
            return True
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            return False
    
    def bootstrap(self) -> bool:
        """Run complete bootstrap process"""
        print("🚀 Bootstrapping Weaver Forge...\n")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Validate semantics
        if not self.validate_semantics():
            return False
        
        # Generate code
        if not self.generate_code():
            return False
        
        # Create package structure
        self.create_init_files()
        
        # Test import
        if not self.test_import():
            return False
        
        print("\n✨ Bootstrap complete! Weaver Forge is ready.")
        print(f"\n📍 Next steps:")
        print(f"   1. cd {self.output_dir}")
        print(f"   2. Implement the operations in operations/forge.py")
        print(f"   3. Use forge_semantic_generate() to generate new semantics")
        print(f"   4. Use forge_self_improve() to enhance Forge itself")
        
        return True
    
    def clean(self):
        """Clean generated files"""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            print(f"🧹 Cleaned: {self.output_dir}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bootstrap Weaver Forge")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean generated files"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("."),
        help="Base directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    bootstrap = ForgeBootstrap(base_dir=args.dir)
    
    if args.clean:
        bootstrap.clean()
    else:
        success = bootstrap.bootstrap()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()