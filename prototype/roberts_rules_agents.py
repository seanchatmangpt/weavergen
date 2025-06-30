#!/usr/bin/env python3
"""
Pydantic-AI agents for Robert's Rules of Order parliamentary procedures.
These agents use the Pydantic models to simulate realistic meeting proceedings.
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import asyncio
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.ollama import OllamaModel

# Import our Roberts Rules models
from roberts_rules_models import (
    Meeting, Motion, Vote, PointOfOrder, RecognitionRequest, 
    ParliamentaryState, MeetingType, MotionType, MotionStatus,
    VoteThreshold, VoteMethod, VoteResult, RecognitionPurpose,
    create_main_motion, create_motion_to_adjourn, create_motion_to_table
)

# Configure Ollama model (can be changed to OpenAI, Anthropic, etc.)
model = OllamaModel(
    model_name='llama3.2',
    base_url='http://localhost:11434',
)

# Shared parliamentary state
parliamentary_state = ParliamentaryState()

# Dependencies for agents
@dataclass
class ParliamentaryDeps:
    """Dependencies passed to agents"""
    state: ParliamentaryState
    member_name: str
    role: Literal["chair", "secretary", "member"]

# Tools for parliamentary procedures

@Tool
async def start_meeting(
    ctx: RunContext[ParliamentaryDeps],
    meeting_type: MeetingType,
    expected_attendance: int
) -> Meeting:
    """Start a new meeting as the chair"""
    if ctx.deps.role != "chair":
        raise ValueError("Only the chair can start a meeting")
    
    meeting = Meeting(
        id=f"meeting-{datetime.now().strftime('%Y%m%d-%H%M')}",
        type=meeting_type,
        quorum=expected_attendance // 2 + 1,
        members_present=expected_attendance,
        chair=ctx.deps.member_name,
        secretary="Secretary Smith",  # Would be from deps in real system
        agenda_items=["Call to order", "Reading of minutes", "New business", "Adjournment"]
    )
    
    ctx.deps.state.current_meeting = meeting
    ctx.deps.state.meetings[meeting.id] = meeting
    
    return meeting

@Tool
async def make_motion(
    ctx: RunContext[ParliamentaryDeps],
    motion_type: MotionType,
    motion_text: str
) -> Motion:
    """Make a motion as a member"""
    if ctx.deps.role == "chair" and motion_type != MotionType.INCIDENTAL:
        raise ValueError("Chair cannot make motions except incidental")
    
    # Check if motion can be made given current state
    if not ctx.deps.state.can_make_motion(motion_type):
        raise ValueError(f"Cannot make {motion_type} motion at this time due to precedence")
    
    motion = Motion(
        id=f"motion-{datetime.now().timestamp()}",
        type=motion_type,
        text=motion_text,
        mover=ctx.deps.member_name,
        requires_second=True,  # Most motions require second
        debatable=motion_type == MotionType.MAIN,  # Main motions are debatable
        vote_required=VoteThreshold.MAJORITY
    )
    
    ctx.deps.state.motions[motion.id] = motion
    if ctx.deps.state.current_meeting:
        ctx.deps.state.current_meeting.motions.append(motion.id)
    
    return motion

@Tool
async def second_motion(
    ctx: RunContext[ParliamentaryDeps],
    motion_id: str
) -> Motion:
    """Second a motion as a member"""
    if ctx.deps.role == "chair":
        raise ValueError("Chair cannot second motions")
    
    motion = ctx.deps.state.motions.get(motion_id)
    if not motion:
        raise ValueError("Motion not found")
    
    if motion.mover == ctx.deps.member_name:
        raise ValueError("Cannot second your own motion")
    
    if motion.seconder:
        raise ValueError("Motion already seconded")
    
    motion.seconder = ctx.deps.member_name
    motion.status = MotionStatus.SECONDED
    
    return motion

@Tool
async def request_recognition(
    ctx: RunContext[ParliamentaryDeps],
    purpose: RecognitionPurpose
) -> RecognitionRequest:
    """Request recognition to speak"""
    request = RecognitionRequest(
        member=ctx.deps.member_name,
        purpose=purpose,
        granted=False  # Chair will grant later
    )
    
    position = ctx.deps.state.speaking_queue.add_to_queue(request)
    request.queue_position = position
    
    return request

@Tool
async def grant_recognition(
    ctx: RunContext[ParliamentaryDeps]
) -> Optional[RecognitionRequest]:
    """Grant recognition to next speaker (chair only)"""
    if ctx.deps.role != "chair":
        raise ValueError("Only chair can grant recognition")
    
    next_speaker = ctx.deps.state.speaking_queue.next_speaker()
    if next_speaker:
        next_speaker.granted = True
        next_speaker.queue_position = None
    
    return next_speaker

@Tool
async def call_for_vote(
    ctx: RunContext[ParliamentaryDeps],
    motion_id: str,
    method: VoteMethod = VoteMethod.VOICE
) -> str:
    """Call for a vote on a motion (chair only)"""
    if ctx.deps.role != "chair":
        raise ValueError("Only chair can call for votes")
    
    motion = ctx.deps.state.motions.get(motion_id)
    if not motion:
        raise ValueError("Motion not found")
    
    if motion.status != MotionStatus.SECONDED and not motion.debatable:
        raise ValueError("Motion must be seconded before voting")
    
    motion.status = MotionStatus.VOTING
    return f"The question is on the motion: {motion.text}. All in favor?"

@Tool
async def record_vote(
    ctx: RunContext[ParliamentaryDeps],
    motion_id: str,
    yes_votes: int,
    no_votes: int,
    abstentions: int = 0
) -> Vote:
    """Record the results of a vote (secretary only)"""
    if ctx.deps.role != "secretary":
        raise ValueError("Only secretary can record votes")
    
    motion = ctx.deps.state.motions.get(motion_id)
    if not motion:
        raise ValueError("Motion not found")
    
    vote = Vote(
        motion_id=motion_id,
        method=VoteMethod.VOICE,
        yes_count=yes_votes,
        no_count=no_votes,
        abstain_count=abstentions
    )
    
    # Check if vote meets threshold
    if vote.meets_threshold(motion.vote_required):
        motion.status = MotionStatus.PASSED
    else:
        motion.status = MotionStatus.FAILED
    
    ctx.deps.state.votes.append(vote)
    return vote

@Tool
async def raise_point_of_order(
    ctx: RunContext[ParliamentaryDeps],
    issue: str
) -> PointOfOrder:
    """Raise a point of order about procedure"""
    point = PointOfOrder(
        member=ctx.deps.member_name,
        issue=issue
    )
    
    ctx.deps.state.points_of_order.append(point)
    return point

@Tool
async def get_current_state(
    ctx: RunContext[ParliamentaryDeps]
) -> Dict[str, Any]:
    """Get current parliamentary state"""
    active_motions = ctx.deps.state.get_active_motions()
    
    return {
        "meeting_active": ctx.deps.state.current_meeting is not None,
        "has_quorum": ctx.deps.state.current_meeting.has_quorum if ctx.deps.state.current_meeting else False,
        "active_motions": len(active_motions),
        "motion_hierarchy": [
            {"id": m.id, "type": m.type, "status": m.status} 
            for m in ctx.deps.state.get_motion_hierarchy()
        ],
        "speaking_queue_length": len(ctx.deps.state.speaking_queue.queue),
        "current_speaker": ctx.deps.state.speaking_queue.current_speaker
    }

# Create specialized agents

chair_agent = Agent(
    model=model,
    deps_type=ParliamentaryDeps,
    system_prompt="""You are the Chair of a meeting following Robert's Rules of Order.
    Your responsibilities:
    - Maintain order and ensure proper procedure
    - Recognize members who wish to speak
    - Call for votes on motions
    - Rule on points of order
    - Ensure fair debate and participation
    
    Always be impartial and follow proper parliamentary procedure.""",
    tools=[start_meeting, grant_recognition, call_for_vote, get_current_state]
)

secretary_agent = Agent(
    model=model,
    deps_type=ParliamentaryDeps,
    system_prompt="""You are the Secretary of a meeting following Robert's Rules of Order.
    Your responsibilities:
    - Record accurate minutes of the proceedings
    - Read previous minutes when requested
    - Record all votes accurately
    - Maintain official records
    
    Be precise and detailed in your record-keeping.""",
    tools=[record_vote, get_current_state]
)

member_agent = Agent(
    model=model,
    deps_type=ParliamentaryDeps,
    result_type=str,
    system_prompt="""You are a member in a meeting following Robert's Rules of Order.
    You can:
    - Make motions (main, subsidiary, privileged, or incidental)
    - Second motions made by others
    - Request recognition to speak
    - Raise points of order
    - Participate in debate and voting
    
    Follow proper parliamentary procedure and be respectful.""",
    tools=[make_motion, second_motion, request_recognition, raise_point_of_order, get_current_state]
)

# Response models for structured agent outputs

class ChairAction(BaseModel):
    """Action taken by the chair"""
    action: Literal["recognize", "call_vote", "rule", "announce"]
    details: str
    
class MemberStatement(BaseModel):
    """Statement or action by a member"""
    action: Literal["motion", "second", "speak", "point_of_order"]
    content: str

# Simulation functions

async def simulate_meeting():
    """Simulate a complete meeting using agents"""
    print("🏛️  Robert's Rules Agent-Based Meeting Simulation")
    print("=" * 50)
    
    # Initialize dependencies for each role
    chair_deps = ParliamentaryDeps(parliamentary_state, "Jane Smith", "chair")
    secretary_deps = ParliamentaryDeps(parliamentary_state, "John Secretary", "secretary")
    member1_deps = ParliamentaryDeps(parliamentary_state, "Alice Member", "member")
    member2_deps = ParliamentaryDeps(parliamentary_state, "Bob Member", "member")
    
    # 1. Chair starts the meeting
    print("\n1. CHAIR STARTING MEETING")
    result = await chair_agent.run(
        "Start a board meeting with 7 expected attendees",
        deps=chair_deps
    )
    print(f"Chair: {result.data}")
    
    # 2. Member makes a motion
    print("\n2. MEMBER MAKING MOTION")
    result = await member_agent.run(
        "Make a main motion to approve the annual budget of $50,000",
        deps=member1_deps
    )
    print(f"Alice: {result.data}")
    
    # 3. Another member seconds
    print("\n3. SECOND THE MOTION")
    state = await get_current_state.fn(RunContext(deps=member2_deps))
    active_motion_id = state["motion_hierarchy"][0]["id"] if state["motion_hierarchy"] else None
    
    if active_motion_id:
        result = await member_agent.run(
            f"Second the motion {active_motion_id}",
            deps=member2_deps
        )
        print(f"Bob: {result.data}")
    
    # 4. Members request recognition to debate
    print("\n4. DEBATE")
    result = await member_agent.run(
        "Request recognition to speak in favor of the budget motion",
        deps=member1_deps
    )
    print(f"Alice: {result.data}")
    
    # Grant recognition
    result = await chair_agent.run(
        "Grant recognition to the next speaker",
        deps=chair_deps
    )
    print(f"Chair: {result.data}")
    
    # 5. Call for vote
    print("\n5. VOTING")
    result = await chair_agent.run(
        f"Call for a voice vote on motion {active_motion_id}",
        deps=chair_deps
    )
    print(f"Chair: {result.data}")
    
    # Secretary records vote
    result = await secretary_agent.run(
        f"Record vote on {active_motion_id}: 5 yes, 2 no, 0 abstain",
        deps=secretary_deps
    )
    print(f"Secretary: {result.data}")
    
    # 6. Final state
    print("\n6. FINAL STATE")
    final_state = await get_current_state.fn(RunContext(deps=chair_deps))
    print(f"\nMeeting Summary:")
    print(f"- Active motions: {final_state['active_motions']}")
    print(f"- Speaking queue: {final_state['speaking_queue_length']} waiting")
    print(f"- Has quorum: {final_state['has_quorum']}")

async def demonstrate_precedence():
    """Demonstrate motion precedence rules"""
    print("\n\n🎯 Motion Precedence Demonstration")
    print("=" * 50)
    
    member_deps = ParliamentaryDeps(parliamentary_state, "Demo Member", "member")
    
    # Make a main motion
    print("\n1. Making a main motion...")
    await member_agent.run(
        "Make a main motion to purchase new equipment",
        deps=member_deps
    )
    
    # Try to make another main motion (should fail)
    print("\n2. Trying another main motion (should fail)...")
    try:
        await member_agent.run(
            "Make another main motion about hiring",
            deps=member_deps
        )
    except Exception as e:
        print(f"   ❌ Failed as expected: {e}")
    
    # Make a subsidiary motion (should succeed)
    print("\n3. Making a subsidiary motion to table...")
    result = await member_agent.run(
        "Make a motion to table the current discussion",
        deps=member_deps
    )
    print(f"   ✅ Subsidiary motion succeeded: {result.data}")
    
    # Show motion hierarchy
    state = await get_current_state.fn(RunContext(deps=member_deps))
    print("\n4. Current motion hierarchy:")
    for i, motion in enumerate(state["motion_hierarchy"]):
        print(f"   {i+1}. {motion['type']} motion (ID: {motion['id']})")

# Main execution
if __name__ == "__main__":
    print("🤖 Robert's Rules of Order - Pydantic AI Agent Simulation")
    print("\nThis demonstrates how semantic conventions can generate")
    print("complex agent-based systems with proper domain logic.\n")
    
    # Run the simulations
    asyncio.run(simulate_meeting())
    asyncio.run(demonstrate_precedence())
    
    print("\n\n✨ Key Insights:")
    print("- Agents enforce Robert's Rules through tool constraints")
    print("- Pydantic models ensure type safety and validation")
    print("- State management tracks complete parliamentary proceedings")
    print("- Motion precedence is automatically enforced")
    print("- Each role (chair, secretary, member) has appropriate permissions")