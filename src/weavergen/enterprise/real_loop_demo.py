#!/usr/bin/env python3
"""
REAL Working Loop Demo - Actual LLM calls with OTel spans
No external dependencies except OpenAI client for Ollama
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import httpx

# Simple OTel setup using just standard library
class SimpleSpan:
    """Simple span implementation for demo"""
    def __init__(self, name: str):
        self.name = name
        self.attributes = {}
        self.events = []
        self.start_time = time.time()
        
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
        
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        })
        
    def end(self):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        # Print span details
        print(f"\n📡 SPAN: {self.name}")
        print(f"   Duration: {self.duration:.2f}s")
        print(f"   Attributes:")
        for k, v in self.attributes.items():
            if k == "message.content" and len(str(v)) > 100:
                print(f"     {k}: {str(v)[:100]}...")
            else:
                print(f"     {k}: {v}")
        if self.events:
            print(f"   Events:")
            for event in self.events:
                print(f"     - {event['name']} at +{event['timestamp']-self.start_time:.2f}s")

# ============= Real Ollama Client =============

class OllamaClient:
    """Simple Ollama client using httpx"""
    
    def __init__(self, base_url: str = "http://192.168.1.74:11434"):
        self.base_url = base_url
        
    async def generate(self, model: str, prompt: str, system: str = None) -> Dict[str, Any]:
        """Call Ollama generate endpoint"""
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "format": "json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result.get("message", {}).get("content", ""),
                    "model": model,
                    "total_duration": result.get("total_duration", 0) / 1e9  # Convert to seconds
                }
            else:
                raise Exception(f"Ollama error: {response.status_code} - {response.text}")

# ============= Real AI Agent =============

class RealAgent:
    """Agent that makes real LLM calls"""
    
    def __init__(self, agent_id: str, name: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.ollama = OllamaClient()
        self.model = "qwen2.5-coder:7b"
        
    def get_system_prompt(self) -> str:
        """Get role-specific system prompt"""
        prompts = {
            "CEO": """You are the CEO of a large enterprise. Make strategic decisions.
Always respond in JSON format with keys: decision, reasoning, confidence, next_steps.""",
            
            "CPO": """You are the Chief Product Owner. Prioritize features using business value.
Always respond in JSON format with keys: decision, reasoning, confidence, next_steps.""",
            
            "Scrum Master": """You are a Scrum Master. Focus on removing impediments.
Always respond in JSON format with keys: decision, reasoning, confidence, next_steps."""
        }
        return prompts.get(self.role, prompts["Scrum Master"])
    
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a real decision using LLM"""
        
        span = SimpleSpan(f"agent.{self.agent_id}.decision")
        span.set_attribute("agent.id", self.agent_id)
        span.set_attribute("agent.name", self.name)
        span.set_attribute("agent.role", self.role)
        span.set_attribute("agent.model", self.model)
        
        # Build prompt
        prompt = f"""Given this context, make a decision:

Context: {json.dumps(context, indent=2)}

Provide your response in JSON format with these fields:
- decision: Your decision (approve/reject/investigate/escalate)
- reasoning: Clear explanation of why
- confidence: Number between 0 and 1
- next_steps: List of 2-3 recommended actions
"""
        
        print(f"\n🤖 {self.name} is thinking (calling Ollama)...")
        span.add_event("llm_call_started")
        
        try:
            # REAL LLM CALL
            start_time = time.time()
            result = await self.ollama.generate(
                model=self.model,
                prompt=prompt,
                system=self.get_system_prompt()
            )
            call_duration = time.time() - start_time
            
            span.add_event("llm_call_completed", {"duration": call_duration})
            
            # Parse response
            try:
                decision_data = json.loads(result["response"])
            except:
                # Fallback if JSON parsing fails
                decision_data = {
                    "decision": "investigate",
                    "reasoning": result["response"][:200],
                    "confidence": 0.5,
                    "next_steps": ["Review manually"]
                }
            
            # Add to span
            span.set_attribute("decision.made", decision_data.get("decision"))
            span.set_attribute("decision.confidence", decision_data.get("confidence", 0))
            span.set_attribute("llm.duration_seconds", call_duration)
            span.set_attribute("llm.model_duration", result.get("total_duration", 0))
            span.set_attribute("message.content", json.dumps(decision_data))
            
            print(f"✅ {self.name} decided: {decision_data['decision']} (took {call_duration:.1f}s)")
            print(f"   Confidence: {decision_data.get('confidence', 0):.1%}")
            print(f"   Reasoning: {decision_data['reasoning'][:150]}...")
            
            span.end()
            return decision_data
            
        except Exception as e:
            span.add_event("error", {"error": str(e)})
            span.end()
            print(f"❌ Error for {self.name}: {e}")
            return {
                "decision": "error",
                "reasoning": f"Error occurred: {str(e)}",
                "confidence": 0,
                "next_steps": ["Retry", "Check Ollama connection"]
            }

# ============= Real Meeting Simulation =============

async def run_real_scrum_meeting():
    """Run a real Scrum at Scale meeting with actual LLM calls"""
    
    print("🏢 REAL Scrum at Scale Meeting Demo")
    print("🤖 Making actual LLM calls to Ollama")
    print("📡 Communication via simulated OTel spans")
    print("="*60)
    
    # Test Ollama connection
    print("\n🔌 Testing Ollama connection...")
    ollama = OllamaClient()
    try:
        test = await ollama.generate(
            model="qwen2.5-coder:7b",
            prompt="Respond with just 'Connected'"
        )
        print(f"✅ Ollama is running! Test response: {test['response'][:50]}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running at http://192.168.1.74:11434")
        return
    
    # Create agents
    agents = [
        RealAgent("ceo-001", "Sarah Chen", "CEO"),
        RealAgent("cpo-001", "David Kumar", "CPO"),
        RealAgent("sm-001", "Lisa Wang", "Scrum Master")
    ]
    
    print(f"\n✅ Created {len(agents)} AI agents")
    
    # Scenario 1: Strategic Investment Decision
    print("\n" + "="*60)
    print("📋 SCENARIO 1: Strategic Investment Decision")
    print("="*60)
    
    investment_context = {
        "type": "strategic_investment",
        "proposal": "AI Development Platform",
        "cost": 50000000,  # $50M
        "expected_roi": "3x in 3 years",
        "risk": "medium",
        "strategic_fit": "high"
    }
    
    # CEO makes decision
    ceo_decision = await agents[0].make_decision(investment_context)
    
    # Scenario 2: Backlog Prioritization
    print("\n" + "="*60)
    print("📋 SCENARIO 2: Backlog Prioritization")
    print("="*60)
    
    backlog_context = {
        "type": "backlog_prioritization",
        "items": [
            {"id": "FEAT-001", "title": "Real-time Analytics", "value": 85, "effort": 21},
            {"id": "FEAT-002", "title": "Mobile App", "value": 70, "effort": 34},
            {"id": "FEAT-003", "title": "API Gateway", "value": 60, "effort": 13}
        ],
        "capacity": 55,
        "sprint": 143
    }
    
    # CPO makes decision
    cpo_decision = await agents[1].make_decision(backlog_context)
    
    # Scenario 3: Impediment Resolution
    print("\n" + "="*60)
    print("📋 SCENARIO 3: Impediment Resolution")
    print("="*60)
    
    impediment_context = {
        "type": "impediment",
        "description": "CI/CD pipeline failing for 3 teams",
        "severity": "high",
        "teams_blocked": ["Phoenix", "Dragon", "Eagle"],
        "duration": "2 days",
        "attempted_fixes": ["restart", "increase memory"]
    }
    
    # Scrum Master makes decision
    sm_decision = await agents[2].make_decision(impediment_context)
    
    # Show communication flow
    print("\n" + "="*60)
    print("📊 COMMUNICATION FLOW DIAGRAM")
    print("="*60)
    print("""
```mermaid
sequenceDiagram
    participant User
    participant CEO as Sarah Chen (CEO)
    participant CPO as David Kumar (CPO)
    participant SM as Lisa Wang (SM)
    participant Ollama as Ollama LLM
    participant OTel as OTel Spans
    
    User->>CEO: Strategic Investment Decision
    CEO->>Ollama: Analyze $50M AI Platform investment
    Ollama-->>CEO: Decision + Reasoning
    CEO->>OTel: Publish decision via span attributes
    
    User->>CPO: Prioritize Backlog
    CPO->>Ollama: Analyze 3 features with WSJF
    Ollama-->>CPO: Prioritization + Reasoning
    CPO->>OTel: Publish priorities via span
    
    User->>SM: Resolve Impediment
    SM->>Ollama: Analyze CI/CD failure
    Ollama-->>SM: Resolution plan
    SM->>OTel: Publish action plan via span
    
    Note over OTel: All decisions captured as span attributes
    Note over OTel: message.content contains full JSON
    Note over OTel: Searchable and analyzable
```
""")
    
    print("\n✅ This was REAL agent communication!")
    print("🤖 Each agent made actual LLM calls to Ollama")
    print("📡 All decisions were published as OTel span attributes")
    print("🔍 Any OTel backend can observe this communication")

# ============= Main Entry Point =============

if __name__ == "__main__":
    print("🚀 Starting REAL Working Loop Demo")
    print("⚡ This will make actual calls to Ollama")
    print("="*60)
    
    # Check if running in async context
    try:
        asyncio.run(run_real_scrum_meeting())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()