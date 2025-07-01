"""
BPMN Live Workflow Monitor - 80/20 Real-time Visualization

Provides real-time monitoring of BPMN workflow execution with minimal complexity.
Displays workflow progress in the terminal using Rich.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.tree import Tree
from rich.text import Text

from opentelemetry import trace


class TaskState(Enum):
    """Task execution states"""
    PENDING = "⏳"
    RUNNING = "🔄"  
    COMPLETED = "✅"
    FAILED = "❌"
    COMPENSATED = "↩️"
    SKIPPED = "⏭️"


@dataclass
class TaskStatus:
    """Status of a BPMN task"""
    task_id: str
    task_name: str
    state: TaskState = TaskState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    spans: List[str] = field(default_factory=list)


class BPMNLiveMonitor:
    """
    Real-time BPMN workflow monitor with 80/20 simplicity.
    
    Shows live execution progress in the terminal without external dependencies.
    """
    
    def __init__(self, workflow_name: str = "WeaverGen"):
        self.workflow_name = workflow_name
        self.console = Console()
        self.tasks: Dict[str, TaskStatus] = {}
        self.start_time = datetime.now()
        self.is_running = False
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        )
        
    def register_task(self, task_id: str, task_name: str):
        """Register a task for monitoring"""
        self.tasks[task_id] = TaskStatus(task_id=task_id, task_name=task_name)
        
    def task_started(self, task_id: str):
        """Mark task as started"""
        if task_id in self.tasks:
            self.tasks[task_id].state = TaskState.RUNNING
            self.tasks[task_id].start_time = datetime.now()
            
    def task_completed(self, task_id: str, result: Optional[Dict[str, Any]] = None):
        """Mark task as completed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.state = TaskState.COMPLETED
            task.end_time = datetime.now()
            if task.start_time:
                task.duration_ms = (task.end_time - task.start_time).total_seconds() * 1000
            task.result = result
            
    def task_failed(self, task_id: str, error: str):
        """Mark task as failed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.state = TaskState.FAILED
            task.end_time = datetime.now()
            task.error = error
            
    def add_span(self, task_id: str, span_id: str):
        """Add a span ID to a task"""
        if task_id in self.tasks:
            self.tasks[task_id].spans.append(span_id)
            
    def create_workflow_diagram(self) -> Panel:
        """Create visual workflow diagram"""
        
        # Simple ASCII workflow representation
        workflow_lines = [
            "🚀 Workflow: " + self.workflow_name,
            "",
            "┌─────────────┐",
            "│    Start    │",
            "└──────┬──────┘",
            "       │"
        ]
        
        # Add tasks in order
        task_list = list(self.tasks.values())
        for i, task in enumerate(task_list):
            is_last = i == len(task_list) - 1
            
            # Task box
            state_icon = task.state.value
            task_display = f"{state_icon} {task.task_name}"
            
            # Color based on state
            if task.state == TaskState.COMPLETED:
                color = "green"
            elif task.state == TaskState.RUNNING:
                color = "yellow"
            elif task.state == TaskState.FAILED:
                color = "red"
            else:
                color = "dim"
                
            workflow_lines.extend([
                "       │",
                f"┌─────────────┐",
                f"│ [{color}]{task_display:^11}[/{color}] │",
                f"└──────{'─' if is_last else '┬'}──────┘"
            ])
            
        workflow_lines.extend([
            "       │",
            "       ▼",
            "    Complete"
        ])
        
        return Panel(
            "\n".join(workflow_lines),
            title="BPMN Workflow Progress",
            border_style="blue"
        )
        
    def create_task_table(self) -> Table:
        """Create task status table"""
        
        table = Table(title="Task Execution Details")
        table.add_column("Task", style="cyan", no_wrap=True)
        table.add_column("Status", style="yellow")
        table.add_column("Duration", style="green")
        table.add_column("Spans", style="blue")
        table.add_column("Result", style="magenta")
        
        for task in self.tasks.values():
            duration = f"{task.duration_ms:.0f}ms" if task.duration_ms else "-"
            spans = str(len(task.spans))
            
            # Truncate result for display
            result = "-"
            if task.result:
                if "success" in task.result:
                    result = "✓" if task.result["success"] else "✗"
                elif task.error:
                    result = f"Error: {task.error[:20]}..."
                    
            table.add_row(
                task.task_name,
                task.state.value,
                duration,
                spans,
                result
            )
            
        return table
        
    def create_metrics_panel(self) -> Panel:
        """Create execution metrics panel"""
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        completed = sum(1 for t in self.tasks.values() if t.state == TaskState.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.state == TaskState.FAILED)
        running = sum(1 for t in self.tasks.values() if t.state == TaskState.RUNNING)
        
        total_duration = sum(t.duration_ms or 0 for t in self.tasks.values())
        avg_duration = total_duration / len(self.tasks) if self.tasks else 0
        
        metrics_text = f"""
Workflow: {self.workflow_name}
Started: {self.start_time.strftime('%H:%M:%S')}
Elapsed: {elapsed:.1f}s

Tasks:
  ✅ Completed: {completed}
  🔄 Running: {running}
  ❌ Failed: {failed}
  📊 Total: {len(self.tasks)}

Performance:
  ⚡ Avg Duration: {avg_duration:.0f}ms
  📡 Total Spans: {sum(len(t.spans) for t in self.tasks.values())}
"""
        
        return Panel(
            metrics_text.strip(),
            title="Execution Metrics",
            border_style="green"
        )
        
    def create_layout(self) -> Layout:
        """Create the monitor layout"""
        
        layout = Layout()
        
        layout.split_column(
            Layout(self.create_workflow_diagram(), size=20),
            Layout(name="middle"),
            Layout(self.create_metrics_panel(), size=15)
        )
        
        layout["middle"].split_row(
            Layout(self.create_task_table())
        )
        
        return layout
        
    async def start_live_monitor(self, update_interval: float = 0.5):
        """Start the live monitoring display"""
        
        self.is_running = True
        
        with Live(self.create_layout(), refresh_per_second=2, console=self.console) as live:
            while self.is_running:
                live.update(self.create_layout())
                await asyncio.sleep(update_interval)
                
                # Stop if all tasks are complete
                if all(t.state in [TaskState.COMPLETED, TaskState.FAILED] 
                      for t in self.tasks.values()):
                    self.is_running = False
                    
    def stop(self):
        """Stop the monitor"""
        self.is_running = False


class BPMNMonitorContext:
    """
    Context manager for BPMN monitoring integration.
    
    Automatically tracks task execution within a context.
    """
    
    def __init__(self, monitor: BPMNLiveMonitor, task_id: str):
        self.monitor = monitor
        self.task_id = task_id
        self.tracer = trace.get_tracer(__name__)
        
    async def __aenter__(self):
        self.monitor.task_started(self.task_id)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.monitor.task_failed(self.task_id, str(exc_val))
        else:
            self.monitor.task_completed(self.task_id)
            
        # Capture span info
        current_span = trace.get_current_span()
        if current_span:
            span_context = current_span.get_span_context()
            self.monitor.add_span(self.task_id, hex(span_context.span_id))


# Convenience function for easy monitoring
async def monitor_bpmn_workflow(workflow_func, workflow_name: str = "WeaverGen"):
    """
    Monitor a BPMN workflow execution.
    
    Usage:
        async def my_workflow():
            # workflow implementation
            
        await monitor_bpmn_workflow(my_workflow, "MyWorkflow")
    """
    
    monitor = BPMNLiveMonitor(workflow_name)
    
    # Start monitor in background
    monitor_task = asyncio.create_task(monitor.start_live_monitor())
    
    try:
        # Execute workflow with monitor context
        result = await workflow_func(monitor)
        return result
    finally:
        monitor.stop()
        await monitor_task


# Example usage for testing
async def example_workflow(monitor: BPMNLiveMonitor):
    """Example workflow demonstrating monitoring"""
    
    # Register tasks
    tasks = [
        ("load", "Load Semantics"),
        ("validate", "Validate Input"),
        ("generate", "Generate Code"),
        ("test", "Test Output"),
        ("report", "Generate Report")
    ]
    
    for task_id, task_name in tasks:
        monitor.register_task(task_id, task_name)
        
    # Simulate execution
    for task_id, task_name in tasks:
        async with BPMNMonitorContext(monitor, task_id):
            # Simulate work
            await asyncio.sleep(0.5 + (0.1 * len(task_name)))
            
            # Simulate some results
            if task_id == "generate":
                monitor.tasks[task_id].result = {"files_generated": 5}
                
    return {"success": True}