#!/usr/bin/env python3
"""
Quick validation script to check WeaverGen project status
Helps verify what's working before v1 migration
"""

import subprocess
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and report status"""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} NOT FOUND")
        return False

def run_command(cmd, description):
    """Run a command and report success/failure"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False

def main():
    print("WeaverGen Project Status Check")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check project structure
    print("\n📁 Project Structure:")
    for path, desc in [
        ("src/weavergen/__init__.py", "Package initialized"),
        ("src/weavergen/cli.py", "CLI module"),
        ("src/weavergen/core.py", "Core module"),
        ("src/weavergen/models.py", "Models module"),
        ("pyproject.toml", "Project configuration"),
        ("README.md", "Documentation"),
        ("Makefile", "CDCS workflows"),
    ]:
        total_checks += 1
        if check_file_exists(path, desc):
            checks_passed += 1
    
    # Check prototype
    print("\n🧪 Prototype Status:")
    for path, desc in [
        ("prototype/weaver_wrapper.py", "Core wrapper"),
        ("prototype/semantic-generator.py", "Semantic generation"),
        ("prototype/enhanced_cli.py", "Enhanced CLI"),
        ("prototype/roberts_rules_models.py", "Roberts Rules models"),
        ("prototype/semantic_quine_demo.py", "Semantic quine demo"),
        ("prototype/validate_80_20.py", "Validation script"),
    ]:
        total_checks += 1
        if check_file_exists(path, desc):
            checks_passed += 1
    
    # Check documentation
    print("\n📚 Documentation:")
    for path, desc in [
        ("PROTOTYPE_TO_V1_MIGRATION_CHECKLIST.md", "Migration checklist"),
        ("PROTOTYPE_KEY_INNOVATIONS.md", "Key innovations"),
        ("WEAVERGEN_V1_SUMMARY.md", "v1 summary"),
        ("WEAVERGEN_IMPLEMENTATION_PLAN.md", "Implementation plan"),
    ]:
        total_checks += 1
        if check_file_exists(path, desc):
            checks_passed += 1
    
    # Check Python environment
    print("\n🐍 Python Environment:")
    total_checks += 1
    if run_command("python --version", "Python installed"):
        checks_passed += 1
    
    # Summary
    print(f"\n📊 Summary: {checks_passed}/{total_checks} checks passed")
    percentage = (checks_passed / total_checks) * 100 if total_checks > 0 else 0
    
    if percentage == 100:
        print("✅ Project structure looks perfect!")
    elif percentage >= 80:
        print("🟡 Project mostly ready, some files missing")
    else:
        print("🔴 Project needs attention")
    
    print("\n🚀 Next Steps:")
    if Path("prototype/weaver_wrapper.py").exists() and not Path("src/weavergen/core.py").exists():
        print("1. Migrate prototype/weaver_wrapper.py → src/weavergen/core.py")
    if Path("prototype/semantic_generator.py").exists():
        print("2. Migrate prototype/semantic_generator.py → src/weavergen/semantic.py")
    if Path("prototype/enhanced_cli.py").exists():
        print("3. Merge enhanced CLI features into src/weavergen/cli.py")
    
    return 0 if percentage >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())
