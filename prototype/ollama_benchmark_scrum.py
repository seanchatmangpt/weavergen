#!/usr/bin/env python3
"""
Benchmark Ollama performance for Scrum at Scale simulation with GPU monitoring.
Tests response times, token generation, and system resource usage on macOS.
"""

import subprocess
import time
import psutil
import asyncio
from datetime import datetime
import json
import statistics
from typing import Dict, List, Any
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel

# OpenTelemetry setup
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

# Models for benchmarking
class BenchmarkResult(BaseModel):
    operation: str
    model: str
    duration_ms: float
    tokens_generated: int
    tokens_per_second: float
    cpu_percent: float
    memory_mb: float
    gpu_active: bool
    timestamp: str

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    gpu_info: Dict[str, Any]

def get_gpu_info_macos() -> Dict[str, Any]:
    """Get GPU information on macOS using system_profiler"""
    try:
        # Get GPU info from system_profiler
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType", "-json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            displays = data.get("SPDisplaysDataType", [])
            
            gpu_info = {
                "gpu_found": False,
                "gpu_name": "Unknown",
                "gpu_vram": "Unknown",
                "metal_support": False,
                "gpu_cores": "Unknown"
            }
            
            for display in displays:
                if "sppci_model" in display:
                    gpu_info["gpu_found"] = True
                    gpu_info["gpu_name"] = display.get("sppci_model", "Unknown")
                    gpu_info["gpu_vram"] = display.get("sppci_vram", "Unknown")
                    gpu_info["metal_support"] = "Metal" in display.get("sppci_metal", "")
                    gpu_info["gpu_cores"] = display.get("sppci_cores", "Unknown")
                    break
            
            return gpu_info
    except Exception as e:
        return {"error": str(e)}
    
    return {"gpu_found": False}

def get_ollama_gpu_usage() -> Dict[str, Any]:
    """Check if Ollama is using GPU acceleration"""
    try:
        # Check Ollama process
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        ollama_running = "ollama" in result.stdout
        
        # Check for Metal usage (macOS GPU acceleration)
        metal_check = subprocess.run(
            ["ioreg", "-l", "-w", "0"],
            capture_output=True,
            text=True
        )
        
        metal_active = "Metal" in metal_check.stdout and ollama_running
        
        return {
            "ollama_running": ollama_running,
            "metal_acceleration": metal_active,
            "gpu_backend": "Metal" if metal_active else "CPU"
        }
    except Exception as e:
        return {"error": str(e)}

def get_system_metrics() -> SystemMetrics:
    """Get current system metrics"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    gpu_info = {**get_gpu_info_macos(), **get_ollama_gpu_usage()}
    
    return SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        memory_mb=memory.used / 1024 / 1024,
        gpu_info=gpu_info
    )

async def benchmark_scrum_agent(model_name: str = "qwen3:latest") -> List[BenchmarkResult]:
    """Benchmark a single Scrum Master agent"""
    model = OllamaModel(model_name=model_name)
    agent = Agent(
        model=model,
        name="Scrum Master",
        system_prompt="""You are a Scrum Master in a Scrum of Scrums meeting.
        Report your team's sprint status concisely using these elements:
        1. Sprint progress percentage
        2. Story points completed/total
        3. Any impediments
        4. Dependencies on other teams
        Keep responses under 50 words."""
    )
    
    test_prompts = [
        "Report Platform team sprint status",
        "What impediments does Mobile team have?",
        "Propose resolution for testing environment blocker",
        "Update on Backend team dependencies",
        "Motion to address critical production issue"
    ]
    
    results = []
    
    for prompt in test_prompts:
        # Get metrics before
        metrics_before = get_system_metrics()
        
        # Time the operation
        start = time.time()
        response = await agent.run(prompt)
        duration = (time.time() - start) * 1000  # ms
        
        # Get metrics after
        metrics_after = get_system_metrics()
        
        # Estimate tokens (rough approximation)
        response_text = response.data
        tokens = len(response_text.split()) * 1.3  # Rough token estimate
        tokens_per_second = tokens / (duration / 1000) if duration > 0 else 0
        
        result = BenchmarkResult(
            operation=prompt[:30] + "...",
            model=model_name,
            duration_ms=duration,
            tokens_generated=int(tokens),
            tokens_per_second=tokens_per_second,
            cpu_percent=metrics_after.cpu_percent,
            memory_mb=metrics_after.memory_mb,
            gpu_active=metrics_after.gpu_info.get("metal_acceleration", False),
            timestamp=datetime.now().isoformat()
        )
        results.append(result)
        
        # Small delay between requests
        await asyncio.sleep(0.1)
    
    return results

async def benchmark_full_scrum_of_scrums() -> Dict[str, Any]:
    """Benchmark a complete Scrum of Scrums with 5 teams"""
    
    print("🚀 Starting Ollama Benchmark for Scrum at Scale...")
    print("=" * 60)
    
    # Get system info
    sys_info = get_system_metrics()
    print(f"📱 System Info:")
    print(f"   CPU: {sys_info.cpu_percent}%")
    print(f"   Memory: {sys_info.memory_mb:.0f} MB ({sys_info.memory_percent}%)")
    print(f"   GPU: {sys_info.gpu_info.get('gpu_name', 'Unknown')}")
    print(f"   GPU VRAM: {sys_info.gpu_info.get('gpu_vram', 'Unknown')}")
    print(f"   Metal Support: {sys_info.gpu_info.get('metal_support', False)}")
    print(f"   Ollama GPU: {sys_info.gpu_info.get('gpu_backend', 'Unknown')}")
    print("=" * 60)
    
    # Test different models
    models_to_test = [
        "qwen3:latest",
        "devstral:latest"
    ]
    
    all_results = {}
    
    for model in models_to_test:
        print(f"\n📊 Testing model: {model}")
        try:
            # Warm up
            print("   Warming up...")
            await benchmark_scrum_agent(model)
            
            # Actual benchmark
            print("   Running benchmark...")
            results = await benchmark_scrum_agent(model)
            all_results[model] = results
            
            # Calculate statistics
            durations = [r.duration_ms for r in results]
            tokens_per_sec = [r.tokens_per_second for r in results]
            
            print(f"   ✅ Completed {len(results)} operations")
            print(f"   ⏱️  Avg response time: {statistics.mean(durations):.0f}ms")
            print(f"   📈 Avg tokens/sec: {statistics.mean(tokens_per_sec):.0f}")
            print(f"   🖥️  GPU Active: {any(r.gpu_active for r in results)}")
            
        except Exception as e:
            print(f"   ❌ Error testing {model}: {e}")
    
    # Simulate full Scrum of Scrums timing
    print("\n🏁 Full Scrum of Scrums Simulation:")
    
    total_operations = 25  # Typical number of agent interactions
    best_model = min(all_results.keys(), 
                    key=lambda m: statistics.mean([r.duration_ms for r in all_results[m]]))
    best_avg = statistics.mean([r.duration_ms for r in all_results[best_model]])
    
    estimated_time = (total_operations * best_avg) / 1000  # seconds
    
    print(f"   Best model: {best_model}")
    print(f"   Estimated meeting time: {estimated_time:.1f} seconds")
    print(f"   Operations: {total_operations}")
    
    return {
        "system_info": sys_info.dict(),
        "benchmarks": {k: [r.dict() for r in v] for k, v in all_results.items()},
        "summary": {
            "best_model": best_model,
            "avg_response_ms": best_avg,
            "estimated_meeting_seconds": estimated_time,
            "gpu_acceleration": sys_info.gpu_info.get("metal_acceleration", False)
        }
    }

def generate_benchmark_mermaid(benchmark_data: Dict[str, Any]):
    """Generate Mermaid diagrams for benchmark results"""
    
    # Performance comparison
    perf_chart = """```mermaid
graph TB
    subgraph "Ollama Model Performance Comparison"
"""
    
    for model, results in benchmark_data["benchmarks"].items():
        avg_ms = statistics.mean([r["duration_ms"] for r in results])
        avg_tps = statistics.mean([r["tokens_per_second"] for r in results])
        perf_chart += f"""
        {model.replace(":", "_").replace(".", "_")}["{model}<br/>Avg: {avg_ms:.0f}ms<br/>{avg_tps:.0f} tokens/s"]
"""
    
    perf_chart += """
    end
```"""

    # GPU utilization
    gpu_info = benchmark_data["system_info"]["gpu_info"]
    gpu_chart = f"""```mermaid
pie title "Ollama Acceleration Status"
    "GPU Accelerated ({gpu_info.get('gpu_backend', 'Unknown')})" : {"1" if gpu_info.get('metal_acceleration') else "0"}
    "CPU Only" : {"0" if gpu_info.get('metal_acceleration') else "1"}
```"""

    # Response time distribution
    all_durations = []
    for results in benchmark_data["benchmarks"].values():
        all_durations.extend([r["duration_ms"] for r in results])
    
    time_dist = f"""```mermaid
graph TD
    subgraph "Response Time Analysis"
        A[Min: {min(all_durations):.0f}ms]
        B[Avg: {statistics.mean(all_durations):.0f}ms]
        C[Max: {max(all_durations):.0f}ms]
        D[P95: {sorted(all_durations)[int(len(all_durations)*0.95)]:.0f}ms]
        
        A --> B
        B --> C
        B --> D
    end
```"""

    # System metrics
    sys_metrics = f"""```mermaid
graph LR
    subgraph "macOS System Info"
        GPU["{gpu_info.get('gpu_name', 'Unknown')}<br/>{gpu_info.get('gpu_vram', 'Unknown')} VRAM"]
        Metal["Metal Support: {'✅' if gpu_info.get('metal_support') else '❌'}"]
        Ollama["Ollama Running: {'✅' if gpu_info.get('ollama_running') else '❌'}"]
        Backend["Backend: {gpu_info.get('gpu_backend', 'CPU')}"]
        
        GPU --> Metal
        Metal --> Ollama
        Ollama --> Backend
    end
```"""

    print(perf_chart)
    print()
    print(gpu_chart)
    print()
    print(time_dist)
    print()
    print(sys_metrics)

async def main():
    """Run the complete benchmark"""
    
    # Check Ollama is running
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True)
        if result.returncode != 0:
            print("❌ Ollama not running. Please start with: ollama serve")
            return
    except FileNotFoundError:
        print("❌ Ollama not installed. Please install from ollama.ai")
        return
    
    # Run benchmarks
    benchmark_data = await benchmark_full_scrum_of_scrums()
    
    # Save results
    with open("ollama_benchmark_results.json", "w") as f:
        json.dump(benchmark_data, f, indent=2)
    
    # Generate visualizations
    print("\n📊 Benchmark Visualizations:")
    print("=" * 60)
    generate_benchmark_mermaid(benchmark_data)
    
    # Final summary
    print(f"\n✅ Benchmark complete!")
    print(f"   Results saved to: ollama_benchmark_results.json")
    print(f"   Best model: {benchmark_data['summary']['best_model']}")
    print(f"   GPU Acceleration: {'Yes' if benchmark_data['summary']['gpu_acceleration'] else 'No'}")

if __name__ == "__main__":
    asyncio.run(main())