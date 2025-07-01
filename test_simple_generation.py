#!/usr/bin/env python3
"""Test the simple 80/20 WeaverGen implementation."""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weavergen.core_simple import WeaverGen, generate_code


async def main():
    """Test simple generation."""
    
    print("🧪 Testing 80/20 WeaverGen Implementation")
    print("=" * 50)
    
    # Initialize generator
    generator = WeaverGen()
    
    # Check requirements
    ready, issues = generator.check_requirements()
    if ready:
        print("✅ Weaver found and ready!")
        print(f"📍 Location: {generator.weaver_path}")
    else:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return
    
    # Test with the sample project we created
    test_project = Path("test-weavergen-project")
    if not test_project.exists():
        print("❌ Test project not found. Run 'weavergen init' first.")
        return
    
    # Use the proper semantic convention format we created
    semantic_file = test_project / "semantic-conventions" / "registry" / "http.yaml"
    
    if not semantic_file.exists():
        print(f"❌ Semantic file not found: {semantic_file}")
        return
    
    print(f"\n📄 Using semantic convention: {semantic_file}")
    print("🎯 Generating for: Python")
    print("📁 Output directory: ./test-output\n")
    
    # Generate code
    result = await generator.generate(
        str(semantic_file),
        ["python"],
        "./test-output"
    )
    
    if result.success:
        print(f"\n✅ Generation successful!")
        print(f"📊 Files generated: {len(result.files_generated)}")
        print(f"⏱️ Time: {result.execution_time:.2f}s")
        
        if result.files_generated:
            print("\n📄 Generated files:")
            for file in result.files_generated:
                print(f"  • {file}")
                
                # Show a snippet of the generated content
                if file.suffix == ".py":
                    content = file.read_text()
                    lines = content.split('\n')[:10]
                    print("    Preview:")
                    for line in lines:
                        if line:
                            print(f"      {line}")
                    if len(content.split('\n')) > 10:
                        print("      ...")
    else:
        print(f"\n❌ Generation failed: {result.error}")
        if result.weaver_output:
            print(f"\nWeaver output:\n{result.weaver_output}")


if __name__ == "__main__":
    asyncio.run(main())