"""
BPMN-First WeaverGen Architecture

Key principles:
1. BPMN processes control all flow and decisions
2. Agents are stateless executors of individual tasks
3. No agent-to-agent communication
4. All coordination happens through BPMN
"""

from .agent import BPMNAgent, BPMNProcessEngine, BPMNContext

__all__ = ["BPMNAgent", "BPMNProcessEngine", "BPMNContext"]