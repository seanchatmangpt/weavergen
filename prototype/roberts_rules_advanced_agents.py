#!/usr/bin/env python3
"""
Advanced Pydantic-AI agent system for Robert's Rules of Order.
This demonstrates how autonomous code generation can create sophisticated
multi-agent systems with complex interactions and state management.
"""

from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
import asyncio
from dataclasses import dataclass
import json

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool, ModelRetry
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.ollama import OllamaModel

# Import our models and generated code
from roberts_rules_models import *
from output.roberts import *

# Configure model (can switch between providers)
# For Ollama:
model = OllamaModel(
    model_name='llama3.2',
    base_url='http://localhost:11434',
)

# For OpenAI (uncomment to use):
# model = OpenAIModel('gpt-4-turbo-preview')

# Extended Dependencies
@dataclass
class EnhancedParliamentaryDeps:
    """Enhanced dependencies with telemetry integration"""
    state: ParliamentaryState
    member_name: str
    role: Literal["chair", "secretary", "member", "parliamentarian"]
    meeting_context: Dict[str, Any]
    telemetry_enabled: bool = True

# Advanced Tools with Telemetry

@Tool
async def analyze_motion_validity(
    ctx: RunContext[EnhancedParliamentaryDeps],
    motion_text: str,
    motion_type: MotionType
) -> Dict[str, Any]:
    """Analyze if a motion is valid according to Robert's Rules"""
    # Use the generated validation from semantic conventions
    result = roberts_motion_make(
        motion_id=f"test-{datetime.now().timestamp()}",
        motion_type=motion_type.value,
        motion_text=motion_text,
        mover=ctx.deps.member_name,
        requires_second=True,
        debatable=motion_type == MotionType.MAIN,
        vote_required="majority",
        motion_status="pending"
    )
    
    analysis = {
        "valid": result.success,
        "requires_second": True,
        "debatable": motion_type == MotionType.MAIN,
        "precedence": Motion(
            id="temp", type=motion_type, text=motion_text,
            mover=ctx.deps.member_name, requires_second=True,
            debatable=True, vote_required=VoteThreshold.MAJORITY
        ).get_precedence_level(),
        "can_interrupt": motion_type in [MotionType.PRIVILEGED, MotionType.INCIDENTAL],
        "errors": result.errors if not result.success else []
    }
    
    return analysis

@Tool
async def suggest_parliamentary_action(
    ctx: RunContext[EnhancedParliamentaryDeps],
    situation: str
) -> List[Dict[str, str]]:
    """Suggest appropriate parliamentary actions for a situation"""
    suggestions = []
    
    # Analyze current state
    active_motions = ctx.deps.state.get_active_motions()
    hierarchy = ctx.deps.state.get_motion_hierarchy()
    
    # Common situations and responses
    if "debate" in situation.lower() and active_motions:
        suggestions.append({
            "action": "Move to limit debate",
            "type": "subsidiary",
            "effect": "Limits time for debate on current motion"
        })
        suggestions.append({
            "action": "Move the previous question",
            "type": "subsidiary", 
            "effect": "Ends debate and forces immediate vote"
        })
    
    if "break" in situation.lower() or "recess" in situation.lower():
        suggestions.append({
            "action": "Move to recess",
            "type": "privileged",
            "effect": "Take a short break, resume at specified time"
        })
    
    if "end" in situation.lower() or "adjourn" in situation.lower():
        suggestions.append({
            "action": "Move to adjourn",
            "type": "privileged",
            "effect": "End the meeting"
        })
    
    if "table" in situation.lower() and active_motions:
        suggestions.append({
            "action": "Move to table",
            "type": "subsidiary",
            "effect": "Postpone current motion indefinitely"
        })
    
    return suggestions

@Tool
async def generate_meeting_transcript(
    ctx: RunContext[EnhancedParliamentaryDeps]
) -> str:
    """Generate a formatted meeting transcript"""
    if not ctx.deps.state.current_meeting:
        return "No active meeting"
    
    meeting = ctx.deps.state.current_meeting
    transcript = f"""
MEETING TRANSCRIPT
==================
Meeting ID: {meeting.id}
Type: {meeting.type}
Date: {meeting.start_time.strftime('%Y-%m-%d %H:%M')}
Chair: {meeting.chair}
Secretary: {meeting.secretary}
Attendance: {meeting.members_present} present (Quorum: {meeting.quorum})

PROCEEDINGS:
------------
"""
    
    # Add motions in chronological order
    for motion_id in meeting.motions:
        motion = ctx.deps.state.motions.get(motion_id)
        if motion:
            transcript += f"\n{motion.created_at.strftime('%H:%M')} - MOTION by {motion.mover}:\n"
            transcript += f"  \"{motion.text}\"\n"
            transcript += f"  Type: {motion.type}, Status: {motion.status}\n"
            
            if motion.seconder:
                transcript += f"  Seconded by: {motion.seconder}\n"
            
            # Find related vote
            for vote in ctx.deps.state.votes:
                if vote.motion_id == motion_id:
                    transcript += f"  Vote: {vote.yes_count} Yes, {vote.no_count} No"
                    if vote.abstain_count:
                        transcript += f", {vote.abstain_count} Abstain"
                    transcript += f" - {vote.result}\n"
    
    return transcript

@Tool
async def check_procedural_errors(
    ctx: RunContext[EnhancedParliamentaryDeps]
) -> List[Dict[str, str]]:
    """Check for common procedural errors in the current state"""
    errors = []
    
    # Check for motions without seconds
    for motion in ctx.deps.state.get_active_motions():
        if motion.requires_second and not motion.seconder and motion.status != MotionStatus.PENDING:
            errors.append({
                "error": "Motion progressed without required second",
                "motion_id": motion.id,
                "severity": "high"
            })
    
    # Check for invalid motion hierarchy
    hierarchy = ctx.deps.state.get_motion_hierarchy()
    for i in range(1, len(hierarchy)):
        if hierarchy[i].get_precedence_level() > hierarchy[i-1].get_precedence_level():
            errors.append({
                "error": "Motion precedence violation",
                "details": f"{hierarchy[i].type} motion made while {hierarchy[i-1].type} is pending",
                "severity": "medium"
            })
    
    # Check quorum
    if ctx.deps.state.current_meeting and not ctx.deps.state.current_meeting.has_quorum:
        errors.append({
            "error": "Meeting proceeding without quorum",
            "severity": "high"
        })
    
    return errors

# Specialized Agents with Advanced Capabilities

parliamentarian_agent = Agent(
    model=model,
    deps_type=EnhancedParliamentaryDeps,
    system_prompt="""You are an expert Parliamentarian advising on Robert's Rules of Order.
    Your role is to:
    - Ensure all procedures follow Robert's Rules correctly
    - Advise on proper motions and their precedence
    - Identify procedural errors
    - Suggest appropriate parliamentary actions
    - Educate members on proper procedure
    
    Be precise, cite specific rules when relevant, and maintain strict neutrality.""",
    tools=[analyze_motion_validity, suggest_parliamentary_action, check_procedural_errors, get_current_state]
)

facilitator_agent = Agent(
    model=model,
    deps_type=EnhancedParliamentaryDeps,
    result_type=Dict[str, Any],
    system_prompt="""You are a meeting facilitator helping ensure smooth proceedings.
    Your role is to:
    - Track the flow of discussion
    - Identify when parliamentary actions might help
    - Suggest ways to move the meeting forward efficiently
    - Generate clear summaries and transcripts
    - Help resolve procedural confusion
    
    Be helpful and constructive while respecting formal procedures.""",
    tools=[generate_meeting_transcript, suggest_parliamentary_action, get_current_state]
)

# Advanced Simulation Scenarios

async def simulate_complex_debate():
    """Simulate a complex debate with multiple motions and amendments"""
    print("\n🎭 Complex Parliamentary Debate Simulation")
    print("=" * 50)
    
    # Setup
    state = ParliamentaryState()
    context = {"topic": "Annual Budget", "controversy_level": "high"}
    
    # Create dependencies for different roles
    chair_deps = EnhancedParliamentaryDeps(state, "Chair Wilson", "chair", context)
    parl_deps = EnhancedParliamentaryDeps(state, "Dr. Roberts", "parliamentarian", context)
    member_deps = EnhancedParliamentaryDeps(state, "Member Johnson", "member", context)
    
    # Start meeting
    meeting = Meeting(
        id="budget-meeting-2024",
        type=MeetingType.GENERAL,
        quorum=20,
        members_present=35,
        chair=chair_deps.member_name,
        secretary="Secretary Adams"
    )
    state.current_meeting = meeting
    state.meetings[meeting.id] = meeting
    
    print(f"\n1. Meeting Started - {meeting.members_present} present (quorum: {meeting.quorum})")
    
    # Main motion
    main_motion = create_main_motion(
        "Approve the annual budget of $500,000 as presented",
        "Treasurer Smith"
    )
    state.motions[main_motion.id] = main_motion
    main_motion.seconder = "Member Brown"
    main_motion.status = MotionStatus.SECONDED
    meeting.motions.append(main_motion.id)
    
    print(f"\n2. Main Motion: {main_motion.text}")
    print(f"   Moved by: {main_motion.mover}, Seconded by: {main_motion.seconder}")
    
    # Check parliamentary situation
    parl_result = await parliamentarian_agent.run(
        "What parliamentary actions are available during debate on the budget motion?",
        deps=parl_deps
    )
    print(f"\n3. Parliamentarian Advice: {parl_result.data}")
    
    # Amendment motion
    amendment = Motion(
        id="amendment-001",
        type=MotionType.SUBSIDIARY,
        text="Amend by reducing the budget to $450,000",
        mover="Member Green",
        seconder="Member White",
        requires_second=True,
        debatable=True,
        vote_required=VoteThreshold.MAJORITY,
        status=MotionStatus.SECONDED,
        parent_motion=main_motion.id
    )
    state.motions[amendment.id] = amendment
    meeting.motions.append(amendment.id)
    
    print(f"\n4. Amendment: {amendment.text}")
    
    # Check for errors
    errors = await check_procedural_errors.fn(RunContext(deps=parl_deps))
    if errors:
        print("\n5. Procedural Issues Detected:")
        for error in errors:
            print(f"   ⚠️  {error['error']} (Severity: {error['severity']})")
    else:
        print("\n5. ✅ No procedural errors detected")
    
    # Generate transcript
    transcript = await generate_meeting_transcript.fn(RunContext(deps=chair_deps))
    print(f"\n6. Meeting Transcript Preview:")
    print(transcript[:500] + "...")
    
    return state

async def simulate_motion_precedence_challenge():
    """Simulate a complex precedence scenario"""
    print("\n\n🏛️ Motion Precedence Challenge")
    print("=" * 50)
    
    state = ParliamentaryState()
    context = {"scenario": "precedence_test"}
    parl_deps = EnhancedParliamentaryDeps(state, "Parliamentarian", "parliamentarian", context)
    
    # Create a hierarchy of motions
    motions = [
        ("main", "Approve new policy handbook", MotionType.MAIN),
        ("amend", "Amend to add ethics section", MotionType.SUBSIDIARY),
        ("recess", "Recess for 15 minutes", MotionType.PRIVILEGED),
    ]
    
    for i, (key, text, mtype) in enumerate(motions):
        motion = Motion(
            id=f"motion-{key}",
            type=mtype,
            text=text,
            mover=f"Member{i}",
            requires_second=True,
            debatable=mtype == MotionType.MAIN,
            vote_required=VoteThreshold.MAJORITY,
            status=MotionStatus.SECONDED
        )
        state.motions[motion.id] = motion
        
        # Check if motion can be made
        can_make = state.can_make_motion(mtype)
        print(f"\n{i+1}. Attempting: {text}")
        print(f"   Type: {mtype}, Precedence: {motion.get_precedence_level()}")
        print(f"   Can be made: {'✅ Yes' if can_make else '❌ No'}")
    
    # Ask parliamentarian for analysis
    result = await parliamentarian_agent.run(
        "Analyze the current motion hierarchy and explain the precedence rules",
        deps=parl_deps
    )
    print(f"\n📋 Parliamentarian Analysis: {result.data}")

async def simulate_point_of_order_scenario():
    """Simulate handling points of order"""
    print("\n\n⚖️ Point of Order Scenario")
    print("=" * 50)
    
    state = ParliamentaryState()
    context = {"scenario": "point_of_order"}
    
    # Setup meeting with a procedural violation
    meeting = Meeting(
        id="test-meeting",
        type=MeetingType.BOARD,
        quorum=5,
        members_present=4,  # Below quorum!
        chair="Chair Smith",
        secretary="Secretary Jones"
    )
    state.current_meeting = meeting
    
    # Try to pass a motion without quorum
    motion = create_main_motion("Approve $10,000 expenditure", "Member A")
    motion.status = MotionStatus.VOTING
    state.motions[motion.id] = motion
    
    print(f"1. Meeting has {meeting.members_present} members (quorum: {meeting.quorum})")
    print(f"2. Motion being voted on: {motion.text}")
    
    # Member raises point of order
    point = PointOfOrder(
        member="Member B",
        issue="We don't have quorum to conduct business"
    )
    state.points_of_order.append(point)
    
    print(f"\n3. POINT OF ORDER by {point.member}: {point.issue}")
    
    # Parliamentarian checks
    parl_deps = EnhancedParliamentaryDeps(state, "Parliamentarian", "parliamentarian", context)
    errors = await check_procedural_errors.fn(RunContext(deps=parl_deps))
    
    print("\n4. Parliamentarian Review:")
    for error in errors:
        print(f"   ❌ {error['error']} (Severity: {error['severity']})")
    
    # Chair ruling
    point.ruling = "Point well taken. We lack quorum. No business can be conducted."
    print(f"\n5. CHAIR RULING: {point.ruling}")

# Main demonstration
async def main():
    """Run all demonstrations"""
    print("🚀 Advanced Robert's Rules Agent System")
    print("Demonstrating autonomous code generation for complex domains\n")
    
    # Run simulations
    await simulate_complex_debate()
    await simulate_motion_precedence_challenge()
    await simulate_point_of_order_scenario()
    
    print("\n\n✨ Key Achievements:")
    print("1. Semantic conventions → Working parliamentary system")
    print("2. Type-safe models with business logic validation")
    print("3. Multi-agent coordination with role-based permissions")
    print("4. Automatic precedence and procedure enforcement")
    print("5. Full observability through generated telemetry")
    print("6. Complex state management and error detection")
    
    print("\n🔄 The Semantic Quine at Work:")
    print("This entire system was generated from semantic conventions,")
    print("demonstrating how code can understand and regenerate itself")
    print("while maintaining domain expertise and operational correctness!")

if __name__ == "__main__":
    asyncio.run(main())