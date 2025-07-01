#!/usr/bin/env python3
"""
Visual Workflow Studio - Making BPMN Accessible

This module provides visual tools for designing, debugging, and monitoring
BPMN workflows in the unified engine.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.columns import Columns
from rich.align import Align
from rich.text import Text
from rich import box

from .unified_bpmn_engine import UnifiedBPMNEngine, ServiceTaskInfo, WorkflowExecution

console = Console()


@dataclass
class DebugSession:
    """Interactive debugging session for workflows"""
    execution_id: str
    workflow: str
    engine: UnifiedBPMNEngine
    breakpoints: List[str]
    current_task: Optional[str] = None
    step_mode: bool = False
    variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}


class WorkflowDesigner:
    """Visual BPMN workflow designer"""
    
    def __init__(self, engine: UnifiedBPMNEngine):
        self.engine = engine
        self.current_workflow = None
        self.task_palette = self._build_task_palette()
    
    def _build_task_palette(self) -> Dict[str, List[ServiceTaskInfo]]:
        """Build categorized task palette for designer"""
        return self.engine.discover_tasks()
    
    def show_task_palette(self):
        """Display interactive task palette"""
        console.print("[bold cyan]🧩 BPMN Task Palette[/bold cyan]\n")
        
        categories = self.task_palette
        panels = []
        
        for category, tasks in categories.items():
            # Create compact task list for each category
            task_items = []
            for task in tasks[:5]:  # Show first 5 tasks
                task_items.append(f"[cyan]•[/cyan] {task.id}")
                task_items.append(f"  [dim]{task.description[:40]}...[/dim]")
            
            if len(tasks) > 5:
                task_items.append(f"[yellow]+ {len(tasks) - 5} more tasks[/yellow]")
            
            panel = Panel(
                "\n".join(task_items),
                title=f"[bold]{category.upper()}[/bold] ({len(tasks)})",
                border_style="blue",
                box=box.ROUNDED
            )
            panels.append(panel)
        
        # Display in columns
        console.print(Columns(panels, equal=True, expand=True))
    
    def create_workflow_template(self, workflow_type: str) -> str:
        """Create workflow template based on type"""
        templates = {
            "basic_generation": self._basic_generation_template(),
            "ai_enhanced": self._ai_enhanced_template(),
            "validation_only": self._validation_template(),
            "custom": self._custom_template()
        }
        
        return templates.get(workflow_type, templates["basic_generation"])
    
    def _basic_generation_template(self) -> str:
        """Basic code generation workflow template"""
        return """
graph TD
    Start([Start]) --> Load[weaver.load_semantics]
    Load --> Validate[weaver.validate]
    Validate --> Generate[weaver.multi_generate]
    Generate --> Quality[validate.quality_gate]
    Quality --> End([End])
    
    %% Styling
    classDef weaverTask fill:#e1f5e1,stroke:#4caf50,stroke-width:2px
    classDef validateTask fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class Load,Validate,Generate weaverTask
    class Quality validateTask
        """
    
    def _ai_enhanced_template(self) -> str:
        """AI-enhanced workflow template"""
        return """
graph TD
    Start([Start]) --> Load[weaver.load_semantics]
    Load --> AIAgents[ai.generate_agents]
    AIAgents --> Enhance[ai.enhance_semantics]
    Enhance --> Validate[weaver.validate]
    Validate --> Generate[weaver.multi_generate]
    Generate --> Review[ai.code_review]
    Review --> Quality[validate.quality_gate]
    Quality --> End([End])
    
    %% Styling
    classDef weaverTask fill:#e1f5e1,stroke:#4caf50,stroke-width:2px
    classDef aiTask fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef validateTask fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class Load,Validate,Generate weaverTask
    class AIAgents,Enhance,Review aiTask
    class Quality validateTask
        """
    
    def _validation_template(self) -> str:
        """Validation-focused workflow template"""
        return """
graph TD
    Start([Start]) --> Load[weaver.load_semantics]
    Load --> Validate[weaver.validate]
    Validate --> Health[validate.health]
    Health --> Spans[validate.spans]
    Spans --> Compliance[validate.compliance]
    Compliance --> End([End])
    
    %% Styling
    classDef weaverTask fill:#e1f5e1,stroke:#4caf50,stroke-width:2px
    classDef validateTask fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class Load,Validate weaverTask
    class Health,Spans,Compliance validateTask
        """
    
    def _custom_template(self) -> str:
        """Custom extensible workflow template"""
        return """
graph TD
    Start([Start]) --> Custom1[custom.shell_command]
    Custom1 --> Load[weaver.load_semantics]
    Load --> Plugin[custom.plugin_task]
    Plugin --> Generate[weaver.generate]
    Generate --> FileOps[custom.file_operations]
    FileOps --> End([End])
    
    %% Styling
    classDef weaverTask fill:#e1f5e1,stroke:#4caf50,stroke-width:2px
    classDef customTask fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    
    class Load,Generate weaverTask
    class Custom1,Plugin,FileOps customTask
        """


class VisualDebugger:
    """Interactive visual debugger for BPMN execution"""
    
    def __init__(self, engine: UnifiedBPMNEngine):
        self.engine = engine
        self.active_sessions: Dict[str, DebugSession] = {}
    
    def create_debug_session(self, execution_id: str, workflow: str) -> DebugSession:
        """Create new debug session"""
        session = DebugSession(
            execution_id=execution_id,
            workflow=workflow,
            engine=self.engine,
            breakpoints=[],
            step_mode=True
        )
        
        self.active_sessions[execution_id] = session
        return session
    
    def debug_workflow_execution(self, workflow: str, context: Dict[str, Any]):
        """Debug workflow execution with step-through capability"""
        console.print(f"[cyan]🔍 Starting debug session for: {workflow}[/cyan]\n")
        
        # Create debug session
        execution_id = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = self.create_debug_session(execution_id, workflow)
        
        # Show debug interface
        self._show_debug_interface(session, context)
    
    def _show_debug_interface(self, session: DebugSession, context: Dict[str, Any]):
        """Show interactive debug interface"""
        
        # Create debug layout
        layout = Layout()
        
        # Header
        header = Panel(
            f"[bold cyan]Debug Session: {session.workflow}[/bold cyan]\n"
            f"[dim]Session ID: {session.execution_id}[/dim]",
            box=box.DOUBLE
        )
        
        # Workflow visualization
        tasks = self.engine._get_workflow_tasks(session.workflow)
        workflow_tree = Tree("📋 Workflow Tasks")
        
        for i, task_id in enumerate(tasks):
            task_info = self.engine.get_task_info(task_id)
            if task_info:
                if i == 0:  # Current task
                    workflow_tree.add(f"[bold yellow]▶ {task_id}[/bold yellow] - {task_info.description}")
                else:
                    workflow_tree.add(f"[dim]○ {task_id}[/dim] - {task_info.description}")
        
        # Context variables
        context_table = Table(title="Context Variables", box=box.SIMPLE)
        context_table.add_column("Variable", style="cyan")
        context_table.add_column("Value", style="green")
        context_table.add_column("Type", style="yellow")
        
        for key, value in context.items():
            value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            context_table.add_row(key, value_str, type(value).__name__)
        
        # Debug controls
        controls = Panel(
            "[bold]Debug Controls:[/bold]\n\n"
            "• [cyan]n[/cyan] - Next step\n"
            "• [cyan]c[/cyan] - Continue\n"
            "• [cyan]b <task>[/cyan] - Set breakpoint\n"
            "• [cyan]i[/cyan] - Inspect variables\n"
            "• [cyan]q[/cyan] - Quit debug session",
            title="Controls",
            border_style="yellow"
        )
        
        # Split layout
        layout.split_column(
            Layout(header, size=4),
            Layout(workflow_tree, name="workflow"),
            Layout(context_table, name="context"),
            Layout(controls, size=8)
        )
        
        # Show layout
        console.print(layout)
        
        # Debug interaction loop
        self._debug_interaction_loop(session, context)
    
    def _debug_interaction_loop(self, session: DebugSession, context: Dict[str, Any]):
        """Interactive debug loop"""
        tasks = self.engine._get_workflow_tasks(session.workflow)
        current_task_index = 0
        
        while current_task_index < len(tasks):
            task_id = tasks[current_task_index]
            session.current_task = task_id
            
            console.print(f"\n[bold yellow]🔍 Current Task: {task_id}[/bold yellow]")
            
            task_info = self.engine.get_task_info(task_id)
            if task_info:
                console.print(task_info.to_rich_panel())
            
            # Check for breakpoints
            if task_id in session.breakpoints:
                console.print(f"[red]🛑 Breakpoint hit at: {task_id}[/red]")
            
            # Wait for user input
            try:
                command = console.input("\n[cyan]Debug> [/cyan]").strip().lower()
                
                if command == 'n' or command == 'next':
                    console.print(f"[green]⏭️ Stepping to next task...[/green]")
                    current_task_index += 1
                    
                elif command == 'c' or command == 'continue':
                    console.print(f"[green]▶️ Continuing execution...[/green]")
                    break
                    
                elif command.startswith('b '):
                    breakpoint_task = command[2:].strip()
                    if breakpoint_task in tasks:
                        session.breakpoints.append(breakpoint_task)
                        console.print(f"[yellow]🛑 Breakpoint set at: {breakpoint_task}[/yellow]")
                    else:
                        console.print(f"[red]❌ Task not found: {breakpoint_task}[/red]")
                
                elif command == 'i' or command == 'inspect':
                    self._show_variable_inspector(session, context)
                
                elif command == 'q' or command == 'quit':
                    console.print("[red]🛑 Debug session terminated[/red]")
                    return
                
                else:
                    console.print("[yellow]⚠️ Unknown command. Use 'n', 'c', 'b <task>', 'i', or 'q'[/yellow]")
                    
            except KeyboardInterrupt:
                console.print("\n[red]🛑 Debug session interrupted[/red]")
                return
        
        console.print("[green]✅ Debug session completed[/green]")
    
    def _show_variable_inspector(self, session: DebugSession, context: Dict[str, Any]):
        """Show detailed variable inspector"""
        console.print("\n[bold cyan]🔍 Variable Inspector[/bold cyan]")
        
        inspector_table = Table(title="Current Context", box=box.ROUNDED)
        inspector_table.add_column("Variable", style="cyan", width=20)
        inspector_table.add_column("Type", style="yellow", width=15)
        inspector_table.add_column("Value", style="green")
        
        for key, value in context.items():
            value_repr = json.dumps(value, indent=2, default=str) if isinstance(value, (dict, list)) else str(value)
            if len(value_repr) > 100:
                value_repr = value_repr[:97] + "..."
            
            inspector_table.add_row(key, type(value).__name__, value_repr)
        
        console.print(inspector_table)


class ExecutionMonitor:
    """Real-time execution monitoring with performance analytics"""
    
    def __init__(self, engine: UnifiedBPMNEngine):
        self.engine = engine
        self.monitoring_active = False
    
    def start_monitoring(self, execution_id: str):
        """Start real-time monitoring"""
        self.monitoring_active = True
        console.print(f"[green]📊 Monitoring started for execution: {execution_id}[/green]")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        console.print("[yellow]📊 Monitoring stopped[/yellow]")
    
    def show_performance_dashboard(self, execution_id: str):
        """Show performance analytics dashboard"""
        execution = self.engine.monitor.executions.get(execution_id)
        if not execution:
            console.print(f"[red]❌ Execution not found: {execution_id}[/red]")
            return
        
        console.print(f"[bold cyan]📊 Performance Dashboard: {execution_id}[/bold cyan]\n")
        
        # Execution overview
        overview_table = Table(title="Execution Overview", box=box.SIMPLE)
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="green")
        
        total_duration = sum(task["duration_ms"] for task in execution.tasks)
        overview_table.add_row("Workflow", execution.workflow)
        overview_table.add_row("Status", execution.status)
        overview_table.add_row("Total Tasks", str(len(execution.tasks)))
        overview_table.add_row("Total Duration", f"{total_duration}ms")
        
        if execution.start_time:
            elapsed = datetime.now() - execution.start_time
            overview_table.add_row("Elapsed Time", str(elapsed).split('.')[0])
        
        console.print(overview_table)
        
        # Task performance breakdown
        if execution.tasks:
            console.print("\n[bold]⏱️ Task Performance Breakdown:[/bold]")
            
            perf_table = Table(box=box.SIMPLE)
            perf_table.add_column("Task", style="cyan", width=25)
            perf_table.add_column("Duration", style="green", width=10)
            perf_table.add_column("Status", style="yellow", width=10)
            perf_table.add_column("Performance Bar", style="blue", width=30)
            
            max_duration = max(task["duration_ms"] for task in execution.tasks)
            
            for task in execution.tasks:
                # Create performance bar
                bar_length = int((task["duration_ms"] / max_duration) * 20) if max_duration > 0 else 0
                performance_bar = "█" * bar_length
                
                status_icon = "✅" if task["status"] == "success" else "❌"
                
                perf_table.add_row(
                    task["task_id"],
                    f"{task['duration_ms']}ms",
                    f"{status_icon} {task['status']}",
                    performance_bar
                )
            
            console.print(perf_table)
        
        # Performance recommendations
        self._show_performance_recommendations(execution)
    
    def _show_performance_recommendations(self, execution: WorkflowExecution):
        """Generate performance recommendations"""
        if not execution.tasks:
            return
        
        recommendations = []
        
        # Analyze task durations
        durations = [task["duration_ms"] for task in execution.tasks]
        avg_duration = sum(durations) / len(durations)
        
        slow_tasks = [task for task in execution.tasks if task["duration_ms"] > avg_duration * 2]
        if slow_tasks:
            recommendations.append(f"🐌 Consider optimizing slow tasks: {', '.join(t['task_id'] for t in slow_tasks)}")
        
        # Check for failed tasks
        failed_tasks = [task for task in execution.tasks if task["status"] != "success"]
        if failed_tasks:
            recommendations.append(f"❌ Review failed tasks: {', '.join(t['task_id'] for t in failed_tasks)}")
        
        # Parallel execution suggestions
        if len(execution.tasks) > 3:
            recommendations.append("⚡ Consider parallel execution for independent tasks")
        
        if recommendations:
            console.print("\n[bold yellow]💡 Performance Recommendations:[/bold yellow]")
            for rec in recommendations:
                console.print(f"  • {rec}")


class WorkflowStudio:
    """Complete visual workflow studio combining all tools"""
    
    def __init__(self, engine: UnifiedBPMNEngine):
        self.engine = engine
        self.designer = WorkflowDesigner(engine)
        self.debugger = VisualDebugger(engine)
        self.monitor = ExecutionMonitor(engine)
    
    def launch_interactive_studio(self):
        """Launch interactive studio session"""
        console.print(Panel.fit(
            "[bold cyan]🎨 Visual Workflow Studio[/bold cyan]\n\n"
            "Welcome to the unified BPMN workflow studio!\n"
            "Design, debug, and monitor workflows visually.",
            border_style="cyan"
        ))
        
        self._show_studio_menu()
    
    def _show_studio_menu(self):
        """Show interactive studio menu"""
        while True:
            console.print("\n[bold]🏠 Studio Menu:[/bold]")
            console.print("1. [cyan]Task Palette[/cyan] - Browse available service tasks")
            console.print("2. [cyan]Design Workflow[/cyan] - Create new workflow")
            console.print("3. [cyan]Debug Workflow[/cyan] - Step through execution")
            console.print("4. [cyan]Monitor Execution[/cyan] - Performance dashboard")
            console.print("5. [cyan]Visualize Workflow[/cyan] - Generate diagrams")
            console.print("6. [cyan]Export Tools[/cyan] - Export workflows and catalogs")
            console.print("7. [red]Exit[/red] - Close studio")
            
            try:
                choice = console.input("\n[cyan]Studio> [/cyan]").strip()
                
                if choice == "1":
                    self.designer.show_task_palette()
                    
                elif choice == "2":
                    self._design_workflow_interactive()
                    
                elif choice == "3":
                    self._debug_workflow_interactive()
                    
                elif choice == "4":
                    self._monitor_execution_interactive()
                    
                elif choice == "5":
                    self._visualize_workflow_interactive()
                    
                elif choice == "6":
                    self._export_tools_interactive()
                    
                elif choice == "7":
                    console.print("[yellow]👋 Goodbye from Visual Workflow Studio![/yellow]")
                    break
                    
                else:
                    console.print("[red]❌ Invalid choice. Please select 1-7.[/red]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Studio session interrupted. Goodbye![/yellow]")
                break
    
    def _design_workflow_interactive(self):
        """Interactive workflow design"""
        console.print("\n[bold cyan]🎨 Workflow Designer[/bold cyan]")
        
        workflow_types = {
            "1": "basic_generation",
            "2": "ai_enhanced", 
            "3": "validation_only",
            "4": "custom"
        }
        
        console.print("\nSelect workflow template:")
        console.print("1. Basic Generation")
        console.print("2. AI Enhanced")
        console.print("3. Validation Only")
        console.print("4. Custom Template")
        
        choice = console.input("\n[cyan]Template> [/cyan]").strip()
        
        if choice in workflow_types:
            template = self.designer.create_workflow_template(workflow_types[choice])
            console.print(f"\n[green]✅ Generated {workflow_types[choice]} template:[/green]")
            console.print(Panel(template, title="Workflow Template", border_style="green"))
            
            save = console.input("\n[cyan]Save to file? (y/N): [/cyan]").strip().lower()
            if save == 'y':
                filename = console.input("[cyan]Filename: [/cyan]").strip()
                if filename:
                    Path(filename).write_text(template)
                    console.print(f"[green]💾 Saved to: {filename}[/green]")
        else:
            console.print("[red]❌ Invalid template choice[/red]")
    
    def _debug_workflow_interactive(self):
        """Interactive workflow debugging"""
        console.print("\n[bold cyan]🔍 Workflow Debugger[/bold cyan]")
        
        workflow = console.input("[cyan]Workflow file: [/cyan]").strip()
        if not workflow:
            console.print("[red]❌ No workflow specified[/red]")
            return
        
        # Mock context for debugging
        context = {
            "semantic_file": "test_semantic.yaml",
            "languages": ["python", "rust"],
            "debug_mode": True
        }
        
        self.debugger.debug_workflow_execution(workflow, context)
    
    def _monitor_execution_interactive(self):
        """Interactive execution monitoring"""
        console.print("\n[bold cyan]📊 Execution Monitor[/bold cyan]")
        
        # Show available executions
        executions = list(self.engine.monitor.executions.keys())
        if not executions:
            console.print("[yellow]⚠️ No executions available for monitoring[/yellow]")
            return
        
        console.print("\nAvailable executions:")
        for i, exec_id in enumerate(executions, 1):
            console.print(f"{i}. {exec_id}")
        
        try:
            choice = int(console.input("\n[cyan]Select execution (number): [/cyan]").strip())
            if 1 <= choice <= len(executions):
                execution_id = executions[choice - 1]
                self.monitor.show_performance_dashboard(execution_id)
            else:
                console.print("[red]❌ Invalid execution choice[/red]")
        except ValueError:
            console.print("[red]❌ Please enter a valid number[/red]")
    
    def _visualize_workflow_interactive(self):
        """Interactive workflow visualization"""
        console.print("\n[bold cyan]📊 Workflow Visualizer[/bold cyan]")
        
        workflow = console.input("[cyan]Workflow file: [/cyan]").strip()
        if not workflow:
            console.print("[red]❌ No workflow specified[/red]")
            return
        
        diagram = self.engine.visualize_workflow(workflow)
        console.print(Panel(diagram, title=f"Workflow: {workflow}", border_style="blue"))
        console.print("\n[dim]💡 Copy diagram to https://mermaid.live for visualization[/dim]")
    
    def _export_tools_interactive(self):
        """Interactive export tools"""
        console.print("\n[bold cyan]📤 Export Tools[/bold cyan]")
        
        console.print("\nExport options:")
        console.print("1. Task Catalog (JSON)")
        console.print("2. Task Catalog (Markdown)")
        console.print("3. Workflow Templates")
        console.print("4. Performance Reports")
        
        choice = console.input("\n[cyan]Export> [/cyan]").strip()
        
        if choice == "1":
            catalog = self.engine.export_task_catalog("json")
            filename = "task_catalog.json"
            Path(filename).write_text(catalog)
            console.print(f"[green]💾 Task catalog exported to: {filename}[/green]")
            
        elif choice == "2":
            # Convert to markdown format
            categories = self.engine.discover_tasks()
            markdown = "# BPMN Service Task Catalog\n\n"
            
            for category, tasks in categories.items():
                markdown += f"## {category.title()} Tasks\n\n"
                for task in tasks:
                    markdown += f"### {task.id}\n\n"
                    markdown += f"{task.description}\n\n"
                    markdown += "**Inputs:**\n"
                    for inp, type_ in task.inputs.items():
                        markdown += f"- {inp}: {type_}\n"
                    markdown += "\n**Outputs:**\n"
                    for out, type_ in task.outputs.items():
                        markdown += f"- {out}: {type_}\n"
                    markdown += "\n"
            
            filename = "task_catalog.md"
            Path(filename).write_text(markdown)
            console.print(f"[green]💾 Markdown catalog exported to: {filename}[/green]")
            
        else:
            console.print("[yellow]⚠️ Export option not implemented yet[/yellow]")