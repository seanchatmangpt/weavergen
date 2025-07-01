#!/usr/bin/env python3
"""
Debug CLI for WeaverGen - Testing and debugging commands
"""

import asyncio
import time
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel

# Local imports
from .examples.ollama_utils import (
    check_ollama_connection,
    get_available_models,
    get_ollama_model,
    OllamaConnectionError,
    OllamaModelNotFoundError
)

app = typer.Typer(name="weavergen-debug", help="Debug and testing CLI for WeaverGen")
console = Console()


@app.command()
def check_ollama():
    """Check Ollama connection and available models."""
    console.print("[bold blue]🔍 Checking Ollama Setup...[/bold blue]")
    
    # Check connection
    if check_ollama_connection():
        console.print("✅ Ollama connection: [green]OK[/green]")
    else:
        console.print("❌ Ollama connection: [red]FAILED[/red]")
        console.print("Run: [yellow]ollama serve[/yellow]")
        return
    
    # Get models
    models = get_available_models()
    if models:
        console.print(f"✅ Available models: [green]{len(models)} found[/green]")
        
        table = Table(title="Available Models")
        table.add_column("Model Name", style="cyan")
        
        for model in models:
            table.add_row(model)
        
        console.print(table)
    else:
        console.print("❌ No models found")
        console.print("Install a model: [yellow]ollama pull qwen3:latest[/yellow]")


@app.command()
def test_agent_basic(
    model: str = typer.Option("qwen3:latest", help="Model to test"),
    timeout: int = typer.Option(30, help="Timeout in seconds")
):
    """Test basic agent functionality with timeout."""
    console.print(f"[bold blue]🤖 Testing Basic Agent with {model}...[/bold blue]")
    
    async def _test():
        try:
            # Import here to avoid startup issues
            from pydantic_ai import Agent
            from .examples.ollama_utils import get_ollama_model
            
            # Create simple agent
            test_agent = Agent(
                get_ollama_model(model),
                system_prompt="You are a helpful assistant. Keep responses short and clear."
            )
            
            # Test with timeout
            start_time = time.time()
            
            with console.status(f"Testing agent with {timeout}s timeout..."):
                try:
                    result = await asyncio.wait_for(
                        test_agent.run("What is 2+2? Answer in one word."),
                        timeout=timeout
                    )
                    
                    elapsed = time.time() - start_time
                    console.print(f"✅ Agent response in {elapsed:.2f}s: [green]{result.output}[/green]")
                    
                except asyncio.TimeoutError:
                    console.print(f"❌ Agent timed out after {timeout}s")
                    console.print("Try reducing model size or increasing timeout")
                    
        except Exception as e:
            console.print(f"❌ Agent test failed: [red]{e}[/red]")
    
    asyncio.run(_test())


@app.command()
def test_multi_agent_simple(
    timeout: int = typer.Option(60, help="Timeout in seconds")
):
    """Test simplified multi-agent pattern."""
    console.print("[bold blue]🔗 Testing Simple Multi-Agent Pattern...[/bold blue]")
    
    async def _test():
        try:
            from pydantic_ai import Agent
            from .examples.ollama_utils import get_ollama_model
            
            # Create two simple agents
            analyzer = Agent(
                get_ollama_model("qwen3:latest"),
                system_prompt="Analyze the input and return one word summary."
            )
            
            responder = Agent(
                get_ollama_model("qwen3:latest"), 
                system_prompt="Respond to the analysis with a simple action."
            )
            
            start_time = time.time()
            
            with Progress() as progress:
                task = progress.add_task("Running agents...", total=2)
                
                # Agent 1: Analyze
                progress.update(task, description="Agent 1: Analyzing...")
                analysis = await asyncio.wait_for(
                    analyzer.run("The weather is sunny and warm"),
                    timeout=timeout // 2
                )
                progress.advance(task)
                
                # Agent 2: Respond  
                progress.update(task, description="Agent 2: Responding...")
                response = await asyncio.wait_for(
                    responder.run(f"Analysis result: {analysis.output}"),
                    timeout=timeout // 2
                )
                progress.advance(task)
            
            elapsed = time.time() - start_time
            
            console.print(Panel(
                f"Analysis: {analysis.output}\nResponse: {response.output}",
                title=f"✅ Multi-Agent Success ({elapsed:.2f}s)",
                border_style="green"
            ))
            
        except asyncio.TimeoutError:
            console.print(f"❌ Multi-agent test timed out after {timeout}s")
        except Exception as e:
            console.print(f"❌ Multi-agent test failed: [red]{e}[/red]")
    
    asyncio.run(_test())


@app.command()
def test_span_validation():
    """Test OpenTelemetry span validation."""
    console.print("[bold blue]📊 Testing Span Validation...[/bold blue]")
    
    async def _test():
        try:
            from .layers.otel_validation import run_architecture_validation
            
            with console.status("Running architecture validation..."):
                await run_architecture_validation()
                
            console.print("✅ Span validation completed successfully")
            
        except Exception as e:
            console.print(f"❌ Span validation failed: [red]{e}[/red]")
    
    asyncio.run(_test())


@app.command()
def test_gap_validation():
    """Test gap validation that unit tests miss."""
    console.print("[bold blue]🔍 Testing Gap Validation...[/bold blue]")
    
    async def _test():
        try:
            from .layers.span_gap_validation import ComprehensiveGapValidator
            
            validator = ComprehensiveGapValidator()
            
            with console.status("Running gap validation..."):
                await validator.validate_all_gaps()
                
            console.print("✅ Gap validation completed successfully")
            
        except Exception as e:
            console.print(f"❌ Gap validation failed: [red]{e}[/red]")
    
    asyncio.run(_test())


@app.command()
def run_layers_demo():
    """Test the 4-layer architecture demo."""
    console.print("[bold blue]🏗️ Testing 4-Layer Architecture...[/bold blue]")
    
    try:
        from .layers.demo import main as demo_main
        
        with console.status("Running layers demo..."):
            demo_main()
            
        console.print("✅ Layers demo completed successfully")
        
    except Exception as e:
        console.print(f"❌ Layers demo failed: [red]{e}[/red]")


@app.command()
def debug_multi_agent_timeout(
    model: str = typer.Option("qwen3:latest", help="Model to debug"),
    step_timeout: int = typer.Option(10, help="Timeout per step")
):
    """Debug multi-agent timeout issues step by step."""
    console.print(f"[bold blue]🐛 Debugging Multi-Agent Timeout with {model}...[/bold blue]")
    
    async def _test():
        try:
            from pydantic_ai import Agent
            from .examples.ollama_utils import get_ollama_model
            from .layers.contracts import SemanticConvention, TargetLanguage
            
            # Test each component step by step
            steps = [
                ("Model Connection", lambda: get_ollama_model(model)),
                ("Agent Creation", lambda: Agent(get_ollama_model(model), system_prompt="Test")),
                ("Simple Query", None),  # Will be async
                ("Multi-Agent Setup", None),  # Will be async
            ]
            
            results = {}
            
            for i, (step_name, sync_test) in enumerate(steps, 1):
                console.print(f"\n[yellow]{i}. {step_name}...[/yellow]")
                
                try:
                    start_time = time.time()
                    
                    if sync_test:
                        # Synchronous test
                        result = sync_test()
                        elapsed = time.time() - start_time
                        console.print(f"  ✅ {step_name}: {elapsed:.2f}s")
                        results[step_name] = {"success": True, "time": elapsed}
                        
                    elif step_name == "Simple Query":
                        # Test simple async query
                        agent = Agent(get_ollama_model(model), system_prompt="Answer briefly")
                        result = await asyncio.wait_for(
                            agent.run("Say 'OK'"),
                            timeout=step_timeout
                        )
                        elapsed = time.time() - start_time
                        console.print(f"  ✅ {step_name}: {elapsed:.2f}s - {result.output}")
                        results[step_name] = {"success": True, "time": elapsed}
                        
                    elif step_name == "Multi-Agent Setup":
                        # Test multi-agent pattern
                        agent1 = Agent(get_ollama_model(model), system_prompt="Return 'STEP1'")
                        agent2 = Agent(get_ollama_model(model), system_prompt="Return 'STEP2'")
                        
                        # Sequential execution
                        result1 = await asyncio.wait_for(
                            agent1.run("Execute step 1"),
                            timeout=step_timeout
                        )
                        result2 = await asyncio.wait_for(
                            agent2.run("Execute step 2"),
                            timeout=step_timeout
                        )
                        
                        elapsed = time.time() - start_time
                        console.print(f"  ✅ {step_name}: {elapsed:.2f}s - {result1.output}, {result2.output}")
                        results[step_name] = {"success": True, "time": elapsed}
                        
                except asyncio.TimeoutError:
                    console.print(f"  ❌ {step_name}: TIMEOUT after {step_timeout}s")
                    results[step_name] = {"success": False, "error": "timeout"}
                    break
                except Exception as e:
                    console.print(f"  ❌ {step_name}: ERROR - {e}")
                    results[step_name] = {"success": False, "error": str(e)}
                    break
            
            # Summary
            console.print("\n[bold]Debug Summary:[/bold]")
            for step, result in results.items():
                if result["success"]:
                    console.print(f"  ✅ {step}: {result['time']:.2f}s")
                else:
                    console.print(f"  ❌ {step}: {result['error']}")
                    
        except Exception as e:
            console.print(f"❌ Debug failed: [red]{e}[/red]")
    
    asyncio.run(_test())


@app.command()
def health_check():
    """Complete health check of all WeaverGen components."""
    console.print("[bold blue]🏥 WeaverGen Health Check...[/bold blue]")
    
    checks = [
        ("Python Environment", lambda: True),
        ("Ollama Connection", check_ollama_connection),
        ("Available Models", lambda: len(get_available_models()) > 0),
        ("PydanticAI Import", lambda: __import__("pydantic_ai")),
        ("WeaverGen Layers", lambda: __import__("weavergen.layers")),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            status = "✅ PASS" if result else "❌ FAIL"
            results.append((check_name, status, ""))
        except Exception as e:
            results.append((check_name, "❌ ERROR", str(e)))
    
    # Display results
    table = Table(title="Health Check Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")
    
    for name, status, details in results:
        table.add_row(name, status, details)
    
    console.print(table)
    
    # Overall status
    failed = [r for r in results if "FAIL" in r[1] or "ERROR" in r[1]]
    if failed:
        console.print(f"\n❌ {len(failed)} components failed")
        return False
    else:
        console.print("\n✅ All components healthy")
        return True


if __name__ == "__main__":
    app()