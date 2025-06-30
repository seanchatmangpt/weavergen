"""Utilities for Ollama integration with pydantic-ai."""

import os
import sys
from typing import Optional, List
import httpx
from pydantic_ai.models.openai import OpenAIModel
from rich.console import Console


console = Console()


class OllamaConnectionError(Exception):
    """Raised when Ollama connection fails."""
    pass


class OllamaModelNotFoundError(Exception):
    """Raised when requested model is not found."""
    pass


def check_ollama_connection() -> bool:
    """Check if Ollama is accessible."""
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def get_available_models() -> List[str]:
    """Get list of available Ollama models."""
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except:
        return []


def setup_ollama_env(base_url: str = "http://localhost:11434/v1"):
    """Set up environment variables for Ollama."""
    os.environ["OPENAI_API_KEY"] = "ollama"
    os.environ["OPENAI_BASE_URL"] = base_url


def get_ollama_model(
    model_name: str = "qwen3:latest",
    fallback_models: Optional[List[str]] = None,
    check_connection: bool = True
) -> OpenAIModel:
    """Get an Ollama model with error handling and fallbacks.
    
    Args:
        model_name: Primary model to use
        fallback_models: List of fallback models to try
        check_connection: Whether to check Ollama connection first
        
    Returns:
        OpenAIModel configured for Ollama
        
    Raises:
        OllamaConnectionError: If Ollama is not accessible
        OllamaModelNotFoundError: If no suitable model is found
    """
    if fallback_models is None:
        fallback_models = ["llama3.2:latest", "mistral:latest"]
    
    # Set up environment
    setup_ollama_env()
    
    if check_connection:
        if not check_ollama_connection():
            console.print("[red]❌ Cannot connect to Ollama[/red]")
            console.print("\n[yellow]Please ensure Ollama is running:[/yellow]")
            console.print("  Run: ollama serve")
            raise OllamaConnectionError("Cannot connect to Ollama service at localhost:11434")
        
        # Check available models
        available = get_available_models()
        if not available:
            console.print("[red]❌ No models installed[/red]")
            console.print("\n[yellow]Install a model first:[/yellow]")
            console.print(f"  Run: ollama pull {model_name}")
            raise OllamaModelNotFoundError("No Ollama models installed")
        
        # Try primary model
        if model_name in available:
            return OpenAIModel(model_name=model_name)
        
        # Try fallbacks
        for fallback in fallback_models:
            if fallback in available:
                console.print(f"[yellow]Model '{model_name}' not found, using '{fallback}'[/yellow]")
                return OpenAIModel(model_name=fallback)
        
        # No suitable model found
        console.print(f"[red]❌ Model '{model_name}' not found[/red]")
        console.print(f"\n[yellow]Available models:[/yellow] {', '.join(available)}")
        console.print(f"\n[yellow]Install the model:[/yellow]")
        console.print(f"  Run: ollama pull {model_name}")
        raise OllamaModelNotFoundError(f"Model '{model_name}' not found")
    
    # If not checking connection, just return the model
    return OpenAIModel(model_name=model_name)


def handle_ollama_error(func):
    """Decorator to handle Ollama-specific errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OllamaConnectionError:
            console.print("\n[red]Failed to connect to Ollama.[/red]")
            console.print("Run: python -m weavergen.examples.check_setup")
            sys.exit(1)
        except OllamaModelNotFoundError:
            console.print("\n[red]Required model not found.[/red]")
            console.print("Run: python -m weavergen.examples.check_setup")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[red]Unexpected error: {e}[/red]")
            raise
    
    return wrapper