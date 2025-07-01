#!/usr/bin/env python3
"""
BPMN Unified Engine Demo - Making Complexity Accessible

This demonstrates the enhanced BPMN-first approach that keeps all functionality
while making it 80% easier to use.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.progress import track
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich import box

console = Console()


@dataclass
class ServiceTaskInfo:
    """Self-documenting service task"""
    id: str
    category: str
    description: str
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    
    def to_panel(self) -> Panel:
        """Rich panel representation"""
        content = f"[bold]{self.description}[/bold]\n\n"
        content += "[cyan]Inputs:[/cyan]\n"
        for name, type_ in self.inputs.items():
            content += f"  • {name}: {type_}\n"
        content += "\n[green]Outputs:[/green]\n"
        for name, type_ in self.outputs.items():
            content += f"  • {name}: {type_}"
        return Panel(content, title=f"[yellow]{self.id}[/yellow]", box=box.ROUNDED)


class UnifiedServiceRegistry:
    """All BPMN service tasks in one place"""
    
    def __init__(self):
        self.tasks = self._discover_all_tasks()
    
    def _discover_all_tasks(self) -> Dict[str, ServiceTaskInfo]:
        """Auto-discover all available tasks"""
        return {
            # Weaver Tasks
            "weaver.initialize": ServiceTaskInfo(
                id="weaver.initialize",
                category="weaver",
                description="Initialize OTel Weaver binary",
                inputs={"config": "dict"},
                outputs={"weaver_path": "str", "version": "str"}
            ),
            "weaver.generate": ServiceTaskInfo(
                id="weaver.generate",
                category="weaver", 
                description="Generate code with Weaver",
                inputs={"semantic_file": "path", "language": "str", "template": "str"},
                outputs={"generated_files": "list[path]", "metrics": "dict"}
            ),
            "weaver.validate": ServiceTaskInfo(
                id="weaver.validate",
                category="weaver",
                description="Validate semantic conventions",
                inputs={"semantic_file": "path"},
                outputs={"valid": "bool", "issues": "list[str]"}
            ),
            
            # AI Tasks
            "ai.enhance": ServiceTaskInfo(
                id="ai.enhance",
                category="ai",
                description="Enhance with LLM capabilities",
                inputs={"content": "str", "model": "str", "prompt": "str"},
                outputs={"enhanced": "str", "suggestions": "list[str]"}
            ),
            "ai.generate_docs": ServiceTaskInfo(
                id="ai.generate_docs",
                category="ai",
                description="Generate documentation with AI",
                inputs={"code": "str", "style": "str"},
                outputs={"documentation": "str", "examples": "list[str]"}
            ),
            
            # Validation Tasks
            "validate.spans": ServiceTaskInfo(
                id="validate.spans",
                category="validation",
                description="Validate with span tracking",
                inputs={"spans": "list[dict]", "rules": "dict"},
                outputs={"valid": "bool", "report": "dict"}
            ),
            "validate.health": ServiceTaskInfo(
                id="validate.health",
                category="validation",
                description="System health validation",
                inputs={"components": "list[str]"},
                outputs={"health_score": "float", "issues": "dict"}
            ),
        }
    
    def list_by_category(self) -> Dict[str, List[ServiceTaskInfo]]:
        """Group tasks by category"""
        categories = {}
        for task in self.tasks.values():
            if task.category not in categories:
                categories[task.category] = []
            categories[task.category].append(task)
        return categories
    
    def search(self, query: str) -> List[ServiceTaskInfo]:
        """Search tasks by ID or description"""
        query = query.lower()
        return [
            task for task in self.tasks.values()
            if query in task.id.lower() or query in task.description.lower()
        ]


class WorkflowMonitor:
    """Real-time workflow monitoring"""
    
    def __init__(self):
        self.executions = []
        self.current_execution = None
    
    def start_execution(self, workflow: str) -> str:
        """Start monitoring a workflow execution"""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_execution = {
            "id": execution_id,
            "workflow": workflow,
            "start_time": datetime.now(),
            "tasks": [],
            "status": "running"
        }
        self.executions.append(self.current_execution)
        return execution_id
    
    def record_task(self, task_id: str, duration_ms: int, status: str = "success"):
        """Record task execution"""
        if self.current_execution:
            self.current_execution["tasks"].append({
                "task_id": task_id,
                "duration_ms": duration_ms,
                "status": status,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_timeline(self) -> str:
        """Generate execution timeline"""
        if not self.current_execution:
            return "No execution in progress"
        
        timeline = "Execution Timeline:\n"
        timeline += "─" * 50 + "\n"
        
        for task in self.current_execution["tasks"]:
            bar_length = int(task["duration_ms"] / 10)  # Scale for display
            status_icon = "✅" if task["status"] == "success" else "❌"
            timeline += f"{task['task_id']:20} │{'█' * bar_length}│ {task['duration_ms']}ms {status_icon}\n"
        
        timeline += "─" * 50
        return timeline


class UnifiedBPMNEngine:
    """The unified engine that makes everything accessible"""
    
    def __init__(self):
        self.registry = UnifiedServiceRegistry()
        self.monitor = WorkflowMonitor()
        console.print("[green]✅ Unified BPMN Engine initialized[/green]")
    
    def discover_tasks(self) -> Dict[str, List[ServiceTaskInfo]]:
        """Discover all available tasks"""
        return self.registry.list_by_category()
    
    async def execute(self, workflow: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a BPMN workflow with monitoring"""
        execution_id = self.monitor.start_execution(workflow)
        
        with Live(self._get_status_layout(), refresh_per_second=4) as live:
            # Simulate workflow execution
            tasks_to_run = self._get_workflow_tasks(workflow)
            
            results = {}
            for task_id in tasks_to_run:
                # Update live display
                live.update(self._get_status_layout(current_task=task_id))
                
                # Simulate task execution
                start_time = datetime.now()
                result = await self._execute_task(task_id, context)
                duration = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Record execution
                self.monitor.record_task(task_id, duration)
                results[task_id] = result
                
                # Brief pause for visual effect
                await asyncio.sleep(0.5)
        
        return {
            "execution_id": execution_id,
            "results": results,
            "timeline": self.monitor.get_timeline()
        }
    
    def _get_workflow_tasks(self, workflow: str) -> List[str]:
        """Get tasks for a workflow"""
        # In real implementation, this would parse BPMN
        workflow_tasks = {
            "generate.bpmn": [
                "weaver.initialize",
                "weaver.validate", 
                "weaver.generate",
                "ai.enhance",
                "validate.spans"
            ],
            "validate.bpmn": [
                "weaver.validate",
                "validate.health",
                "validate.spans"
            ]
        }
        return workflow_tasks.get(workflow, ["weaver.validate"])
    
    async def _execute_task(self, task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        # Simulate task execution
        await asyncio.sleep(0.1)  # Simulate work
        
        # Return mock results based on task
        if task_id == "weaver.generate":
            return {
                "generated_files": ["models.py", "metrics.py", "spans.py"],
                "metrics": {"files": 3, "lines": 450}
            }
        elif task_id == "ai.enhance":
            return {
                "enhanced": True,
                "suggestions": ["Added docstrings", "Improved type hints"]
            }
        else:
            return {"status": "success", "timestamp": datetime.now().isoformat()}
    
    def _get_status_layout(self, current_task: Optional[str] = None) -> Layout:
        """Create rich layout for live display"""
        layout = Layout()
        
        # Header
        header = Panel(
            "[bold cyan]BPMN Unified Engine - Workflow Execution[/bold cyan]",
            box=box.DOUBLE
        )
        
        # Task list
        task_tree = Tree("📋 Workflow Tasks")
        for task_id in self._get_workflow_tasks("generate.bpmn"):
            if task_id == current_task:
                task_tree.add(f"[bold yellow]▶ {task_id}[/bold yellow] [blink]⚡[/blink]")
            elif any(t["task_id"] == task_id for t in (self.monitor.current_execution or {}).get("tasks", [])):
                task_tree.add(f"[green]✓ {task_id}[/green]")
            else:
                task_tree.add(f"[dim]○ {task_id}[/dim]")
        
        # Timeline
        timeline_panel = Panel(
            self.monitor.get_timeline(),
            title="Execution Timeline",
            border_style="blue"
        )
        
        layout.split_column(
            Layout(header, size=3),
            Layout(task_tree, size=10),
            Layout(timeline_panel)
        )
        
        return layout
    
    def visualize_workflow(self, workflow: str) -> str:
        """Generate Mermaid diagram of workflow"""
        tasks = self._get_workflow_tasks(workflow)
        
        mermaid = "graph TD\n"
        mermaid += "    Start([Start]) --> Init[weaver.initialize]\n"
        
        for i, task in enumerate(tasks):
            task_info = self.registry.tasks.get(task)
            if task_info:
                label = f"{task}\\n{task_info.description}"
            else:
                label = task
            
            if i == 0:
                mermaid += f"    Init --> T{i}[{label}]\n"
            elif i < len(tasks) - 1:
                mermaid += f"    T{i-1} --> T{i}[{label}]\n"
            else:
                mermaid += f"    T{i-1} --> T{i}[{label}]\n"
                mermaid += f"    T{i} --> End([End])\n"
        
        # Add styling
        mermaid += "\n    %% Styling\n"
        mermaid += "    classDef weaverTask fill:#e1f5e1,stroke:#4caf50,stroke-width:2px\n"
        mermaid += "    classDef aiTask fill:#e3f2fd,stroke:#2196f3,stroke-width:2px\n"
        mermaid += "    classDef validateTask fill:#fff3e0,stroke:#ff9800,stroke-width:2px\n"
        
        # Apply styles
        for i, task in enumerate(tasks):
            if "weaver" in task:
                mermaid += f"    class T{i} weaverTask\n"
            elif "ai" in task:
                mermaid += f"    class T{i} aiTask\n"
            elif "validate" in task:
                mermaid += f"    class T{i} validateTask\n"
        
        return mermaid


class WorkflowStudio:
    """Visual workflow design and debugging"""
    
    def __init__(self, engine: UnifiedBPMNEngine):
        self.engine = engine
    
    def show_task_catalog(self):
        """Display available tasks in a rich catalog"""
        console.print("\n[bold cyan]📚 BPMN Service Task Catalog[/bold cyan]\n")
        
        categories = self.engine.discover_tasks()
        
        for category, tasks in categories.items():
            console.print(f"\n[bold yellow]{category.upper()} TASKS[/bold yellow]")
            console.print("─" * 50)
            
            for task in tasks:
                console.print(task.to_panel())
                console.print()
    
    def search_tasks(self, query: str):
        """Search and display tasks"""
        results = self.engine.registry.search(query)
        
        if results:
            console.print(f"\n[green]Found {len(results)} tasks matching '{query}':[/green]\n")
            for task in results:
                console.print(task.to_panel())
                console.print()
        else:
            console.print(f"[red]No tasks found matching '{query}'[/red]")
    
    def visualize_workflow(self, workflow: str):
        """Display workflow visualization"""
        console.print(f"\n[bold cyan]Workflow Visualization: {workflow}[/bold cyan]\n")
        
        mermaid = self.engine.visualize_workflow(workflow)
        
        console.print(Panel(
            mermaid,
            title="Mermaid Diagram",
            border_style="blue",
            box=box.ROUNDED
        ))
        
        console.print("\n[dim]Copy the above diagram to view at: https://mermaid.live[/dim]")


async def demo():
    """Demonstrate the unified BPMN engine"""
    
    # Initialize engine
    engine = UnifiedBPMNEngine()
    studio = WorkflowStudio(engine)
    
    # Show banner
    console.print(Panel.fit(
        "[bold cyan]BPMN Unified Engine Demo[/bold cyan]\n"
        "Making Complexity Accessible",
        border_style="cyan"
    ))
    
    # 1. Show task catalog
    console.print("\n[bold]1. Discovering Available Tasks[/bold]")
    studio.show_task_catalog()
    
    # 2. Search for tasks
    console.print("\n[bold]2. Searching for AI Tasks[/bold]")
    studio.search_tasks("ai")
    
    # 3. Visualize workflow
    console.print("\n[bold]3. Visualizing Workflow[/bold]")
    studio.visualize_workflow("generate.bpmn")
    
    # 4. Execute workflow
    console.print("\n[bold]4. Executing Workflow[/bold]")
    
    context = {
        "semantic_file": "test_semantic.yaml",
        "languages": ["python", "rust"],
        "enable_ai": True
    }
    
    result = await engine.execute("generate.bpmn", context)
    
    # 5. Show results
    console.print("\n[bold]5. Execution Results[/bold]")
    console.print(Panel(
        json.dumps(result["results"], indent=2),
        title="Results",
        border_style="green"
    ))
    
    # 6. Show timeline
    console.print("\n[bold]6. Execution Timeline[/bold]")
    console.print(Panel(
        result["timeline"],
        title="Performance Analysis",
        border_style="yellow"
    ))
    
    # Summary
    console.print("\n[bold green]✨ Demo Complete![/bold green]")
    console.print(
        "\nThe Unified BPMN Engine provides:\n"
        "• [cyan]All functionality in one place[/cyan]\n"
        "• [yellow]Visual workflow design[/yellow]\n"
        "• [green]Self-documenting tasks[/green]\n"
        "• [magenta]Real-time monitoring[/magenta]\n"
        "• [blue]Easy debugging[/blue]\n"
    )


if __name__ == "__main__":
    asyncio.run(demo())