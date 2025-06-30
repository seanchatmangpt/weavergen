#!/usr/bin/env python3
"""
Comprehensive validation of the WeaverGen CLI
Tests every command to ensure all prototype functionality is accessible
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, 'src')

# Track results
results = {
    "timestamp": datetime.now().isoformat(),
    "total_commands": 0,
    "passed": 0,
    "failed": 0,
    "commands": {}
}

def test_command(name: str, cmd: list, check_output: bool = True) -> bool:
    """Test a CLI command and record result"""
    results["total_commands"] += 1
    
    print(f"\n🧪 Testing: {name}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        
        if success:
            print(f"   ✅ PASSED")
            results["passed"] += 1
            status = "passed"
            
            # Show relevant output
            if check_output and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[:5]:  # Show first 5 lines
                    print(f"      {line}")
                if len(lines) > 5:
                    print(f"      ... ({len(lines)-5} more lines)")
        else:
            print(f"   ❌ FAILED")
            results["failed"] += 1
            status = "failed"
            
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
        
        results["commands"][name] = {
            "command": ' '.join(cmd),
            "status": status,
            "return_code": result.returncode,
            "has_output": bool(result.stdout)
        }
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  TIMEOUT")
        results["failed"] += 1
        results["commands"][name] = {
            "command": ' '.join(cmd),
            "status": "timeout",
            "return_code": -1,
            "has_output": False
        }
        return False
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        results["failed"] += 1
        results["commands"][name] = {
            "command": ' '.join(cmd),
            "status": "error",
            "return_code": -1,
            "has_output": False,
            "error": str(e)
        }
        return False


def main():
    """Run all CLI validation tests"""
    print("🚀 WeaverGen Comprehensive CLI Validation")
    print("=" * 60)
    
    # Check if running from src/weavergen directory
    cli_path = Path("src/weavergen/cli_comprehensive_mock.py")
    if not cli_path.exists():
        print(f"❌ CLI not found at {cli_path}")
        print("   Please run from the weavergen root directory")
        return
    
    # Base command
    base_cmd = [sys.executable, str(cli_path)]
    
    # ========== Main Commands ==========
    print("\n📋 Testing Main Commands")
    print("-" * 40)
    
    test_command(
        "status",
        base_cmd + ["status"]
    )
    
    test_command(
        "version",
        base_cmd + ["version"]
    )
    
    test_command(
        "init",
        base_cmd + ["init", "test_project", "--examples"]
    )
    
    test_command(
        "export",
        base_cmd + ["export", "--format", "json", "--output", "test_export"]
    )
    
    test_command(
        "clean",
        base_cmd + ["clean", "--force"]
    )
    
    # ========== Generate Commands ==========
    print("\n🚀 Testing Generate Commands")
    print("-" * 40)
    
    # Create test semantic file
    test_semantic = Path("test_semantic.yaml")
    test_semantic.write_text("""groups:
  - id: test.service
    type: span
    brief: Test service
    stability: experimental
    attributes:
      - id: test.service.name
        type: string
        requirement_level: required
        brief: Service name""")
    
    test_command(
        "generate forge",
        base_cmd + ["generate", "forge", str(test_semantic)]
    )
    
    test_command(
        "generate models",
        base_cmd + ["generate", "models"]
    )
    
    test_command(
        "generate roberts",
        base_cmd + ["generate", "roberts"]
    )
    
    # ========== Validate Commands ==========
    print("\n✅ Testing Validate Commands")
    print("-" * 40)
    
    test_command(
        "validate all",
        base_cmd + ["validate", "all", "--no-concurrent"]
    )
    
    test_command(
        "validate quine",
        base_cmd + ["validate", "quine"]
    )
    
    test_command(
        "validate otel",
        base_cmd + ["validate", "otel"]
    )
    
    # ========== Agent Commands ==========
    print("\n🤖 Testing Agent Commands")
    print("-" * 40)
    
    test_command(
        "agents communicate",
        base_cmd + ["agents", "communicate", "--mode", "otel", "--agents", "3"]
    )
    
    test_command(
        "agents analyze",
        base_cmd + ["agents", "analyze", str(test_semantic)]
    )
    
    # ========== Meeting Commands ==========
    print("\n🏛️ Testing Meeting Commands")
    print("-" * 40)
    
    test_command(
        "meeting roberts",
        base_cmd + ["meeting", "roberts", "--topic", "Test Meeting"]
    )
    
    test_command(
        "meeting scrum",
        base_cmd + ["meeting", "scrum", "--teams", "3"]
    )
    
    test_command(
        "meeting dev",
        base_cmd + ["meeting", "dev"]
    )
    
    # ========== Benchmark Commands ==========
    print("\n⚡ Testing Benchmark Commands")
    print("-" * 40)
    
    test_command(
        "benchmark ollama",
        base_cmd + ["benchmark", "ollama", "--model", "qwen3:latest"],
        check_output=False  # May timeout
    )
    
    test_command(
        "benchmark concurrent",
        base_cmd + ["benchmark", "concurrent"]
    )
    
    # ========== Demo Commands ==========
    print("\n🎭 Testing Demo Commands")
    print("-" * 40)
    
    test_command(
        "demo quine",
        base_cmd + ["demo", "quine"]
    )
    
    test_command(
        "demo full",
        base_cmd + ["demo", "full"],
        check_output=False  # Long running
    )
    
    # ========== Semantic Commands ==========
    print("\n🧠 Testing Semantic Commands")
    print("-" * 40)
    
    test_command(
        "semantic generate",
        base_cmd + ["semantic", "generate", "test service", "--output", "test_gen.yaml", "--no-validate"]
    )
    
    # Cleanup
    test_semantic.unlink(missing_ok=True)
    Path("test_gen.yaml").unlink(missing_ok=True)
    Path("test_export.json").unlink(missing_ok=True)
    
    # ========== Summary ==========
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"Total Commands Tested: {results['total_commands']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed'] / results['total_commands'] * 100):.1f}%")
    
    # Save detailed results
    with open("cli_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: cli_validation_results.json")
    
    # Show failed commands
    if results["failed"] > 0:
        print("\n❌ Failed Commands:")
        for name, info in results["commands"].items():
            if info["status"] != "passed":
                print(f"  - {name}: {info['status']}")
    
    # Create Mermaid diagram
    print("\n📊 Mermaid Validation Report:")
    print("```mermaid")
    print("graph TB")
    print(f'    Total["Total Commands: {results["total_commands"]}"]')
    print(f'    Passed["✅ Passed: {results["passed"]}"]')
    print(f'    Failed["❌ Failed: {results["failed"]}"]')
    print("    ")
    print("    Total --> Passed")
    print("    Total --> Failed")
    print("    ")
    
    # Group results by category
    categories = {
        "Main": ["status", "version", "init", "export", "clean"],
        "Generate": ["generate forge", "generate models", "generate roberts"],
        "Validate": ["validate all", "validate quine", "validate otel"],
        "Agents": ["agents communicate", "agents analyze"],
        "Meeting": ["meeting roberts", "meeting scrum", "meeting dev"],
        "Benchmark": ["benchmark ollama", "benchmark concurrent"],
        "Demo": ["demo quine", "demo full"],
        "Semantic": ["semantic generate"]
    }
    
    for cat, cmds in categories.items():
        passed_in_cat = sum(1 for c in cmds if c in results["commands"] and results["commands"][c]["status"] == "passed")
        total_in_cat = len(cmds)
        status = "✅" if passed_in_cat == total_in_cat else "⚠️"
        print(f'    {cat}["{cat}<br/>{passed_in_cat}/{total_in_cat} {status}"]')
        print(f"    Passed --> {cat}")
    
    print("    ")
    print("    style Total fill:#4CAF50")
    print("    style Passed fill:#90EE90")
    print("    style Failed fill:#FFB6C1")
    print("```")
    
    # Final verdict
    print("\n🎯 FINAL VERDICT:")
    if results["passed"] == results["total_commands"]:
        print("✅ ALL COMMANDS PASSED! The CLI can perform all prototype tasks!")
    elif results["passed"] >= results["total_commands"] * 0.8:
        print("⚠️  Most commands passed. The CLI is mostly functional.")
    else:
        print("❌ Many commands failed. The CLI needs work.")
    
    return results["passed"] == results["total_commands"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)