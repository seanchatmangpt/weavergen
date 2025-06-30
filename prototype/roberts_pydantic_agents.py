#!/usr/bin/env python3
"""
Pydantic-AI agents that use the integrated Roberts Rules system.
This properly combines the generated code, Pydantic models, and agent intelligence.
"""

import sys
import os
import asyncio
from typing import List, Optional, Dict, Any, Literal
from dataclasses import dataclass

# Setup paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'output'))

# First, install our integrated operations
from roberts_integrated_operations import install_integrated_operations, get_pydantic_state
install_integrated_operations()

# Now import everything we need
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.ollama import OllamaModel

# Import Pydantic models
from roberts_rules_models import (
    Meeting, Motion, Vote, PointOfOrder, RecognitionRequest,
    ParliamentaryState, MeetingType, MotionType, MotionStatus,
    VoteThreshold, VoteMethod, VoteResult, RecognitionPurpose
)

# Import generated functions (now with integrated operations)
from output.roberts.commands.forge import (
    roberts_meeting_start,
    roberts_motion_make,
    roberts_motion_second,
    roberts_vote_record,
    roberts_point_of_order_raise,
    roberts_recognition_request,
    ForgeResult
)

# Configure model
model = OllamaModel(
    model_name='llama3.2',
    base_url='http://localhost:11434',
)

# Dependencies
@dataclass
class RobertsRulesDeps:
    """Dependencies for Roberts Rules agents"""
    member_name: str
    role: Literal["chair", "secretary", "member", "parliamentarian"]
    
    @property
    def state(self) -> ParliamentaryState:
        """Get the current parliamentary state"""
        return get_pydantic_state()

# Tools that properly use the generated functions

@Tool
async def start_meeting_tool(
    ctx: RunContext[RobertsRulesDeps],
    meeting_type: str,
    expected_attendance: int
) -> Dict[str, Any]:
    """Start a meeting (chair only)"""
    if ctx.deps.role != "chair":
        raise ValueError("Only the chair can start a meeting")
    
    # Use the generated function with proper parameters
    result = roberts_meeting_start(
        roberts_meeting_id=f"meeting-{ctx.deps.member_name}-{asyncio.get_event_loop().time()}",
        roberts_meeting_type=meeting_type,
        roberts_meeting_quorum=expected_attendance // 2 + 1,
        roberts_meeting_members_present=expected_attendance,
        roberts_meeting_chair=ctx.deps.member_name,
        roberts_meeting_secretary="Secretary Smith"
    )
    
    if result.success:
        return result.data
    else:
        raise ValueError(f"Failed to start meeting: {result.errors}")

@Tool
async def make_motion_tool(
    ctx: RunContext[RobertsRulesDeps],
    motion_type: str,
    motion_text: str
) -> Dict[str, Any]:
    """Make a motion"""
    if ctx.deps.role == "chair" and motion_type != "incidental":
        raise ValueError("Chair cannot make motions except incidental")
    
    # Use the generated function
    result = roberts_motion_make(
        roberts_motion_id=f"motion-{asyncio.get_event_loop().time()}",
        roberts_motion_type=motion_type,
        roberts_motion_text=motion_text,
        roberts_motion_mover=ctx.deps.member_name,
        roberts_motion_requires_second=True,
        roberts_motion_debatable=motion_type == "main",
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    
    if result.success:
        return result.data
    else:
        raise ValueError(f"Failed to make motion: {result.errors}")

@Tool
async def second_motion_tool(
    ctx: RunContext[RobertsRulesDeps],
    motion_id: str
) -> Dict[str, Any]:
    """Second a motion"""
    if ctx.deps.role == "chair":
        raise ValueError("Chair cannot second motions")
    
    # Get motion from state
    motion = ctx.deps.state.motions.get(motion_id)
    if not motion:
        raise ValueError("Motion not found")
    
    # Use the generated function
    result = roberts_motion_second(
        roberts_motion_id=motion_id,
        roberts_motion_type=motion.type.value,
        roberts_motion_text=motion.text,
        roberts_motion_mover=motion.mover,
        roberts_motion_seconder=ctx.deps.member_name,
        roberts_motion_requires_second=motion.requires_second,
        roberts_motion_debatable=motion.debatable,
        roberts_motion_vote_required=motion.vote_required.value,
        roberts_motion_status=motion.status.value
    )
    
    if result.success:
        return result.data
    else:
        raise ValueError(f"Failed to second motion: {result.errors}")

@Tool
async def call_vote_tool(
    ctx: RunContext[RobertsRulesDeps],
    motion_id: str,
    yes_votes: int,
    no_votes: int,
    abstentions: int = 0
) -> Dict[str, Any]:
    """Call and record a vote (chair/secretary)"""
    if ctx.deps.role not in ["chair", "secretary"]:
        raise ValueError("Only chair or secretary can record votes")
    
    # Use the generated function
    result = roberts_vote_record(
        roberts_vote_motion_id=motion_id,
        roberts_vote_method="voice",
        roberts_vote_yes_count=yes_votes,
        roberts_vote_no_count=no_votes,
        roberts_vote_abstain_count=abstentions,
        roberts_vote_result="pending"  # Will be calculated
    )
    
    if result.success:
        return result.data
    else:
        raise ValueError(f"Failed to record vote: {result.errors}")

@Tool
async def get_state_tool(ctx: RunContext[RobertsRulesDeps]) -> Dict[str, Any]:
    """Get current parliamentary state"""
    state = ctx.deps.state
    
    return {
        "has_meeting": state.current_meeting is not None,
        "meeting_id": state.current_meeting.id if state.current_meeting else None,
        "has_quorum": state.current_meeting.has_quorum if state.current_meeting else False,
        "active_motions": [
            {
                "id": m.id,
                "type": m.type.value,
                "text": m.text,
                "status": m.status.value,
                "precedence": m.get_precedence_level()
            }
            for m in state.get_active_motions()
        ],
        "motion_hierarchy": [m.id for m in state.get_motion_hierarchy()],
        "total_motions": len(state.motions),
        "total_votes": len(state.votes)
    }

@Tool
async def analyze_precedence_tool(
    ctx: RunContext[RobertsRulesDeps],
    new_motion_type: str
) -> Dict[str, Any]:
    """Analyze if a motion type can be made given current state"""
    try:
        motion_type = MotionType(new_motion_type)
        can_make = ctx.deps.state.can_make_motion(motion_type)
        
        hierarchy = ctx.deps.state.get_motion_hierarchy()
        
        return {
            "can_make_motion": can_make,
            "motion_type": new_motion_type,
            "precedence_level": Motion(
                id="temp", type=motion_type, text="", mover="",
                requires_second=True, debatable=True,
                vote_required=VoteThreshold.MAJORITY
            ).get_precedence_level(),
            "current_hierarchy": [
                {
                    "type": m.type.value,
                    "precedence": m.get_precedence_level()
                }
                for m in hierarchy
            ],
            "reason": "Motion allowed" if can_make else "Higher precedence motion is pending"
        }
    except ValueError:
        return {
            "can_make_motion": False,
            "error": f"Invalid motion type: {new_motion_type}"
        }

# Create specialized agents
chair_agent = Agent(
    model=model,
    deps_type=RobertsRulesDeps,
    system_prompt="""You are the Chair of a meeting following Robert's Rules of Order.
    Your responsibilities:
    - Start meetings and ensure quorum
    - Maintain order and proper procedure
    - Call for votes on motions
    - You cannot make motions (except incidental) or second them
    
    Use the tools to interact with the parliamentary system.""",
    tools=[start_meeting_tool, call_vote_tool, get_state_tool, analyze_precedence_tool]
)

member_agent = Agent(
    model=model,
    deps_type=RobertsRulesDeps,
    system_prompt="""You are a member in a meeting following Robert's Rules of Order.
    You can:
    - Make motions (respecting precedence rules)
    - Second motions made by others
    - Participate in debate and voting
    
    Use the tools to interact with the parliamentary system.""",
    tools=[make_motion_tool, second_motion_tool, get_state_tool, analyze_precedence_tool]
)

parliamentarian_agent = Agent(
    model=model,
    deps_type=RobertsRulesDeps,
    system_prompt="""You are a Parliamentarian advising on Robert's Rules of Order.
    Your role is to:
    - Analyze motion precedence
    - Advise on proper procedure
    - Identify any violations of the rules
    
    Use the tools to analyze the parliamentary state.""",
    tools=[get_state_tool, analyze_precedence_tool]
)

# Demo functions
async def demo_meeting_with_pydantic():
    """Demonstrate a meeting using Pydantic models and generated code"""
    print("🏛️  Roberts Rules with Pydantic Models Demo")
    print("=" * 50)
    
    # Create dependencies
    chair_deps = RobertsRulesDeps("Chair Johnson", "chair")
    member1_deps = RobertsRulesDeps("Alice Smith", "member")
    member2_deps = RobertsRulesDeps("Bob Wilson", "member")
    parl_deps = RobertsRulesDeps("Dr. Parliamentary", "parliamentarian")
    
    # 1. Start meeting
    print("\n1. STARTING MEETING")
    result = await chair_agent.run(
        "Start a board meeting with 7 attendees",
        deps=chair_deps
    )
    print(f"Chair: {result.data}")
    
    # 2. Check state
    print("\n2. CHECKING STATE")
    state = await get_state_tool.fn(RunContext(deps=member1_deps))
    print(f"Current state: Meeting active: {state['has_meeting']}, Quorum: {state['has_quorum']}")
    
    # 3. Make motion
    print("\n3. MAKING MAIN MOTION")
    motion_result = await member_agent.run(
        "Make a main motion to approve the annual budget of $100,000",
        deps=member1_deps
    )
    print(f"Alice: {motion_result.data}")
    
    # 4. Check precedence before another motion
    print("\n4. CHECKING PRECEDENCE")
    precedence = await analyze_precedence_tool.fn(
        RunContext(deps=parl_deps),
        "subsidiary"
    )
    print(f"Parliamentarian: Can make subsidiary motion? {precedence['can_make_motion']}")
    print(f"   Reason: {precedence['reason']}")
    
    # 5. Second the motion
    print("\n5. SECONDING MOTION")
    state = await get_state_tool.fn(RunContext(deps=member2_deps))
    if state['active_motions']:
        motion_id = state['active_motions'][0]['id']
        second_result = await member_agent.run(
            f"Second motion {motion_id}",
            deps=member2_deps
        )
        print(f"Bob: {second_result.data}")
    
    # 6. Vote
    print("\n6. CALLING FOR VOTE")
    vote_result = await chair_agent.run(
        f"Call a vote on motion {motion_id} with 5 yes, 2 no",
        deps=chair_deps
    )
    print(f"Chair: {vote_result.data}")
    
    # 7. Final state with Pydantic models
    print("\n7. FINAL STATE (PYDANTIC MODELS)")
    pydantic_state = get_pydantic_state()
    print(f"   Total meetings: {len(pydantic_state.meetings)}")
    print(f"   Total motions: {len(pydantic_state.motions)}")
    print(f"   Total votes: {len(pydantic_state.votes)}")
    
    # Show a motion's Pydantic model
    if pydantic_state.motions:
        motion = list(pydantic_state.motions.values())[0]
        print(f"\n   Motion Model Example:")
        print(f"   - ID: {motion.id}")
        print(f"   - Type: {motion.type.value}")
        print(f"   - Status: {motion.status.value}")
        print(f"   - Precedence Level: {motion.get_precedence_level()}")
        print(f"   - Can be debated: {motion.can_be_debated}")

async def demo_complex_precedence():
    """Demonstrate complex motion precedence with Pydantic validation"""
    print("\n\n🎯 Complex Precedence Demo")
    print("=" * 50)
    
    member_deps = RobertsRulesDeps("Test Member", "member")
    
    # Make a series of motions to test precedence
    motion_sequence = [
        ("main", "Approve new policy"),
        ("main", "Approve different policy"),  # Should fail
        ("subsidiary", "Amend the policy"),    # Should succeed
        ("privileged", "Take a recess"),       # Should succeed
        ("incidental", "Point of information") # Should succeed
    ]
    
    for motion_type, text in motion_sequence:
        print(f"\n📋 Attempting {motion_type} motion: {text}")
        
        # Check precedence first
        precedence = await analyze_precedence_tool.fn(
            RunContext(deps=member_deps),
            motion_type
        )
        print(f"   Can make: {precedence['can_make_motion']}")
        
        if precedence['can_make_motion']:
            try:
                result = await make_motion_tool.fn(
                    RunContext(deps=member_deps),
                    motion_type,
                    text
                )
                print(f"   ✅ Motion created: {result['motion_id']}")
                print(f"      Precedence level: {result['precedence_level']}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        else:
            print(f"   ❌ Blocked by precedence: {precedence['reason']}")

if __name__ == "__main__":
    print("🤖 Roberts Rules + Pydantic Models + Generated Code")
    print("This demonstrates the complete integration of:")
    print("- Semantic conventions → Generated telemetry code")
    print("- Pydantic models → Type safety and validation")
    print("- Agent intelligence → Proper parliamentary procedure")
    
    # Run demos
    asyncio.run(demo_meeting_with_pydantic())
    asyncio.run(demo_complex_precedence())
    
    print("\n\n✨ Integration Complete!")
    print("The system now properly uses:")
    print("- Generated functions for telemetry")
    print("- Pydantic models for type safety")
    print("- Agent tools that bridge both systems")