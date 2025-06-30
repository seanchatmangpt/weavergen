#!/usr/bin/env python3
"""
Test Weaver CLI commands to understand how Weaver Forge works
"""

from weaver_wrapper import WeaverWrapper
from pathlib import Path

def main():
    print("🧪 Testing Weaver CLI Commands")
    print("=" * 50)
    
    weaver = WeaverWrapper()
    
    # Test 1: Check our test registry
    print("\n### Test 1: Check test_registry ###")
    result = weaver.registry_check("test_registry")
    print(f"Return code: {result.returncode}")
    
    # Test 2: Resolve the registry to see what it produces
    print("\n### Test 2: Resolve test_registry ###")
    result = weaver.registry_resolve("test_registry", output="resolved_registry.yaml")
    print(f"Return code: {result.returncode}")
    
    # Test 3: Check what's in the resolved file
    if Path("resolved_registry.yaml").exists():
        print("\n📄 Resolved registry content:")
        with open("resolved_registry.yaml") as f:
            print(f.read()[:500] + "..." if len(f.read()) > 500 else f.read())
    
    # Test 4: Try to generate with our templates
    print("\n### Test 3: Generate from test_registry ###")
    result = weaver.registry_generate(
        registry_path="test_registry",
        templates="templates",
        target="python",
        output="weaver_output"
    )
    print(f"Return code: {result.returncode}")
    
    # Test 5: List what was generated
    output_dir = Path("weaver_output")
    if output_dir.exists():
        print("\n📁 Generated files:")
        for file in output_dir.rglob("*"):
            if file.is_file():
                print(f"  - {file.relative_to(output_dir)}")
    
    # Test 6: Check a single YAML file directly
    print("\n### Test 4: Check single YAML file ###")
    result = weaver.registry_check("weaver-forge.yaml")
    print(f"Return code: {result.returncode}")
    
    # Test 7: Get registry stats
    print("\n### Test 5: Registry stats ###")
    result = weaver.registry_stats("test_registry")
    print(f"Return code: {result.returncode}")
    
    # Test 8: Check help for generate command
    print("\n### Test 6: Help for generate command ###")
    result = weaver.help("registry generate")
    print(f"Return code: {result.returncode}")

if __name__ == "__main__":
    main()