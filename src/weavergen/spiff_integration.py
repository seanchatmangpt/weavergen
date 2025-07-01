"""SpiffWorkflow integration for advanced workflow orchestration with BPMN support."""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from SpiffWorkflow import Workflow
    from SpiffWorkflow.specs import WorkflowSpec
    SPIFF_AVAILABLE = True
except ImportError:
    SPIFF_AVAILABLE = False
    # Create dummy classes for fallback
    class Workflow:
        pass
    class WorkflowSpec:
        pass

from rich.console import Console
from rich import print as rprint

console = Console()


class WeaverGenWorkflowContext:
    """Context for WeaverGen workflow execution with span capture."""
    
    def __init__(self, output_dir: Path = Path("generated")):
        self.output_dir = output_dir
        self.span_files: List[Path] = []
        self.execution_log: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
    def log_command(self, command: str, success: bool, output: str = "", error: str = ""):
        """Log command execution with timestamp."""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "success": success,
            "output": output,
            "error": error
        })


def execute_command_sequence(commands: List[str], context: Optional[WeaverGenWorkflowContext] = None) -> Dict[str, Any]:
    """Execute a sequence of commands with span capture (fallback when SpiffWorkflow not available)."""
    if not context:
        context = WeaverGenWorkflowContext()
    
    rprint(f"[bold cyan]🔗 COMMAND SEQUENCE EXECUTION[/bold cyan]")
    rprint(f"[cyan]📋 Commands: {len(commands)}[/cyan]")
    
    for i, command in enumerate(commands, 1):
        rprint(f"[cyan]🔗 Step {i}/{len(commands)}: {command}[/cyan]")
        
        try:
            # Build full command
            cmd_parts = command.strip().split()
            full_cmd = ["uv", "run", "run_cli.py"] + cmd_parts
            
            # Execute command
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            context.log_command(command, success, result.stdout, result.stderr)
            
            # Check for span files
            span_files = list(Path(".").glob("*spans*.json"))
            if span_files:
                context.span_files.extend(span_files)
                rprint(f"[yellow]📊 Captured {len(span_files)} span files[/yellow]")
            
            if success:
                rprint(f"[green]✅ Step {i} completed successfully[/green]")
            else:
                rprint(f"[red]❌ Step {i} failed (exit code: {result.returncode})[/red]")
                if result.stderr:
                    rprint(f"[red]Error: {result.stderr[:200]}...[/red]")
                    
        except subprocess.TimeoutExpired:
            context.log_command(command, False, "", "timeout")
            rprint(f"[red]⏰ Step {i} timed out[/red]")
            
        except Exception as e:
            context.log_command(command, False, "", str(e))
            rprint(f"[red]💥 Step {i} failed: {e}[/red]")
    
    # Collect results
    results = {
        "workflow_name": "CommandSequence",
        "start_time": context.start_time.isoformat(),
        "end_time": datetime.now().isoformat(),
        "execution_log": context.execution_log,
        "span_files": [str(f) for f in context.span_files],
        "total_commands": len(context.execution_log),
        "successful_commands": sum(1 for log in context.execution_log if log["success"]),
        "commands": commands
    }
    
    # Summary
    success_rate = results["successful_commands"] / results["total_commands"] if results["total_commands"] > 0 else 0
    rprint(f"\n[bold cyan]🔗 SEQUENCE SUMMARY[/bold cyan]")
    rprint(f"[cyan]✅ Success rate: {success_rate:.1%} ({results['successful_commands']}/{results['total_commands']})[/cyan]")
    rprint(f"[cyan]📊 Span files: {len(context.span_files)}[/cyan]")
    
    if success_rate == 1.0:
        rprint("[bold green]🎉 ALL COMMANDS COMPLETED SUCCESSFULLY[/bold green]")
    else:
        rprint(f"[bold yellow]⚠️ {results['total_commands'] - results['successful_commands']} COMMANDS FAILED[/bold yellow]")
    
    return results


def create_simple_workflow_spec(commands: List[str], workflow_name: str = "WeaverGenWorkflow"):
    """Create a simple workflow - fallback to command sequence if SpiffWorkflow not available."""
    if not SPIFF_AVAILABLE:
        return {"commands": commands, "name": workflow_name, "type": "sequence"}
    
    # If SpiffWorkflow is available, we could implement actual workflow specs here
    # For now, fallback to sequence execution
    return {"commands": commands, "name": workflow_name, "type": "sequence"}


def execute_workflow(workflow, context: Optional[WeaverGenWorkflowContext] = None) -> Dict[str, Any]:
    """Execute workflow - handles both SpiffWorkflow objects and simple command sequences."""
    if not SPIFF_AVAILABLE or isinstance(workflow, dict):
        # Use simple command sequence execution
        commands = workflow.get("commands", []) if isinstance(workflow, dict) else []
        return execute_command_sequence(commands, context)
    
    # If we had full SpiffWorkflow support, we'd execute it here
    # For now, fallback to sequence
    return execute_command_sequence(workflow.get("commands", []), context)


def create_agent_validation_bpmn() -> str:
    """Create BPMN XML for agent validation workflow."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/schema/bpmn/20100524/BPMN20" 
                  xmlns:bpmndi="http://www.omg.org/schema/bpmn/20100524/BPMNDI" 
                  xmlns:dc="http://www.omg.org/schema/bpmn/20100524/DC" 
                  xmlns:di="http://www.omg.org/schema/bpmn/20100524/DI"
                  id="Definitions_1" 
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="WeaverGenProcess" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1"/>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="HealthCheck"/>
    
    <bpmn:scriptTask id="HealthCheck" name="System Health Check">
      <bpmn:script>task.set_data("command", "debug health --deep")</bpmn:script>
    </bpmn:scriptTask>
    <bpmn:sequenceFlow id="Flow_2" sourceRef="HealthCheck" targetRef="AgentCommunication"/>
    
    <bpmn:scriptTask id="AgentCommunication" name="Agent Communication">
      <bpmn:script>task.set_data("command", "agents communicate --agents 3")</bpmn:script>
    </bpmn:scriptTask>
    <bpmn:sequenceFlow id="Flow_3" sourceRef="AgentCommunication" targetRef="SpanAnalysis"/>
    
    <bpmn:scriptTask id="SpanAnalysis" name="Span Analysis">
      <bpmn:script>task.set_data("command", "debug spans --file test_generated/captured_spans.json --format table")</bpmn:script>
    </bpmn:scriptTask>
    <bpmn:sequenceFlow id="Flow_4" sourceRef="SpanAnalysis" targetRef="EndEvent_1"/>
    
    <bpmn:endEvent id="EndEvent_1"/>
  </bpmn:process>
</bpmn:definitions>'''


# Pre-defined workflow configurations
WORKFLOW_CONFIGS = {
    "agent-validation": [
        "debug health --deep",
        "agents communicate --agents 3", 
        "debug spans --file test_generated/captured_spans.json --format table",
        "debug inspect agents --verbose"
    ],
    "multi-agent-test": [
        "debug health",
        "agents communicate --agents 2",
        "agents communicate --agents 3", 
        "agents communicate --agents 4",
        "debug spans --file test_generated/captured_spans.json --format json"
    ],
    "full-validation": [
        "debug health --deep",
        "agents communicate --agents 3",
        "debug spans --file test_generated/captured_spans.json --format table",
        "debug inspect agents --verbose",
        "agents communicate --agents 4",
        "debug spans --file test_generated/captured_spans.json --format mermaid"
    ]
}