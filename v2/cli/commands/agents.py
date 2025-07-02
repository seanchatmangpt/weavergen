"""
WeaverGen v2 AI Agent Commands
Multi-agent system operations and orchestration
"""

import typer
import asyncio
import json
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

from ...core.engine.spiff_engine import WeaverGenV2Engine
from ...weavergen.src.visualizers.mermaid import MermaidVisualizer
from rich.syntax import Syntax

app = typer.Typer(
    name="agents",
    help="AI agent operations and multi-agent orchestration",
    rich_markup_mode="rich"
)

console = Console()

@app.command("communicate")
def agents_communicate(
    ctx: typer.Context,
    agents: int = typer.Option(3, "--agents", "-a", help="Number of agents"),
    mode: str = typer.Option("enhanced", "--mode", "-m", help="Communication mode: enhanced, otel, hybrid"),
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Communication topic"),
    max_rounds: int = typer.Option(5, "--rounds", "-r", help="Maximum communication rounds"),
    save_log: bool = typer.Option(True, "--save-log/--no-log", help="Save communication log")
):
    """Simulate agent communication and collaboration"""
    
    async def run_communicate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "agent_count": agents,
            "communication_config": {
                "mode": mode,
                "topic": topic or "Semantic Convention Design",
                "max_rounds": max_rounds,
                "enable_learning": True,
                "enable_consensus": True
            },
            "cli_command": "agents communicate"
        }
        
        console.print(Panel(
            f"[bold blue]Agent Communication[/bold blue]\n"
            f"Agents: {agents}\n"
            f"Mode: {mode}\n"
            f"Max Rounds: {max_rounds}",
            title="Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🤖 Agents communicating...", total=None)
            
            try:
                result = await engine.execute_workflow("agent_communication", context)
                
                if result.success:
                    comm_result = result.final_data.get("communication_result", {})
                    progress.update(task, description="✅ Communication complete")
                    
                    display_communication_results(comm_result, agents)
                    
                    if save_log:
                        log_file = Path(f"agent_communication_{mode}.json")
                        with open(log_file, 'w') as f:
                            json.dump(comm_result, f, indent=2)
                        console.print(f"[green]Communication log saved to: {log_file}[/green]")
                        
                else:
                    progress.update(task, description="❌ Communication failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Communication failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_communicate())

@app.command("validate")
def agents_validate(
    ctx: typer.Context,
    semantic_file: Path = typer.Argument(help="Semantic convention file to validate"),
    agents: int = typer.Option(3, "--agents", "-a", help="Number of validator agents"),
    deep: bool = typer.Option(False, "--deep", help="Enable deep validation"),
    consensus_threshold: float = typer.Option(0.8, "--consensus", help="Consensus threshold")
):
    """Multi-agent validation with consensus"""
    
    async def run_validate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "semantic_file": str(semantic_file),
            "agent_validation_config": {
                "agent_count": agents,
                "deep_validation": deep,
                "consensus_threshold": consensus_threshold,
                "validation_aspects": ["syntax", "semantics", "completeness", "consistency"]
            },
            "cli_command": "agents validate"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🤖 {agents} agents validating...", total=None)
            
            try:
                result = await engine.execute_workflow("agent_validation", context)
                
                if result.success:
                    validation_result = result.final_data.get("agent_validation_result", {})
                    progress.update(task, description="✅ Agent validation complete")
                    
                    display_agent_validation_results(validation_result, agents)
                else:
                    progress.update(task, description="❌ Agent validation failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Agent validation failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_validate())

@app.command("analyze")
def agents_analyze(
    ctx: typer.Context,
    files: List[Path] = typer.Argument(..., help="Files to analyze"),
    analysis_type: str = typer.Option("comprehensive", "--type", "-t", help="Analysis type"),
    agents: int = typer.Option(5, "--agents", "-a", help="Number of analyst agents"),
    output_format: str = typer.Option("rich", "--format", help="Output format: rich, json, markdown")
):
    """Multi-agent code analysis"""
    
    async def run_analyze():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "files": [str(f) for f in files],
            "analysis_config": {
                "analysis_type": analysis_type,
                "agent_count": agents,
                "aspects": ["structure", "quality", "performance", "security", "maintainability"],
                "generate_recommendations": True
            },
            "cli_command": "agents analyze"
        }
        
        console.print(f"[bold]Analyzing {len(files)} files with {agents} agents...[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Multi-agent analysis in progress...", total=None)
            
            try:
                result = await engine.execute_workflow("agent_analysis", context)
                
                if result.success:
                    analysis_result = result.final_data.get("analysis_result", {})
                    progress.update(task, description="✅ Analysis complete")
                    
                    display_analysis_results(analysis_result, output_format)
                else:
                    progress.update(task, description="❌ Analysis failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Analysis failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_analyze())

@app.command("orchestrate")
def agents_orchestrate(
    ctx: typer.Context,
    workflow: str = typer.Argument(help="Workflow to orchestrate: generate, validate, optimize"),
    agents: int = typer.Option(5, "--agents", "-a", help="Number of agents"),
    strategy: str = typer.Option("balanced", "--strategy", "-s", help="Orchestration strategy"),
    visualize: bool = typer.Option(True, "--visualize/--no-visualize", help="Visualize orchestration")
):
    """Orchestrate complex multi-agent workflows"""
    
    async def run_orchestrate():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "workflow_type": workflow,
            "orchestration_config": {
                "agent_count": agents,
                "strategy": strategy,
                "enable_adaptation": True,
                "enable_monitoring": True,
                "visualize_flow": visualize
            },
            "cli_command": "agents orchestrate"
        }
        
        console.print(Panel(
            f"[bold blue]Multi-Agent Orchestration[/bold blue]\n"
            f"Workflow: {workflow}\n"
            f"Agents: {agents}\n"
            f"Strategy: {strategy}",
            title="Orchestration Setup"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🎭 Orchestrating agents...", total=None)
            
            try:
                result = await engine.execute_workflow("agent_orchestration", context)
                
                if result.success:
                    orchestration_result = result.final_data.get("orchestration_result", {})
                    progress.update(task, description="✅ Orchestration complete")
                    
                    display_orchestration_results(orchestration_result, visualize)
                else:
                    progress.update(task, description="❌ Orchestration failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Orchestration failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_orchestrate())

@app.command("forge-to-agents")
def agents_forge_to_agents(
    ctx: typer.Context,
    semantic_yaml: Path = typer.Argument(help="Path to semantic convention YAML"),
    num_agents: int = typer.Option(3, "--num-agents", "-n", help="Number of agents to generate"),
    output_dir: Path = typer.Option(Path("./agent_system"), "--output", "-o"),
    include_tests: bool = typer.Option(True, "--tests/--no-tests", help="Generate agent tests")
):
    """Generate multi-agent system from Forge semantics"""
    
    async def run_forge_to_agents():
        engine = ctx.obj.get('engine', WeaverGenV2Engine())
        
        context = {
            "semantic_file": str(semantic_yaml),
            "forge_to_agents_config": {
                "num_agents": num_agents,
                "output_dir": str(output_dir),
                "include_tests": include_tests,
                "agent_roles": ["validator", "generator", "optimizer"],
                "communication_protocol": "enhanced"
            },
            "cli_command": "agents forge-to-agents"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔨 Converting Forge to agents...", total=None)
            
            try:
                result = await engine.execute_workflow("forge_to_agents", context)
                
                if result.success:
                    conversion_result = result.final_data.get("conversion_result", {})
                    progress.update(task, description="✅ Conversion complete")
                    
                    display_forge_conversion_results(conversion_result, num_agents)
                    console.print(f"[green]Agent system generated in: {output_dir}[/green]")
                else:
                    progress.update(task, description="❌ Conversion failed")
                    console.print(f"[red]Error: {result.error}[/red]")
                    raise typer.Exit(1)
                    
            except Exception as e:
                progress.update(task, description="❌ Conversion failed")
                console.print(f"[red]Unexpected error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_forge_to_agents())

@app.command("visualize")
def agents_visualize(
    ctx: typer.Context,
    style: str = typer.Option(
        "communication",
        "--style", "-s",
        help="Visualization style: communication, hierarchy, lifecycle, collaboration"
    ),
    agents: int = typer.Option(
        3,
        "--agents", "-a",
        help="Number of agents to visualize"
    ),
    scenario: Optional[str] = typer.Option(
        None,
        "--scenario",
        help="Scenario to visualize: decision, collaborative, hierarchical"
    ),
    include_spans: bool = typer.Option(
        True,
        "--spans",
        help="Include OTel span annotations"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save diagram to file"
    ),
):
    """Visualize agent system interactions and architecture"""
    
    visualizer = MermaidVisualizer()
    
    console.print(f"[bold]Generating {style} visualization for {agents} agents...[/bold]")
    
    try:
        diagram = None
        
        if style == "communication":
            # Build communication data
            agent_list = [{"id": f"Agent_{i}", "name": f"Agent {i}"} for i in range(agents)]
            
            messages = []
            if scenario == "decision":
                messages.extend([
                    {"from": "Agent_0", "to": "Agent_1", "type": "request", "content": "Validate semantic conventions"},
                    {"from": "Agent_1", "to": "Agent_0", "type": "decision", "content": "Approved", "duration_ms": 150},
                    {"from": "Agent_0", "to": "Agent_2", "type": "notify", "content": "Validation complete"}
                ])
            elif scenario == "collaborative":
                for i in range(agents - 1):
                    messages.append({
                        "from": f"Agent_{i}",
                        "to": f"Agent_{i+1}",
                        "type": "collaborate",
                        "content": f"Processing step {i+1}",
                        "duration_ms": 100 + i * 50
                    })
            else:  # Default scenario
                messages.append({"from": "Agent_0", "to": "OTel", "type": "broadcast", "content": "System initialized"})
                for i in range(1, agents):
                    messages.append({
                        "from": f"Agent_{i}",
                        "to": "Agent_0",
                        "type": "response",
                        "content": f"Agent {i} ready",
                        "duration_ms": 50
                    })
            
            comm_data = {
                "agents": agent_list,
                "messages": messages,
                "include_spans": include_spans
            }
            diagram = visualizer.generate_agent_communication_diagram(comm_data)
            
        elif style == "hierarchy":
            # Generate hierarchical agent structure
            lines = ["graph TD"]
            lines.append("    Orchestrator[Orchestrator Agent]")
            
            # Add agent layers
            for i in range(agents):
                lines.append(f"    Agent{i}[Agent {i}]")
                lines.append(f"    Orchestrator --> Agent{i}")
            
            # Add sub-agents if many agents
            if agents > 3:
                for i in range(min(2, agents)):
                    lines.append(f"    SubAgent{i}[Sub-Agent {i}]")
                    lines.append(f"    Agent{i} --> SubAgent{i}")
            
            diagram = "\n".join(lines)
            
        elif style == "lifecycle":
            # Use lifecycle generator for agent lifecycle
            from ...weavergen.src.visualizers.mermaid import MermaidLifecycleGenerator
            lifecycle_gen = MermaidLifecycleGenerator()
            diagram = lifecycle_gen.generate_agent_lifecycle(agents)
            
        elif style == "collaboration":
            # Generate collaboration flow
            lines = ["graph LR"]
            lines.append("    subgraph Collaboration")
            
            for i in range(agents):
                lines.append(f"        A{i}[Agent {i}]")
            
            # Create collaboration links
            for i in range(agents):
                for j in range(i+1, agents):
                    lines.append(f"        A{i} <--> A{j}")
            
            lines.append("    end")
            
            # Add shared resources
            lines.append("    SharedMem[(Shared Memory)]")
            lines.append("    OTel[(OTel Spans)]")
            
            for i in range(agents):
                lines.append(f"    A{i} --> SharedMem")
                lines.append(f"    A{i} --> OTel")
            
            diagram = "\n".join(lines)
            
        else:
            console.print(f"[red]Unknown visualization style: {style}[/red]")
            raise typer.Exit(1)
        
        if diagram:
            # Display diagram
            console.print(Panel(
                Syntax(diagram, "mermaid", theme="monokai"),
                title=f"[bold cyan]Agent {style.title()} Visualization[/bold cyan]"
            ))
            
            if output:
                output.write_text(f"```mermaid\n{diagram}\n```")
                console.print(f"[green]Diagram saved to: {output}[/green]")
                
    except Exception as e:
        console.print(f"[red]Error generating visualization: {e}[/red]")
        raise typer.Exit(1)

# Display helper functions

def display_communication_results(result: dict, agents: int):
    """Display agent communication results"""
    rounds = result.get("rounds_completed", 0)
    consensus_reached = result.get("consensus_reached", False)
    
    table = Table(title="Communication Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Agents", str(agents))
    table.add_row("Rounds Completed", str(rounds))
    table.add_row("Messages Exchanged", str(result.get("message_count", 0)))
    table.add_row("Consensus Reached", "✅ Yes" if consensus_reached else "❌ No")
    table.add_row("Final Agreement", f"{result.get('agreement_level', 0):.1%}")
    
    console.print(table)
    
    # Show conversation highlights
    highlights = result.get("conversation_highlights", [])
    if highlights:
        console.print("\n[bold]Conversation Highlights:[/bold]")
        for highlight in highlights[:5]:
            console.print(f"  • {highlight}")

def display_agent_validation_results(result: dict, agents: int):
    """Display multi-agent validation results"""
    consensus_score = result.get("consensus_score", 0)
    overall_valid = result.get("overall_valid", False)
    
    console.print(Panel(
        f"[bold]{'✅ VALID' if overall_valid else '❌ INVALID'}[/bold]\n"
        f"Consensus Score: {consensus_score:.1%}\n"
        f"Participating Agents: {agents}",
        title="Agent Validation Result"
    ))
    
    # Show individual agent verdicts
    agent_verdicts = result.get("agent_verdicts", {})
    if agent_verdicts:
        table = Table(title="Agent Verdicts")
        table.add_column("Agent", style="cyan")
        table.add_column("Verdict", style="magenta")
        table.add_column("Confidence", style="green")
        
        for agent_id, verdict in agent_verdicts.items():
            table.add_row(
                agent_id,
                "✅ Valid" if verdict["valid"] else "❌ Invalid",
                f"{verdict.get('confidence', 0):.1%}"
            )
        
        console.print(table)

def display_analysis_results(result: dict, output_format: str):
    """Display multi-agent analysis results"""
    if output_format == "json":
        console.print_json(json.dumps(result, indent=2))
        return
    
    # Create analysis tree
    tree = Tree("[bold]Multi-Agent Analysis Results[/bold]")
    
    for file_path, file_analysis in result.get("file_analyses", {}).items():
        file_branch = tree.add(f"📄 {Path(file_path).name}")
        
        for aspect, aspect_data in file_analysis.items():
            aspect_branch = file_branch.add(f"[cyan]{aspect}[/cyan]")
            score = aspect_data.get("score", 0)
            aspect_branch.add(f"Score: {score:.1%}")
            
            findings = aspect_data.get("findings", [])
            if findings:
                findings_branch = aspect_branch.add("Findings:")
                for finding in findings[:3]:
                    findings_branch.add(f"• {finding}")
    
    console.print(tree)
    
    # Overall recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(recommendations[:5], 1):
            console.print(f"{i}. {rec}")

def display_orchestration_results(result: dict, visualize: bool):
    """Display orchestration results"""
    table = Table(title="Orchestration Performance")
    table.add_column("Phase", style="cyan")
    table.add_column("Duration", style="green")
    table.add_column("Agents", style="magenta")
    table.add_column("Status", style="yellow")
    
    phases = result.get("phases", [])
    for phase in phases:
        table.add_row(
            phase["name"],
            f"{phase.get('duration', 0):.2f}s",
            str(phase.get('agent_count', 0)),
            "✅" if phase.get('successful', False) else "❌"
        )
    
    console.print(table)
    
    if visualize and result.get("flow_diagram"):
        console.print("\n[bold]Orchestration Flow:[/bold]")
        console.print("```mermaid")
        console.print(result["flow_diagram"])
        console.print("```")

def display_forge_conversion_results(result: dict, num_agents: int):
    """Display Forge to agents conversion results"""
    table = Table(title="Agent System Generation")
    table.add_column("Component", style="cyan")
    table.add_column("Generated", style="green")
    
    table.add_row("Agent Classes", str(result.get("agent_classes_count", 0)))
    table.add_row("Communication Protocols", str(result.get("protocol_count", 0)))
    table.add_row("Shared Models", str(result.get("model_count", 0)))
    table.add_row("Test Suites", str(result.get("test_count", 0)))
    table.add_row("Configuration Files", str(result.get("config_count", 0)))
    
    console.print(table)
    
    # Show agent roles
    agent_roles = result.get("agent_roles", [])
    if agent_roles:
        console.print("\n[bold]Generated Agent Roles:[/bold]")
        for role in agent_roles:
            console.print(f"  • {role['name']}: {role['description']}")

@app.command("visualize")
def agents_visualize(
    ctx: typer.Context,
    style: str = typer.Option("communication", "--style", "-s", 
                             help="Visualization style: communication, hierarchy, lifecycle, collaboration"),
    agents: int = typer.Option(3, "--agents", "-a", help="Number of agents to visualize"),
    include_spans: bool = typer.Option(True, "--spans/--no-spans", help="Include OTel spans in diagram"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save diagram to file")
):
    """Visualize agent system architecture and communication"""
    
    visualizer = MermaidVisualizer()
    
    console.print(f"[bold cyan]🎨 Generating {style} visualization for {agents} agents...[/bold cyan]")
    
    try:
        diagram = ""
        
        if style == "communication":
            # Generate agent communication diagram
            comm_data = {
                "agents": [
                    {"id": f"Agent{i}", "name": f"Agent {i}"} 
                    for i in range(1, agents + 1)
                ],
                "messages": [
                    {
                        "from": "Agent1",
                        "to": "Agent2",
                        "type": "request",
                        "content": "Analyze semantic conventions",
                        "duration_ms": 150
                    },
                    {
                        "from": "Agent2",
                        "type": "decision",
                        "content": "Schema validation passed",
                        "duration_ms": 200
                    },
                    {
                        "from": "Agent3",
                        "to": "Agent1",
                        "type": "response",
                        "content": "Code generation complete",
                        "duration_ms": 300
                    }
                ]
            }
            diagram = visualizer.generate_agent_communication_diagram(comm_data)
            
        elif style == "hierarchy":
            # Generate agent hierarchy diagram
            lines = ["graph TD"]
            lines.append("    Orchestrator[Orchestrator Agent]")
            
            for i in range(1, agents + 1):
                lines.append(f"    Agent{i}[Agent {i}]")
                lines.append(f"    Orchestrator --> Agent{i}")
            
            if include_spans:
                lines.append("    OTel[OpenTelemetry]")
                for i in range(1, agents + 1):
                    lines.append(f"    Agent{i} -.-> OTel")
            
            diagram = "\n".join(lines)
            
        elif style == "lifecycle":
            # Generate agent lifecycle diagram
            lines = ["stateDiagram-v2"]
            lines.append("    [*] --> Initialization")
            lines.append("    Initialization --> Loading: Load Models")
            lines.append("    Loading --> Ready: Models Loaded")
            lines.append("    Ready --> Processing: Receive Task")
            lines.append("    Processing --> Communicating: Send Message")
            lines.append("    Communicating --> Processing: Continue")
            lines.append("    Processing --> Decision: Make Decision")
            lines.append("    Decision --> Reporting: Report Results")
            lines.append("    Reporting --> Ready: Task Complete")
            lines.append("    Ready --> Shutdown: Terminate Signal")
            lines.append("    Shutdown --> [*]")
            
            diagram = "\n".join(lines)
            
        elif style == "collaboration":
            # Generate collaboration flow diagram
            lines = ["graph LR"]
            lines.append("    subgraph Agents[Agent Collaboration]")
            
            for i in range(1, agents + 1):
                role = ["Analyzer", "Validator", "Generator"][i % 3]
                lines.append(f"        A{i}[{role} Agent {i}]")
            
            lines.append("    end")
            lines.append("    ")
            lines.append("    Input[Semantic YAML] --> A1")
            
            for i in range(1, agents):
                lines.append(f"    A{i} --> A{i+1}")
            
            lines.append(f"    A{agents} --> Output[Generated Code]")
            
            if include_spans:
                lines.append("    ")
                lines.append("    subgraph Telemetry[Telemetry]")
                lines.append("        Spans[OTel Spans]")
                lines.append("        Metrics[Performance Metrics]")
                lines.append("    end")
                lines.append("    ")
                for i in range(1, agents + 1):
                    lines.append(f"    A{i} -.-> Spans")
            
            diagram = "\n".join(lines)
            
        else:
            console.print(f"[red]Unknown style: {style}[/red]")
            console.print("[yellow]Valid styles: communication, hierarchy, lifecycle, collaboration[/yellow]")
            raise typer.Exit(1)
        
        # Display the diagram
        console.print("\n[bold]Mermaid Diagram:[/bold]")
        console.print("```mermaid")
        console.print(diagram)
        console.print("```")
        
        console.print("\n[dim]💡 Tip: Use this diagram to understand agent interactions[/dim]")
        
        # Save to file if requested
        if output:
            output.write_text(diagram)
            console.print(f"[green]✅ Diagram saved to: {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error generating visualization: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()