#!/usr/bin/env python3
"""Check and setup Ollama for pydantic-ai examples.

This script verifies that Ollama is installed and running,
checks for required models, and helps set up the environment.
"""

import subprocess
import sys
import json
import time
from typing import List, Tuple, Optional
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console()


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


def check_ollama_installed() -> bool:
    """Check if Ollama is installed."""
    console.print("\n[blue]Checking Ollama installation...[/blue]")
    
    code, stdout, stderr = run_command(["ollama", "--version"])
    
    if code == 0:
        version = stdout.strip()
        console.print(f"✅ Ollama is installed: {version}")
        return True
    else:
        console.print("❌ Ollama is not installed")
        console.print("\n[yellow]To install Ollama:[/yellow]")
        console.print("  macOS: brew install ollama")
        console.print("  Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        console.print("  Visit: https://ollama.ai")
        return False


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    console.print("\n[blue]Checking Ollama service...[/blue]")
    
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if response.status_code == 200:
            console.print("✅ Ollama service is running")
            return True
    except (httpx.ConnectError, httpx.TimeoutException):
        pass
    
    console.print("❌ Ollama service is not running")
    console.print("\n[yellow]To start Ollama:[/yellow]")
    console.print("  Run: ollama serve")
    return False


def get_installed_models() -> List[dict]:
    """Get list of installed models."""
    try:
        response = httpx.get("http://localhost:11434/api/tags")
        data = response.json()
        return data.get("models", [])
    except:
        return []


def check_models() -> Tuple[bool, List[str]]:
    """Check for recommended models."""
    console.print("\n[blue]Checking installed models...[/blue]")
    
    recommended_models = {
        "qwen3:latest": "Best overall performance",
        "llama3.2:latest": "Good general purpose",
        "mistral:latest": "Fast and efficient",
        "codellama:latest": "Better for code generation"
    }
    
    installed_models = get_installed_models()
    installed_names = [m["name"] for m in installed_models]
    
    # Display installed models
    if installed_models:
        table = Table(title="Installed Models")
        table.add_column("Model", style="cyan")
        table.add_column("Size", style="yellow")
        table.add_column("Modified", style="green")
        
        for model in installed_models:
            size_gb = model["size"] / (1024**3)
            table.add_row(
                model["name"],
                f"{size_gb:.1f} GB",
                model["modified_at"][:10]
            )
        
        console.print(table)
    else:
        console.print("❌ No models installed")
    
    # Check for recommended models
    missing_models = []
    for model, desc in recommended_models.items():
        if model not in installed_names:
            missing_models.append(model)
    
    if missing_models:
        console.print("\n[yellow]Recommended models not installed:[/yellow]")
        for model in missing_models:
            console.print(f"  - {model}: {recommended_models[model]}")
    
    # At least one recommended model should be installed
    has_recommended = any(model in installed_names for model in recommended_models)
    
    if has_recommended:
        console.print("\n✅ At least one recommended model is installed")
    else:
        console.print("\n❌ No recommended models found")
    
    return has_recommended, missing_models


def pull_model(model_name: str) -> bool:
    """Pull a model from Ollama."""
    console.print(f"\n[blue]Pulling model: {model_name}[/blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Downloading {model_name}...", total=None)
        
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor the process
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                progress.update(task, description=line.strip()[:60] + "...")
        
        return_code = process.wait()
        
    if return_code == 0:
        console.print(f"✅ Successfully pulled {model_name}")
        return True
    else:
        console.print(f"❌ Failed to pull {model_name}")
        return False


def test_openai_compatibility() -> bool:
    """Test OpenAI compatibility endpoint."""
    console.print("\n[blue]Testing OpenAI compatibility...[/blue]")
    
    try:
        response = httpx.get("http://localhost:11434/v1/models")
        if response.status_code == 200:
            data = response.json()
            if data.get("object") == "list":
                console.print("✅ OpenAI compatibility endpoint is working")
                return True
    except:
        pass
    
    console.print("❌ OpenAI compatibility endpoint not accessible")
    return False


def run_quick_test() -> bool:
    """Run a quick test with pydantic-ai."""
    console.print("\n[blue]Running quick pydantic-ai test...[/blue]")
    
    try:
        import os
        os.environ["OPENAI_API_KEY"] = "ollama"
        os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
        
        from pydantic import BaseModel
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIModel
        
        class TestOutput(BaseModel):
            message: str
        
        # Use first available model
        models = get_installed_models()
        if not models:
            console.print("❌ No models available for testing")
            return False
        
        model_name = models[0]["name"]
        console.print(f"Testing with model: {model_name}")
        
        agent = Agent(
            OpenAIModel(model_name=model_name),
            result_type=TestOutput
        )
        
        import asyncio
        result = asyncio.run(agent.run("Say hello"))
        
        console.print(f"✅ Test successful! Response: {result.output.message}")
        return True
        
    except Exception as e:
        console.print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup checker."""
    console.print(Panel.fit(
        "[bold]Ollama Setup Checker for Pydantic-AI Examples[/bold]",
        border_style="blue"
    ))
    
    # Track overall status
    all_good = True
    
    # 1. Check Ollama installation
    if not check_ollama_installed():
        all_good = False
        console.print("\n[red]Please install Ollama first[/red]")
        sys.exit(1)
    
    # 2. Check if service is running
    if not check_ollama_running():
        console.print("\n[yellow]Starting Ollama service...[/yellow]")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # Give it time to start
        
        if not check_ollama_running():
            all_good = False
            console.print("\n[red]Failed to start Ollama service[/red]")
            sys.exit(1)
    
    # 3. Check models
    has_models, missing_models = check_models()
    
    if not has_models:
        console.print("\n[yellow]Would you like to install qwen3:latest? (recommended)[/yellow]")
        if input("Install? (y/n): ").lower() == 'y':
            if pull_model("qwen3:latest"):
                has_models = True
            else:
                all_good = False
    
    # 4. Test OpenAI compatibility
    if not test_openai_compatibility():
        all_good = False
    
    # 5. Run quick test
    if has_models:
        if not run_quick_test():
            all_good = False
    
    # Summary
    console.print("\n" + "="*50)
    if all_good:
        console.print(Panel.fit(
            "✅ [bold green]All checks passed![/bold green]\n\n"
            "You're ready to run the examples:\n"
            "  python -m weavergen.examples.structured_output_ollama\n"
            "  python -m weavergen.examples.sql_gen_ollama_simple",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            "⚠️  [bold yellow]Some checks failed[/bold yellow]\n\n"
            "Please address the issues above before running examples.",
            border_style="yellow"
        ))
    
    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())