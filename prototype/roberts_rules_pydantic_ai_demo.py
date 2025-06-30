#!/usr/bin/env python3
"""
Roberts Rules of Order implementation using pydantic-ai agents with Ollama.
This demonstrates the complete integration of semantic code generation,
Pydantic models, and intelligent agents following the pydantic-ai patterns.
"""

import sys
import os
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

# Setup paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'output'))

# First, install our integrated operations
from roberts_integrated_operations import install_integrated_operations, get_pydantic_state
install_integrated_operations()

# Import pydantic-ai components
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Import our Pydantic models
from roberts_rules_models import (
    Meeting, Motion, Vote, PointOfOrder, RecognitionRequest,
    ParliamentaryState, MeetingType, MotionType, MotionStatus,
    VoteThreshold, VoteMethod, VoteResult, RecognitionPurpose,
    MeetingStartRequest, MotionMakeRequest, VoteRecordRequest
)

# Import generated functions
from output.roberts.commands.forge import (
    roberts_meeting_start,
    roberts_motion_make,
    roberts_motion_second,
    roberts_vote_record,
    roberts_point_of_order_raise,
    roberts_recognition_request,
    ForgeResult
)

# Configure Ollama model
ollama_model = OpenAIModel(
    model_name='llama3.2',  # or llama3.2:3b for smaller model
    provider=OpenAIProvider(base_url='http://localhost:11434/v1')
)

# Response models for structured output
class MeetingStartResponse(BaseModel):
    """Response from starting a meeting"""
    meeting_id: str
    status: str
    message: str

class MotionResponse(BaseModel):
    """Response from motion operations"""
    motion_id: str
    action: str
    success: bool
    details: str

class VoteResponse(BaseModel):
    """Response from voting"""
    motion_id: str
    result: str
    vote_counts: Dict[str, int]
    message: str

# Dependencies for agents
@dataclass
class RobertsRulesDeps:
    """Dependencies for Roberts Rules agents"""
    member_name: str
    role: str  # chair, secretary, member, parliamentarian
    
    @property
    def state(self) -> ParliamentaryState:
        """Get the current parliamentary state"""
        return get_pydantic_state()

# Chair Agent
chair_agent = Agent(
    ollama_model,
    deps_type=RobertsRulesDeps,
    output_type=MeetingStartResponse,
    system_prompt="""You are the Chair of a meeting following Robert's Rules of Order.
    Your responsibilities:
    - Start meetings and ensure quorum
    - Maintain order and proper procedure
    - Call for votes on motions
    - Rule on points of order
    - Recognize members who wish to speak
    
    You cannot make motions (except incidental) or second them.
    Always be impartial and follow proper parliamentary procedure.""",
)

@chair_agent.tool
async def start_meeting(
    ctx: RunContext[RobertsRulesDeps],
    meeting_type: str,
    expected_attendance: int
) -> Dict[str, Any]:
    """Start a new meeting with the specified type and expected attendance"""
    if ctx.deps.role != "chair":
        raise ValueError("Only the chair can start a meeting")
    
    meeting_id = f"meeting-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Use the generated function with proper telemetry
    result = roberts_meeting_start(
        roberts_meeting_id=meeting_id,
        roberts_meeting_type=meeting_type,
        roberts_meeting_quorum=expected_attendance // 2 + 1,
        roberts_meeting_members_present=expected_attendance,
        roberts_meeting_chair=ctx.deps.member_name,
        roberts_meeting_secretary="Secretary Johnson"
    )
    
    if result.success:
        return {
            "meeting_id": meeting_id,
            "type": meeting_type,
            "quorum": expected_attendance // 2 + 1,
            "attendance": expected_attendance,
            "data": result.data
        }
    else:
        raise ValueError(f"Failed to start meeting: {result.errors}")

@chair_agent.tool
async def call_for_vote(
    ctx: RunContext[RobertsRulesDeps],
    motion_id: str
) -> str:
    """Call for a vote on a motion"""
    motion = ctx.deps.state.motions.get(motion_id)
    if not motion:
        return f"Motion {motion_id} not found"
    
    if motion.status != MotionStatus.SECONDED:
        return f"Motion must be seconded before voting (current status: {motion.status.value})"
    
    return f"The question is on the motion: '{motion.text}'. All in favor say 'aye'."

# Member Agent
member_agent = Agent(
    ollama_model,
    deps_type=RobertsRulesDeps,
    output_type=MotionResponse,
    system_prompt="""You are a member in a meeting following Robert's Rules of Order.
    You can:
    - Make motions (main, subsidiary, privileged, or incidental)
    - Second motions made by others
    - Request recognition to speak
    - Raise points of order
    - Participate in debate and voting
    
    Follow proper parliamentary procedure and be respectful.
    Remember motion precedence rules.""",
)

@member_agent.tool
async def make_motion(
    ctx: RunContext[RobertsRulesDeps],
    motion_type: str,
    motion_text: str
) -> Dict[str, Any]:
    """Make a motion with the specified type and text"""
    if ctx.deps.role == "chair" and motion_type != "incidental":
        raise ValueError("Chair cannot make motions except incidental")
    
    # Check precedence
    try:
        motion_type_enum = MotionType(motion_type)
        if not ctx.deps.state.can_make_motion(motion_type_enum):
            return {
                "error": f"Cannot make {motion_type} motion due to precedence rules",
                "active_motions": [m.type.value for m in ctx.deps.state.get_active_motions()]
            }
    except ValueError:
        return {"error": f"Invalid motion type: {motion_type}"}
    
    motion_id = f"motion-{datetime.now().timestamp()}"
    
    # Use the generated function
    result = roberts_motion_make(
        roberts_motion_id=motion_id,
        roberts_motion_type=motion_type,
        roberts_motion_text=motion_text,
        roberts_motion_mover=ctx.deps.member_name,
        roberts_motion_requires_second=True,
        roberts_motion_debatable=motion_type == "main",
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    
    if result.success:
        return {
            "motion_id": motion_id,
            "type": motion_type,
            "text": motion_text,
            "mover": ctx.deps.member_name,
            "status": "pending",
            "data": result.data
        }
    else:
        return {"error": f"Failed to make motion: {result.errors}"}

@member_agent.tool
async def second_motion(
    ctx: RunContext[RobertsRulesDeps],
    motion_id: str
) -> Dict[str, Any]:
    """Second a motion that has been made"""
    if ctx.deps.role == "chair":
        raise ValueError("Chair cannot second motions")
    
    motion = ctx.deps.state.motions.get(motion_id)
    if not motion:
        return {"error": f"Motion {motion_id} not found"}
    
    if motion.mover == ctx.deps.member_name:
        return {"error": "Cannot second your own motion"}
    
    if motion.seconder:
        return {"error": f"Motion already seconded by {motion.seconder}"}
    
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
        return {
            "motion_id": motion_id,
            "seconder": ctx.deps.member_name,
            "status": "seconded",
            "data": result.data
        }
    else:
        return {"error": f"Failed to second motion: {result.errors}"}

@member_agent.tool
async def get_meeting_state(ctx: RunContext[RobertsRulesDeps]) -> Dict[str, Any]:
    """Get the current state of the meeting"""
    state = ctx.deps.state
    
    return {
        "has_meeting": state.current_meeting is not None,
        "meeting_id": state.current_meeting.id if state.current_meeting else None,
        "has_quorum": state.current_meeting.has_quorum if state.current_meeting else False,
        "active_motions": [
            {
                "id": m.id,
                "type": m.type.value,
                "text": m.text[:50] + "..." if len(m.text) > 50 else m.text,
                "status": m.status.value,
                "mover": m.mover,
                "seconder": m.seconder
            }
            for m in state.get_active_motions()
        ],
        "total_motions": len(state.motions),
        "motion_hierarchy": [m.type.value for m in state.get_motion_hierarchy()]
    }

# Secretary Agent
secretary_agent = Agent(
    ollama_model,
    deps_type=RobertsRulesDeps,
    output_type=VoteResponse,
    system_prompt="""You are the Secretary of a meeting following Robert's Rules of Order.
    Your responsibilities:
    - Record accurate minutes of the proceedings
    - Read previous minutes when requested
    - Record all votes accurately
    - Maintain official records
    
    Be precise and detailed in your record-keeping.""",
)

@secretary_agent.tool
async def record_vote(
    ctx: RunContext[RobertsRulesDeps],
    motion_id: str,
    yes_votes: int,
    no_votes: int,
    abstentions: int = 0
) -> Dict[str, Any]:
    """Record the vote on a motion"""
    if ctx.deps.role != "secretary":
        raise ValueError("Only the secretary can record votes")
    
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
        return {
            "motion_id": motion_id,
            "yes": yes_votes,
            "no": no_votes,
            "abstain": abstentions,
            "result": result.data.get("result", "unknown"),
            "data": result.data
        }
    else:
        return {"error": f"Failed to record vote: {result.errors}"}

@secretary_agent.tool
async def get_meeting_minutes(ctx: RunContext[RobertsRulesDeps]) -> str:
    """Get a summary of the meeting proceedings so far"""
    state = ctx.deps.state
    if not state.current_meeting:
        return "No meeting in session"
    
    meeting = state.current_meeting
    minutes = f"""
MEETING MINUTES
===============
Meeting ID: {meeting.id}
Type: {meeting.type.value}
Chair: {meeting.chair}
Secretary: {meeting.secretary}
Attendance: {meeting.members_present} (Quorum: {meeting.quorum})

MOTIONS:
"""
    for motion_id in meeting.motions:
        motion = state.motions.get(motion_id)
        if motion:
            minutes += f"\n- {motion.type.value.upper()} MOTION by {motion.mover}: '{motion.text}'"
            minutes += f"\n  Status: {motion.status.value}"
            if motion.seconder:
                minutes += f", Seconded by: {motion.seconder}"
            
            # Find vote if exists
            for vote in state.votes:
                if vote.motion_id == motion_id:
                    minutes += f"\n  Vote: {vote.yes_count} Yes, {vote.no_count} No"
                    if vote.abstain_count:
                        minutes += f", {vote.abstain_count} Abstain"
                    minutes += f" - {vote.result.value.upper()}"
    
    return minutes

# Demo functions
async def demo_basic_meeting():
    """Demonstrate a basic meeting flow with agents"""
    print("🏛️  Roberts Rules Pydantic-AI Demo with Ollama")
    print("=" * 50)
    
    # Create dependencies
    chair_deps = RobertsRulesDeps("Chairperson Smith", "chair")
    member1_deps = RobertsRulesDeps("Alice Johnson", "member")
    member2_deps = RobertsRulesDeps("Bob Williams", "member")
    secretary_deps = RobertsRulesDeps("Secretary Davis", "secretary")
    
    # 1. Chair starts meeting
    print("\n1. STARTING MEETING")
    try:
        result = await chair_agent.run(
            "Please start a board meeting with 7 members expected",
            deps=chair_deps
        )
        print(f"Chair: {result.output}")
    except Exception as e:
        print(f"Error starting meeting: {e}")
        return
    
    # 2. Member makes a motion
    print("\n2. MAKING A MOTION")
    motion_result = await member_agent.run(
        "I'd like to make a main motion to approve the annual budget of $50,000",
        deps=member1_deps
    )
    print(f"Alice: {motion_result.output}")
    
    # 3. Get meeting state
    state = await get_meeting_state.fn(RunContext(deps=member2_deps))
    print(f"\nCurrent state: {state['active_motions']}")
    
    if state['active_motions']:
        motion_id = state['active_motions'][0]['id']
        
        # 4. Second the motion
        print("\n3. SECONDING THE MOTION")
        second_result = await member_agent.run(
            f"I second the motion {motion_id}",
            deps=member2_deps
        )
        print(f"Bob: {second_result.output}")
        
        # 5. Chair calls for vote
        print("\n4. CALLING FOR VOTE")
        vote_call = await call_for_vote.fn(
            RunContext(deps=chair_deps),
            motion_id
        )
        print(f"Chair: {vote_call}")
        
        # 6. Secretary records vote
        print("\n5. RECORDING VOTE")
        vote_result = await secretary_agent.run(
            f"Record the vote on motion {motion_id}: 5 in favor, 2 opposed",
            deps=secretary_deps
        )
        print(f"Secretary: {vote_result.output}")
        
        # 7. Get minutes
        print("\n6. MEETING MINUTES")
        minutes = await get_meeting_minutes.fn(RunContext(deps=secretary_deps))
        print(minutes)

async def demo_streaming():
    """Demonstrate streaming responses with agent iteration"""
    print("\n\n🌊 Streaming Demo")
    print("=" * 50)
    
    member_deps = RobertsRulesDeps("Carol Green", "member")
    
    # Use agent.run_stream for streaming responses
    async with member_agent.run_stream(
        "I want to make a subsidiary motion to table the current discussion",
        deps=member_deps
    ) as response:
        # Stream the response
        async for chunk in response:
            print(chunk, end='', flush=True)
        
        # Get the final output
        result = await response.get_output()
        print(f"\n\nFinal result: {result}")

async def demo_iteration():
    """Demonstrate agent iteration to see the execution flow"""
    print("\n\n🔄 Agent Iteration Demo")
    print("=" * 50)
    
    chair_deps = RobertsRulesDeps("Chair Wilson", "chair")
    
    # Iterate over the agent's graph execution
    async with chair_agent.iter(
        "Start a committee meeting with 5 attendees",
        deps=chair_deps
    ) as agent_run:
        print("Execution flow:")
        async for node in agent_run:
            node_type = type(node).__name__
            print(f"  → {node_type}")
            
            # You can inspect specific node types
            if hasattr(node, 'user_prompt'):
                print(f"     User said: {node.user_prompt}")
            elif hasattr(node, 'tool_name'):
                print(f"     Tool called: {node.tool_name}")
        
        # Get the final result
        print(f"\nFinal output: {agent_run.result.output}")

# Main execution
async def main():
    """Run all demonstrations"""
    print("🤖 Roberts Rules + Pydantic-AI + Ollama Integration")
    print("\nThis demonstrates:")
    print("- Semantic conventions → Generated telemetry code")
    print("- Pydantic models → Type-safe domain objects")
    print("- Pydantic-AI agents → Intelligent parliamentary behavior")
    print("- Ollama integration → Local LLM execution")
    
    # Ensure Ollama is running
    print("\n⚠️  Make sure Ollama is running: ollama run llama3.2")
    print("   If not installed: https://ollama.ai/download\n")
    
    # Run demonstrations
    try:
        await demo_basic_meeting()
        await demo_streaming()
        await demo_iteration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure Ollama is running with: ollama run llama3.2")
    
    print("\n\n✨ Demo Complete!")
    print("The system successfully integrates:")
    print("1. Generated code with full telemetry")
    print("2. Type-safe Pydantic models")
    print("3. Intelligent agents following Roberts Rules")
    print("4. Local LLM execution with Ollama")

if __name__ == "__main__":
    asyncio.run(main())