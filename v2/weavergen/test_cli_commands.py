#!/usr/bin/env python3
"""Test script to run CLI commands and validate their spans."""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def run_command(cmd: List[str]) -> Dict[str, Any]:
    """Run a command and capture output."""
    print(f"\n🔵 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    output = {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "span": None
    }
    
    # Try to extract span JSON from output
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        # Look for JSON span data (starts with {)
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                try:
                    # Join all remaining lines and parse as JSON
                    json_str = '\n'.join(lines[i:])
                    output["span"] = json.loads(json_str)
                    break
                except json.JSONDecodeError:
                    pass
    
    return output

def validate_span(span: Dict[str, Any], expected_name: str) -> bool:
    """Validate span has expected properties."""
    if not span:
        return False
    
    checks = []
    checks.append(("name", span.get("name") == expected_name))
    checks.append(("trace_id", bool(span.get("context", {}).get("trace_id"))))
    checks.append(("span_id", bool(span.get("context", {}).get("span_id"))))
    checks.append(("start_time", bool(span.get("start_time"))))
    checks.append(("end_time", bool(span.get("end_time"))))
    checks.append(("resource", bool(span.get("resource"))))
    
    all_passed = all(check[1] for check in checks)
    
    if not all_passed:
        print(f"❌ Span validation failed for {expected_name}:")
        for check_name, passed in checks:
            if not passed:
                print(f"   - Missing or invalid: {check_name}")
    
    return all_passed

def main():
    """Run commands and validate spans."""
    test_file = Path("/Users/sac/dev/weavergen/v2/weavergen/test_semantic.yaml")
    
    commands = [
        # Validate commands
        (["uv", "run", "weavergen", "validate", "semantic", str(test_file)], "validate.semantic"),
        
        # Agent commands
        (["uv", "run", "weavergen", "agents", "communicate", str(test_file), "--agents", "2", "--rounds", "2"], "agents.communicate"),
        (["uv", "run", "weavergen", "agents", "validate", str(test_file), "--agents", "3"], "agents.validate"),
        
        # BPMN commands
        (["uv", "run", "weavergen", "bpmn", "list"], "bpmn.list"),
        
        # Template commands
        (["uv", "run", "weavergen", "templates", "list"], "templates.list"),
        
        # Debug commands (showing health check)
        (["uv", "run", "weavergen", "debug", "health"], "debug.health"),
    ]
    
    results = []
    
    print("=" * 60)
    print("WeaverGen v2 CLI Command Testing")
    print("=" * 60)
    
    for cmd, expected_span_name in commands:
        result = run_command(cmd)
        
        # Check if command succeeded
        if result["returncode"] != 0:
            print(f"❌ Command failed with code {result['returncode']}")
            if result["stderr"]:
                print(f"   Error: {result['stderr']}")
        else:
            print(f"✅ Command succeeded")
            
            # Validate span if present
            if result["span"]:
                if validate_span(result["span"], expected_span_name):
                    print(f"✅ Span validation passed")
                    # Print key span attributes
                    attrs = result["span"].get("attributes", {})
                    if attrs:
                        print(f"   Attributes: {attrs}")
            else:
                print(f"⚠️  No span data found in output")
        
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total = len(results)
    succeeded = sum(1 for r in results if r["returncode"] == 0)
    with_spans = sum(1 for r in results if r["span"] is not None)
    
    print(f"Commands run: {total}")
    print(f"Succeeded: {succeeded}/{total}")
    print(f"With valid spans: {with_spans}/{total}")
    
    # Display span summary in Mermaid format
    print("\n📊 Span Flow Diagram:")
    print("```mermaid")
    print("graph LR")
    for i, result in enumerate(results):
        if result["span"]:
            span_name = result["span"]["name"]
            print(f"    S{i}[{span_name}]")
            if i > 0:
                print(f"    S{i-1} --> S{i}")
    print("```")
    
    return succeeded == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)