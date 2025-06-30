#!/usr/bin/env python3
"""
Accurate Ollama Metal GPU benchmark for M3 Max
Shows actual GPU acceleration metrics
"""

import subprocess
import time
import json
import requests
from datetime import datetime
from typing import Dict, List

def get_ollama_gpu_layers():
    """Extract GPU layers from running Ollama process"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.split('\n'):
            if 'ollama runner' in line and '--n-gpu-layers' in line:
                # Extract GPU layers
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == '--n-gpu-layers':
                        return int(parts[i+1])
        return 0
    except:
        return 0

def benchmark_scrum_with_metal():
    """Benchmark Scrum responses with Metal GPU tracking"""
    
    # Get GPU layers
    gpu_layers = get_ollama_gpu_layers()
    
    print(f"🚀 Ollama Metal GPU Benchmark on M3 Max")
    print("=" * 60)
    print(f"🔥 GPU Layers Active: {gpu_layers}")
    print(f"⚡ Metal Acceleration: {'YES' if gpu_layers > 0 else 'NO'}")
    print("=" * 60)
    
    # Full Scrum of Scrums conversation
    conversations = [
        # Meeting Start
        {
            "agent": "Chief Scrum Master",
            "messages": [
                {"role": "system", "content": "You are the Chief Scrum Master facilitating a Scrum of Scrums meeting."},
                {"role": "user", "content": "Start the Scrum of Scrums meeting and verify quorum."}
            ]
        },
        # Team Reports
        {
            "agent": "Platform Team",
            "messages": [
                {"role": "system", "content": "You are the Platform team Scrum Master reporting sprint status."},
                {"role": "user", "content": "Report: 46% complete, 32/70 points, authentication service blocker"}
            ]
        },
        {
            "agent": "Mobile Team",
            "messages": [
                {"role": "system", "content": "You are the Mobile team Scrum Master."},
                {"role": "user", "content": "Report: 71% complete, 55/78 points, performance testing environment unavailable"}
            ]
        },
        {
            "agent": "Web Team",
            "messages": [
                {"role": "system", "content": "You are the Web team Scrum Master."},
                {"role": "user", "content": "Report: 88% complete, 59/67 points, waiting on security review"}
            ]
        },
        {
            "agent": "Backend Team",
            "messages": [
                {"role": "system", "content": "You are the Backend team Scrum Master."},
                {"role": "user", "content": "Report: 35% complete, 23/66 points, unclear requirements from Product"}
            ]
        },
        {
            "agent": "Data Team",
            "messages": [
                {"role": "system", "content": "You are the Data team Scrum Master."},
                {"role": "user", "content": "Report: 64% complete, 27/42 points, on track"}
            ]
        },
        # Impediment Resolution
        {
            "agent": "Chief Scrum Master",
            "messages": [
                {"role": "system", "content": "You are the Chief Scrum Master."},
                {"role": "user", "content": "Mobile team raised a critical impediment about performance testing. How should we resolve it?"}
            ]
        },
        # Cross-team Dependencies
        {
            "agent": "Mobile Team",
            "messages": [
                {"role": "system", "content": "You are the Mobile team Scrum Master."},
                {"role": "user", "content": "We need the authentication service endpoints from Platform team by July 3rd."}
            ]
        },
        {
            "agent": "Platform Team",
            "messages": [
                {"role": "system", "content": "You are the Platform team Scrum Master."},
                {"role": "user", "content": "Confirm: We can deliver authentication endpoints by July 3rd."}
            ]
        },
        # Meeting Close
        {
            "agent": "Chief Scrum Master",
            "messages": [
                {"role": "system", "content": "You are the Chief Scrum Master."},
                {"role": "user", "content": "Summarize action items and adjourn the meeting."}
            ]
        }
    ]
    
    results = []
    total_start = time.time()
    
    print("\n📊 Running Scrum of Scrums...\n")
    
    for conv in conversations:
        print(f"🎤 {conv['agent']}...")
        
        start = time.time()
        
        # Call Ollama chat API
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:latest",
                "messages": conv["messages"],
                "stream": False
            }
        )
        
        duration = (time.time() - start) * 1000  # ms
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {}).get("content", "")
            eval_count = data.get("eval_count", 0)
            eval_duration = data.get("eval_duration", 0) / 1_000_000  # to ms
            
            # Calculate tokens per second
            tokens_per_sec = (eval_count / eval_duration * 1000) if eval_duration > 0 else 0
            
            result = {
                "agent": conv["agent"],
                "duration_ms": duration,
                "eval_count": eval_count,
                "eval_duration_ms": eval_duration,
                "tokens_per_sec": tokens_per_sec,
                "gpu_layers": gpu_layers,
                "response_preview": message[:100] + "..." if len(message) > 100 else message
            }
            results.append(result)
            
            print(f"   ✅ {duration:.0f}ms total, {eval_count} tokens @ {tokens_per_sec:.0f} tok/s")
            print(f"   📝 \"{result['response_preview']}\"")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        print()
    
    total_duration = time.time() - total_start
    
    return {
        "model": "qwen3:latest",
        "gpu_layers": gpu_layers,
        "metal_enabled": gpu_layers > 0,
        "total_duration_seconds": total_duration,
        "conversations": results,
        "timestamp": datetime.now().isoformat()
    }

def generate_mermaid_analysis(data: Dict):
    """Generate comprehensive Mermaid diagrams"""
    
    # Meeting Flow with Timings
    meeting_flow = """```mermaid
sequenceDiagram
    participant CSM as Chief Scrum Master
    participant Platform as Platform Team
    participant Mobile as Mobile Team
    participant Web as Web Team
    participant Backend as Backend Team
    participant Data as Data Team
    
    Note over All: Scrum of Scrums - Metal GPU Accelerated
"""
    
    for conv in data["conversations"]:
        agent = conv["agent"]
        duration = conv["duration_ms"]
        tokens = conv["eval_count"]
        tps = conv["tokens_per_sec"]
        
        if agent == "Chief Scrum Master":
            meeting_flow += f"\n    CSM->>All: {duration:.0f}ms, {tokens} tokens @ {tps:.0f} tok/s"
        else:
            team = agent.split()[0]
            meeting_flow += f"\n    {team}->>CSM: {duration:.0f}ms, {tokens} tokens @ {tps:.0f} tok/s"
    
    meeting_flow += "\n```"
    
    # GPU Performance Analysis
    gpu_analysis = f"""```mermaid
pie title "M3 Max GPU Acceleration Impact"
    "GPU Layers Active" : {data['gpu_layers']}
    "CPU Layers" : {37 - data['gpu_layers']}
```

```mermaid
graph TD
    subgraph "Metal GPU Performance Metrics"
        A["GPU Layers: {data['gpu_layers']}/37"]
        B["Metal Enabled: {'✅' if data['metal_enabled'] else '❌'}"]
        C["Total Meeting Time: {data['total_duration_seconds']:.1f}s"]
        D["Avg Response: {sum(c['duration_ms'] for c in data['conversations'])/len(data['conversations']):.0f}ms"]
        E["Avg Speed: {sum(c['tokens_per_sec'] for c in data['conversations'])/len(data['conversations']):.0f} tok/s"]
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
    
    style A fill:#4CAF50
    style B fill:#4CAF50
```"""

    # Token Generation Performance
    token_perf = """```mermaid
graph TB
    subgraph "Token Generation Performance by Agent"
"""
    
    for i, conv in enumerate(data["conversations"]):
        color = "#90EE90" if conv["tokens_per_sec"] > 100 else "#FFB6C1" if conv["tokens_per_sec"] > 50 else "#FF6B6B"
        token_perf += f"""
        A{i}["{conv['agent']}<br/>{conv['eval_count']} tokens<br/>{conv['tokens_per_sec']:.0f} tok/s"]
        style A{i} fill:{color}
"""
    
    token_perf += """
    end
```"""

    # Response Time Comparison
    response_times = f"""```mermaid
gantt
    title Response Times (ms) - Scrum of Scrums
    dateFormat X
    axisFormat %L
    
    section Meeting
"""
    
    start = 0
    for conv in data["conversations"]:
        response_times += f"    {conv['agent']:<20} :active, {start}, {conv['duration_ms']:.0f}\n"
        start += conv['duration_ms']
    
    response_times += "```"
    
    print(meeting_flow)
    print()
    print(gpu_analysis)
    print()
    print(token_perf)
    print()
    print(response_times)

def main():
    """Run Metal GPU benchmark"""
    
    # Check system
    print("🖥️  System Check...")
    sysinfo = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True)
    print(f"   CPU: {sysinfo.stdout.strip()}")
    
    # Run benchmark
    benchmark_data = benchmark_scrum_with_metal()
    
    # Save results
    with open("ollama_metal_benchmark.json", "w") as f:
        json.dump(benchmark_data, f, indent=2)
    
    # Generate analysis
    print("\n📊 Metal GPU Performance Analysis:")
    print("=" * 60)
    generate_mermaid_analysis(benchmark_data)
    
    print(f"\n✅ Benchmark complete!")
    print(f"   Total time: {benchmark_data['total_duration_seconds']:.1f}s")
    print(f"   GPU Acceleration: {'ACTIVE' if benchmark_data['metal_enabled'] else 'INACTIVE'}")
    print(f"   Results saved: ollama_metal_benchmark.json")

if __name__ == "__main__":
    main()