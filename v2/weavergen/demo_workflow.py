#!/usr/bin/env python
"""Demo script for WeaverGen v2 workflow subcommand."""

import sys
import subprocess
import time

def run_command(cmd):
    """Run a command and show output."""
    print(f"\n📍 Running: {' '.join(cmd)}")
    print("─" * 60)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def main():
    print("🚀 WeaverGen v2 Workflow Subcommand Demo")
    print("=" * 60)
    
    # Show help
    if not run_command(["uv", "run", "weavergen", "workflow", "--help"]):
        print("Failed to show help")
        return
    
    time.sleep(1)
    
    # Add workflows
    print("\n📝 Adding workflows...")
    run_command(["uv", "run", "weavergen", "workflow", "add", "SimpleWorkflow", 
                 "--bpmn", "bpmn/simple_workflow.bpmn"])
    
    run_command(["uv", "run", "weavergen", "workflow", "add", "SemanticGeneration",
                 "--bpmn", "bpmn/semantic_generation.bpmn",
                 "--name", "Semantic Code Generation"])
    
    # List workflows
    print("\n📋 Listing workflows...")
    run_command(["uv", "run", "weavergen", "workflow", "list"])
    
    # Validate BPMN
    print("\n✅ Validating BPMN file...")
    run_command(["uv", "run", "weavergen", "workflow", "validate", 
                 "bpmn/semantic_generation.bpmn"])
    
    # Show workflow details
    print("\n🔍 Showing workflow details...")
    run_command(["uv", "run", "weavergen", "workflow", "show", "SimpleWorkflow"])
    
    # Run workflow
    print("\n▶️  Running workflow...")
    run_command(["uv", "run", "weavergen", "workflow", "run", "SimpleWorkflow"])
    
    # Run workflow with data
    print("\n▶️  Running workflow with data...")
    run_command(["uv", "run", "weavergen", "workflow", "run", "SemanticGeneration",
                 "--data", '{"semantic_file": "test.yaml", "target_language": "python"}'])
    
    # List with instances
    print("\n📋 Listing workflows with instances...")
    run_command(["uv", "run", "weavergen", "workflow", "list", "--instances"])
    
    # Check status
    print("\n📊 Checking workflow status...")
    run_command(["uv", "run", "weavergen", "workflow", "status", "SimpleWorkflow_0"])
    
    # Export workflow
    print("\n📤 Exporting workflow...")
    run_command(["uv", "run", "weavergen", "workflow", "export", "SemanticGeneration"])
    
    print("\n✨ Demo complete!")

if __name__ == "__main__":
    main()