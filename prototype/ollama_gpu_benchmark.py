#!/usr/bin/env python3
"""
Simple Ollama GPU benchmark for macOS M3 Max
Tests Scrum agent responses and monitors GPU usage
"""

import subprocess
import time
import json
import psutil
import requests
from datetime import datetime
from typing import Dict, List, Any

def get_gpu_info_macos() -> Dict[str, Any]:
    """Get GPU information on macOS M3 Max"""
    try:
        # Get GPU info
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType", "-json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            displays = data.get("SPDisplaysDataType", [])
            
            for display in displays:
                if "sppci_model" in display:
                    return {
                        "gpu_found": True,
                        "gpu_name": display.get("sppci_model", "Unknown"),
                        "metal_support": "Metal" in display.get("sppci_metal", "")
                    }
        
        # Check for Apple Silicon
        cpu_result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True
        )
        
        if "Apple" in cpu_result.stdout:
            return {
                "gpu_found": True,
                "gpu_name": cpu_result.stdout.strip(),
                "metal_support": True,
                "gpu_type": "Apple Silicon Integrated GPU"
            }
            
    except Exception as e:
        return {"error": str(e)}
    
    return {"gpu_found": False}

def check_metal_usage():
    """Check if Metal is being used by Ollama"""
    try:
        # Check Activity Monitor for GPU usage
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        ollama_processes = [line for line in result.stdout.split('\n') if 'ollama' in line.lower()]
        
        # Check if Ollama is using GPU
        gpu_check = subprocess.run(
            ["ioreg", "-l", "-w", "0"],
            capture_output=True,
            text=True
        )
        
        metal_active = "IOAccelerator" in gpu_check.stdout and len(ollama_processes) > 0
        
        return {
            "ollama_running": len(ollama_processes) > 0,
            "metal_active": metal_active,
            "process_count": len(ollama_processes)
        }
    except Exception as e:
        return {"error": str(e)}

def benchmark_ollama_scrum(model: str = "qwen3:latest"):
    """Benchmark Ollama responses for Scrum scenarios"""
    
    scrum_prompts = [
        {
            "role": "Platform Scrum Master",
            "prompt": "Report sprint status: 46% complete, 32/70 points, authentication service blocker"
        },
        {
            "role": "Mobile Scrum Master", 
            "prompt": "Report sprint status: 71% complete, 55/78 points, performance testing unavailable"
        },
        {
            "role": "Web Scrum Master",
            "prompt": "Report sprint status: 88% complete, 59/67 points, awaiting security review"
        },
        {
            "role": "Backend Scrum Master",
            "prompt": "Report sprint status: 35% complete, 23/66 points, unclear requirements"
        },
        {
            "role": "Data Scrum Master",
            "prompt": "Report sprint status: 64% complete, 27/42 points, no blockers"
        }
    ]
    
    results = []
    
    print(f"🚀 Benchmarking Ollama {model} on macOS...")
    
    # Get system info
    gpu_info = get_gpu_info_macos()
    metal_info = check_metal_usage()
    
    print(f"🖥️  GPU: {gpu_info.get('gpu_name', 'Unknown')}")
    print(f"⚡ Metal Support: {gpu_info.get('metal_support', False)}")
    print(f"🔥 Metal Active: {metal_info.get('metal_active', False)}")
    print(f"📊 Starting benchmark...\n")
    
    for i, scenario in enumerate(scrum_prompts):
        print(f"Testing {scenario['role']}...")
        
        # Get system metrics before
        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().used / 1024 / 1024 / 1024  # GB
        
        # Time the request
        start = time.time()
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": f"You are a {scenario['role']} in a Scrum of Scrums. {scenario['prompt']}. Keep response under 50 words.",
                "stream": False
            }
        )
        
        duration = (time.time() - start) * 1000  # ms
        
        # Get system metrics after
        cpu_after = psutil.cpu_percent(interval=0.1)
        mem_after = psutil.virtual_memory().used / 1024 / 1024 / 1024  # GB
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            tokens = len(response_text.split()) * 1.3  # Rough estimate
            
            result = {
                "role": scenario['role'],
                "duration_ms": duration,
                "tokens": int(tokens),
                "tokens_per_sec": tokens / (duration / 1000),
                "cpu_delta": cpu_after - cpu_before,
                "memory_delta_gb": mem_after - mem_before,
                "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
            }
            results.append(result)
            
            print(f"  ✅ {duration:.0f}ms, {result['tokens_per_sec']:.0f} tokens/s")
        else:
            print(f"  ❌ Error: {response.status_code}")
    
    return {
        "model": model,
        "gpu_info": gpu_info,
        "metal_info": metal_info,
        "benchmarks": results,
        "timestamp": datetime.now().isoformat()
    }

def generate_mermaid_results(benchmark_data: Dict[str, Any]):
    """Generate Mermaid diagrams for benchmark results"""
    
    results = benchmark_data["benchmarks"]
    
    # Performance by team
    perf_chart = """```mermaid
graph TB
    subgraph "Ollama Response Times by Team"
"""
    
    for i, r in enumerate(results):
        color = "#90EE90" if r["duration_ms"] < 500 else "#FFB6C1" if r["duration_ms"] < 1000 else "#FF6B6B"
        perf_chart += f"""
        T{i}["{r['role']}<br/>{r['duration_ms']:.0f}ms<br/>{r['tokens_per_sec']:.0f} tok/s"]
        style T{i} fill:{color}
"""
    
    perf_chart += """
    end
```"""

    # GPU Status
    gpu_info = benchmark_data["gpu_info"]
    metal_info = benchmark_data["metal_info"]
    
    gpu_status = f"""```mermaid
pie title "macOS GPU Acceleration Status"
    "M3 Max GPU Active" : {"1" if metal_info.get('metal_active') else "0"}
    "CPU Only" : {"0" if metal_info.get('metal_active') else "1"}
```

```mermaid
graph LR
    subgraph "Apple Silicon GPU Info"
        A["{gpu_info.get('gpu_name', 'Unknown')}"]
        B["Metal Support: {'✅' if gpu_info.get('metal_support') else '❌'}"]
        C["Ollama Running: {'✅' if metal_info.get('ollama_running') else '❌'}"]
        D["GPU Acceleration: {'Active' if metal_info.get('metal_active') else 'Inactive'}"]
        
        A --> B
        B --> C
        C --> D
    end
```"""

    # Performance summary
    avg_duration = sum(r["duration_ms"] for r in results) / len(results)
    total_tokens = sum(r["tokens"] for r in results)
    avg_tps = sum(r["tokens_per_sec"] for r in results) / len(results)
    
    summary = f"""```mermaid
graph TD
    subgraph "Benchmark Summary"
        A["Model: {benchmark_data['model']}"]
        B["Avg Response: {avg_duration:.0f}ms"]
        C["Avg Speed: {avg_tps:.0f} tokens/sec"]
        D["Total Tokens: {total_tokens}"]
        E["Full Meeting Est: {len(results) * avg_duration / 1000:.1f}s"]
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
    
    style A fill:#4CAF50
    style E fill:#2196F3
```"""

    print(perf_chart)
    print()
    print(gpu_status)
    print()
    print(summary)

def main():
    """Run the benchmark"""
    
    # Check Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print("❌ Ollama not responding. Please start with: ollama serve")
            return
    except:
        print("❌ Cannot connect to Ollama. Please start with: ollama serve")
        return
    
    # Run benchmark
    print("=" * 60)
    benchmark_data = benchmark_ollama_scrum("qwen3:latest")
    
    # Save results
    with open("ollama_gpu_benchmark.json", "w") as f:
        json.dump(benchmark_data, f, indent=2)
    
    # Generate visualizations
    print("\n📊 Benchmark Results:")
    print("=" * 60)
    generate_mermaid_results(benchmark_data)
    
    print("\n✅ Benchmark complete! Results saved to ollama_gpu_benchmark.json")

if __name__ == "__main__":
    main()