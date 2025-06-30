#!/usr/bin/env python3
"""
REAL Working System with Pydantic AI and Ollama
Using the correct imports and generated models
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Pydantic and Pydantic AI - CORRECT IMPORTS
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Simple span tracking for demo
class SimpleSpan:
    def __init__(self, name: str):
        self.name = name
        self.attributes = {}
        self.start_time = time.time()
        
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
        
    def end(self):
        duration = time.time() - self.start_time
        print(f"\n📡 SPAN: {self.name} (took {duration:.2f}s)")
        for k, v in self.attributes.items():
            if isinstance(v, str) and len(v) > 100:
                print(f"   {k}: {v[:100]}...")
            else:
                print(f"   {k}: {v}")

# ============= Generated Pydantic Models (from semantic conventions) =============

class AgentDecision(BaseModel):
    """Decision output from any agent - GENERATED from agent.output.decision"""
    decision: str = Field(..., description="The decision made")
    reasoning: str = Field(..., description="Detailed reasoning")
    confidence: float = Field(..., ge=0.0, le=1.0)
    alternatives_considered: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)

class BacklogPrioritization(BaseModel):
    """Backlog prioritization - GENERATED from sas.ems.prioritization"""
    prioritized_ids: List[str]
    wsjf_scores: Dict[str, float]
    sprint_allocation: Dict[str, int]
    dependencies: List[Dict[str, str]]

class ImpedimentResolution(BaseModel):
    """Impediment resolution - GENERATED from sas.impediment.resolution"""
    impediment_id: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    root_causes: List[str]
    resolution_plan: str
    escalation_required: bool
    estimated_time: str

# ============= Real Agents using Pydantic AI =============

class RealScrumAgent:
    """Base agent using Pydantic AI with Ollama"""
    
    def __init__(self, agent_id: str, name: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        
        # Ollama via OpenAI-compatible API (as shown in user's example)
        self.ollama_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://192.168.1.74:11434/v1')
        )
        
        self.decisions_made = []

class CEOAgent(RealScrumAgent):
    """CEO making strategic decisions"""
    
    def __init__(self):
        super().__init__("ceo-001", "Sarah Chen", "CEO")
        
    async def make_strategic_decision(self, context: Dict[str, Any]) -> AgentDecision:
        """Make a real strategic decision"""
        
        span = SimpleSpan(f"ceo.strategic_decision")
        span.set_attribute("agent.id", self.agent_id)
        span.set_attribute("agent.name", self.name)
        
        # Create Pydantic AI agent with structured output
        decision_agent = Agent(
            self.ollama_model,
            output_type=AgentDecision,
            system_prompt="""You are the CEO of a $5B enterprise.
Make strategic decisions considering ROI, risk, and long-term impact.
Focus on digital transformation and competitive advantage."""
        )
        
        prompt = f"""Analyze this strategic opportunity:

{json.dumps(context, indent=2)}

Make a decision considering financial impact, strategic alignment, and risk."""

        print(f"\n🤔 {self.name} thinking (real Ollama call)...")
        
        # REAL LLM CALL
        result = await decision_agent.run(prompt)
        decision = result.output  # Pydantic model instance
        
        span.set_attribute("decision.made", decision.decision)
        span.set_attribute("decision.confidence", decision.confidence)
        span.set_attribute("message.content", decision.model_dump_json())
        span.end()
        
        print(f"✅ CEO Decision: {decision.decision}")
        print(f"   Confidence: {decision.confidence:.1%}")
        print(f"   Reasoning: {decision.reasoning[:150]}...")
        
        self.decisions_made.append(decision)
        return decision

class CPOAgent(RealScrumAgent):
    """Chief Product Owner prioritizing backlog"""
    
    def __init__(self):
        super().__init__("cpo-001", "David Kumar", "CPO")
        
    async def prioritize_backlog(self, items: List[Dict[str, Any]]) -> BacklogPrioritization:
        """Prioritize backlog using WSJF"""
        
        span = SimpleSpan("cpo.backlog_prioritization")
        span.set_attribute("agent.id", self.agent_id)
        span.set_attribute("items.count", len(items))
        
        # Create prioritization agent
        prioritization_agent = Agent(
            self.ollama_model,
            output_type=BacklogPrioritization,
            system_prompt="""You are the Chief Product Owner managing a $1.2B portfolio.
Use WSJF (Weighted Shortest Job First) to prioritize features.
WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size"""
        )
        
        prompt = f"""Prioritize these backlog items using WSJF:

Items: {json.dumps(items, indent=2)}

Calculate WSJF scores, identify dependencies, and allocate to sprints."""

        print(f"\n📊 {self.name} prioritizing (real Ollama call)...")
        
        result = await prioritization_agent.run(prompt)
        prioritization = result.output
        
        span.set_attribute("top_item", prioritization.prioritized_ids[0] if prioritization.prioritized_ids else "none")
        span.set_attribute("message.content", prioritization.model_dump_json())
        span.end()
        
        print(f"✅ Backlog Prioritized:")
        print(f"   Top priority: {prioritization.prioritized_ids[0] if prioritization.prioritized_ids else 'None'}")
        print(f"   WSJF scores calculated: {len(prioritization.wsjf_scores)}")
        
        return prioritization

class ScrumMasterAgent(RealScrumAgent):
    """Scrum Master resolving impediments"""
    
    def __init__(self, teams: List[str]):
        super().__init__(f"sm-{teams[0]}", f"SM for {', '.join(teams)}", "Scrum Master")
        self.teams = teams
        
    async def resolve_impediment(self, impediment: Dict[str, Any]) -> ImpedimentResolution:
        """Analyze and resolve impediment"""
        
        span = SimpleSpan("sm.impediment_resolution")
        span.set_attribute("agent.id", self.agent_id)
        span.set_attribute("impediment.id", impediment.get("id"))
        
        # Create resolution agent
        resolution_agent = Agent(
            self.ollama_model,
            output_type=ImpedimentResolution,
            system_prompt=f"""You are an experienced Scrum Master for teams: {', '.join(self.teams)}.
Use root cause analysis (5 Whys) to resolve impediments.
Focus on systemic solutions and prevention."""
        )
        
        prompt = f"""Analyze and resolve this impediment:

{json.dumps(impediment, indent=2)}

Provide root cause analysis, resolution plan, and escalation assessment."""

        print(f"\n🔧 {self.name} analyzing (real Ollama call)...")
        
        result = await resolution_agent.run(prompt)
        resolution = result.output
        
        span.set_attribute("severity", resolution.severity)
        span.set_attribute("escalation", resolution.escalation_required)
        span.set_attribute("message.content", resolution.model_dump_json())
        span.end()
        
        print(f"✅ Resolution Plan:")
        print(f"   Severity: {resolution.severity}")
        print(f"   Root causes: {len(resolution.root_causes)}")
        print(f"   Escalation: {'Yes' if resolution.escalation_required else 'No'}")
        
        return resolution

# ============= Demo Runner =============

async def demonstrate_real_sas():
    """Demonstrate real Scrum at Scale with actual LLM calls"""
    
    print("🏢 REAL Scrum at Scale with Pydantic AI + Ollama")
    print("🤖 Making actual LLM calls to http://192.168.1.74:11434")
    print("📊 Using generated Pydantic models for structured output")
    print("="*60)
    
    # Test connection
    print("\n🔌 Testing Ollama connection...")
    try:
        test_model = OpenAIModel(
            model_name='qwen3:latest',
            provider=OpenAIProvider(base_url='http://192.168.1.74:11434/v1')
        )
        test_agent = Agent(test_model, output_type=str)
        result = await test_agent.run("Say 'Connected!'")
        print(f"✅ Ollama connected: {result.output}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Create agents
    ceo = CEOAgent()
    cpo = CPOAgent()
    sm = ScrumMasterAgent(["Platform", "Mobile"])
    
    # Scenario 1: Strategic Decision
    print("\n" + "="*60)
    print("📋 SCENARIO 1: Strategic Investment Decision")
    print("="*60)
    
    investment = {
        "proposal": "AI Development Platform",
        "cost": 75000000,
        "expected_roi": "3x in 3 years",
        "strategic_fit": "Core to digital transformation"
    }
    
    ceo_decision = await ceo.make_strategic_decision(investment)
    
    # Scenario 2: Backlog Prioritization
    print("\n" + "="*60)
    print("📋 SCENARIO 2: Backlog Prioritization")
    print("="*60)
    
    backlog = [
        {"id": "F1", "title": "Real-time Analytics", "value": 85, "size": 21},
        {"id": "F2", "title": "Mobile App", "value": 70, "size": 34},
        {"id": "F3", "title": "API Gateway", "value": 60, "size": 13}
    ]
    
    cpo_prioritization = await cpo.prioritize_backlog(backlog)
    
    # Scenario 3: Impediment Resolution
    print("\n" + "="*60)
    print("📋 SCENARIO 3: Impediment Resolution")
    print("="*60)
    
    impediment = {
        "id": "IMP-001",
        "description": "CI/CD pipeline failures blocking 3 teams",
        "severity": "high",
        "duration": "2 days"
    }
    
    sm_resolution = await sm.resolve_impediment(impediment)
    
    # Summary
    print("\n" + "="*60)
    print("📊 COMMUNICATION SUMMARY")
    print("="*60)
    print(f"""
✅ Real LLM Calls Made: 3
🤖 All decisions from actual Ollama responses
📊 Structured output via Pydantic models
📡 Communication tracked via spans

Key Decisions:
1. CEO: {ceo_decision.decision} (confidence: {ceo_decision.confidence:.1%})
2. CPO: Prioritized {len(cpo_prioritization.prioritized_ids)} items
3. SM: {sm_resolution.severity} severity, escalation: {sm_resolution.escalation_required}
""")

    # Mermaid diagram
    print("\n📈 ACTUAL COMMUNICATION FLOW:")
    print("""
```mermaid
sequenceDiagram
    participant User
    participant CEO
    participant CPO
    participant SM
    participant Ollama as Ollama (qwen3)
    
    User->>CEO: Investment decision request
    CEO->>Ollama: Analyze $75M platform
    Ollama-->>CEO: AgentDecision model
    CEO->>User: Decision + reasoning
    
    User->>CPO: Prioritize backlog
    CPO->>Ollama: WSJF analysis
    Ollama-->>CPO: BacklogPrioritization model
    CPO->>User: Prioritized items
    
    User->>SM: Resolve impediment
    SM->>Ollama: Root cause analysis
    Ollama-->>SM: ImpedimentResolution model
    SM->>User: Resolution plan
    
    Note over Ollama: All real LLM calls
    Note over CEO,SM: Structured Pydantic output
```
""")

if __name__ == "__main__":
    asyncio.run(demonstrate_real_sas())