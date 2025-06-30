#!/usr/bin/env python3
"""
Integrated operations layer that bridges the generated code with Pydantic models.
This replaces the placeholder operations with implementations using our models.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

# Add paths for imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'output', 'roberts'))

# Import our Pydantic models
from roberts_rules_models import (
    Meeting, Motion, Vote, PointOfOrder, RecognitionRequest,
    ParliamentaryState, MeetingType, MotionType, MotionStatus,
    VoteThreshold, VoteMethod, VoteResult, RecognitionPurpose,
    MeetingStartRequest, MotionMakeRequest, VoteRecordRequest
)

# Import the generated result type
from output.roberts.commands.forge import ForgeResult

# Import runtime utilities
from output.roberts.runtime.roberts import (
    meeting_state,
    validate_quorum,
    validate_motion_type,
    validate_vote_method
)

# Global parliamentary state using Pydantic models
pydantic_state = ParliamentaryState()

def roberts_meeting_start_execute(
    roberts_meeting_id: str,
    roberts_meeting_type: str,
    roberts_meeting_quorum: int,
    roberts_meeting_members_present: int,
    roberts_meeting_chair: str,
    roberts_meeting_secretary: str,
) -> ForgeResult:
    """Start a meeting using Pydantic models"""
    try:
        # Validate input using Pydantic
        request = MeetingStartRequest(
            meeting_id=roberts_meeting_id,
            meeting_type=MeetingType(roberts_meeting_type),
            quorum=roberts_meeting_quorum,
            members_present=roberts_meeting_members_present,
            chair=roberts_meeting_chair,
            secretary=roberts_meeting_secretary
        )
        
        # Create Meeting model
        meeting = Meeting(
            id=request.meeting_id,
            type=request.meeting_type,
            quorum=request.quorum,
            members_present=request.members_present,
            chair=request.chair,
            secretary=request.secretary
        )
        
        # Check quorum
        if not meeting.has_quorum:
            return ForgeResult(
                success=False,
                errors=[f"Quorum not met. Required: {meeting.quorum}, Present: {meeting.members_present}"]
            )
        
        # Update both states (runtime and Pydantic)
        pydantic_state.current_meeting = meeting
        pydantic_state.meetings[meeting.id] = meeting
        
        # Also update the runtime state for compatibility
        success = meeting_state.start_meeting(
            meeting_id=meeting.id,
            meeting_type=meeting.type.value,
            quorum=meeting.quorum,
            members_present=meeting.members_present,
            chair=meeting.chair,
            secretary=meeting.secretary
        )
        
        return ForgeResult(
            success=True,
            data={
                "meeting_id": meeting.id,
                "status": "in_session",
                "quorum_met": meeting.has_quorum,
                "meeting_model": meeting.model_dump()
            }
        )
        
    except Exception as e:
        return ForgeResult(success=False, errors=[str(e)])

def roberts_motion_make_execute(
    roberts_motion_id: str,
    roberts_motion_type: str,
    roberts_motion_text: str,
    roberts_motion_mover: str,
    roberts_motion_requires_second: bool,
    roberts_motion_debatable: bool,
    roberts_motion_vote_required: str,
    roberts_motion_status: str,
    roberts_motion_seconder: Optional[str] = None,
) -> ForgeResult:
    """Make a motion using Pydantic models"""
    try:
        # Validate using Pydantic
        motion_type_enum = MotionType(roberts_motion_type)
        vote_threshold = VoteThreshold(roberts_motion_vote_required)
        
        # Check if motion can be made
        if not pydantic_state.can_make_motion(motion_type_enum):
            return ForgeResult(
                success=False,
                errors=[f"Cannot make {motion_type_enum.value} motion due to precedence rules"]
            )
        
        # Create Motion model
        motion = Motion(
            id=roberts_motion_id,
            type=motion_type_enum,
            text=roberts_motion_text,
            mover=roberts_motion_mover,
            seconder=roberts_motion_seconder,
            requires_second=roberts_motion_requires_second,
            debatable=roberts_motion_debatable,
            vote_required=vote_threshold,
            status=MotionStatus(roberts_motion_status)
        )
        
        # Add to state
        pydantic_state.motions[motion.id] = motion
        if pydantic_state.current_meeting:
            pydantic_state.current_meeting.motions.append(motion.id)
        
        # Also update runtime state
        meeting_state.add_motion(
            motion_id=motion.id,
            motion_type=motion.type.value,
            text=motion.text,
            mover=motion.mover,
            requires_second=motion.requires_second,
            debatable=motion.debatable,
            vote_required=motion.vote_required.value
        )
        
        return ForgeResult(
            success=True,
            data={
                "motion_id": motion.id,
                "status": motion.status.value,
                "precedence_level": motion.get_precedence_level(),
                "can_be_debated": motion.can_be_debated,
                "motion_model": motion.model_dump()
            }
        )
        
    except Exception as e:
        return ForgeResult(success=False, errors=[str(e)])

def roberts_motion_second_execute(
    roberts_motion_id: str,
    roberts_motion_type: str,
    roberts_motion_text: str,
    roberts_motion_mover: str,
    roberts_motion_seconder: str,
    roberts_motion_requires_second: bool,
    roberts_motion_debatable: bool,
    roberts_motion_vote_required: str,
    roberts_motion_status: str,
) -> ForgeResult:
    """Second a motion using Pydantic models"""
    try:
        motion = pydantic_state.motions.get(roberts_motion_id)
        if not motion:
            return ForgeResult(success=False, errors=["Motion not found"])
        
        if motion.seconder:
            return ForgeResult(success=False, errors=["Motion already seconded"])
        
        if motion.mover == roberts_motion_seconder:
            return ForgeResult(success=False, errors=["Cannot second your own motion"])
        
        # Update motion
        motion.seconder = roberts_motion_seconder
        motion.status = MotionStatus.SECONDED
        
        # Update runtime state
        meeting_state.second_motion(roberts_motion_id, roberts_motion_seconder)
        
        return ForgeResult(
            success=True,
            data={
                "motion_id": motion.id,
                "status": motion.status.value,
                "can_be_debated": motion.can_be_debated,
                "next_step": "debate" if motion.debatable else "vote"
            }
        )
        
    except Exception as e:
        return ForgeResult(success=False, errors=[str(e)])

def roberts_vote_record_execute(
    roberts_vote_motion_id: str,
    roberts_vote_method: str,
    roberts_vote_yes_count: int,
    roberts_vote_no_count: int,
    roberts_vote_result: str,
    roberts_vote_abstain_count: Optional[int] = None,
) -> ForgeResult:
    """Record a vote using Pydantic models"""
    try:
        # Validate vote method
        vote_method = VoteMethod(roberts_vote_method)
        
        # Get motion
        motion = pydantic_state.motions.get(roberts_vote_motion_id)
        if not motion:
            return ForgeResult(success=False, errors=["Motion not found"])
        
        # Create Vote model
        vote = Vote(
            motion_id=roberts_vote_motion_id,
            method=vote_method,
            yes_count=roberts_vote_yes_count,
            no_count=roberts_vote_no_count,
            abstain_count=roberts_vote_abstain_count or 0
        )
        
        # Check if vote meets threshold
        if vote.meets_threshold(motion.vote_required):
            motion.status = MotionStatus.PASSED
            vote.result = VoteResult.PASSED
        else:
            motion.status = MotionStatus.FAILED
            vote.result = VoteResult.FAILED
        
        # Add to state
        pydantic_state.votes.append(vote)
        
        # Update runtime state
        meeting_state.record_vote(
            motion_id=vote.motion_id,
            yes_count=vote.yes_count,
            no_count=vote.no_count,
            abstain_count=vote.abstain_count,
            vote_method=vote.method.value
        )
        
        return ForgeResult(
            success=True,
            data={
                "motion_id": vote.motion_id,
                "result": vote.result.value,
                "yes": vote.yes_count,
                "no": vote.no_count,
                "abstain": vote.abstain_count,
                "meets_threshold": vote.meets_threshold(motion.vote_required),
                "vote_model": vote.model_dump()
            }
        )
        
    except Exception as e:
        return ForgeResult(success=False, errors=[str(e)])

def roberts_point_of_order_raise_execute(
    roberts_point_of_order_member: str,
    roberts_point_of_order_issue: str,
    roberts_point_of_order_ruling: Optional[str] = None,
    roberts_point_of_order_appealed: Optional[bool] = None,
) -> ForgeResult:
    """Raise a point of order using Pydantic models"""
    try:
        # Create PointOfOrder model
        point = PointOfOrder(
            member=roberts_point_of_order_member,
            issue=roberts_point_of_order_issue,
            ruling=roberts_point_of_order_ruling,
            appealed=roberts_point_of_order_appealed or False
        )
        
        # Add to state
        pydantic_state.points_of_order.append(point)
        
        # Handle appeal if necessary
        if point.appealed and point.ruling:
            # Create appeal motion
            appeal_motion = Motion(
                id=f"appeal-{point.timestamp.timestamp()}",
                type=MotionType.INCIDENTAL,
                text=f"Appeal the ruling of the chair regarding: {point.issue}",
                mover=point.member,
                requires_second=True,
                debatable=True,
                vote_required=VoteThreshold.MAJORITY
            )
            pydantic_state.motions[appeal_motion.id] = appeal_motion
            point.appeal_motion_id = appeal_motion.id
        
        return ForgeResult(
            success=True,
            data={
                "member": point.member,
                "issue": point.issue,
                "ruling": point.ruling,
                "appealed": point.appealed,
                "appeal_motion_id": point.appeal_motion_id,
                "point_model": point.model_dump()
            }
        )
        
    except Exception as e:
        return ForgeResult(success=False, errors=[str(e)])

def roberts_recognition_request_execute(
    roberts_recognition_member: str,
    roberts_recognition_purpose: str,
    roberts_recognition_granted: bool,
    roberts_recognition_queue_position: Optional[int] = None,
) -> ForgeResult:
    """Request recognition using Pydantic models"""
    try:
        # Create RecognitionRequest model
        purpose = RecognitionPurpose(roberts_recognition_purpose)
        
        request = RecognitionRequest(
            member=roberts_recognition_member,
            purpose=purpose,
            granted=roberts_recognition_granted,
            queue_position=roberts_recognition_queue_position
        )
        
        if not request.granted:
            # Add to queue
            position = pydantic_state.speaking_queue.add_to_queue(request)
            request.queue_position = position
        
        return ForgeResult(
            success=True,
            data={
                "member": request.member,
                "purpose": request.purpose.value,
                "granted": request.granted,
                "queue_position": request.queue_position,
                "status": "recognized" if request.granted else "queued",
                "request_model": request.model_dump()
            }
        )
        
    except Exception as e:
        return ForgeResult(success=False, errors=[str(e)])

# Export the state for use in agents
def get_pydantic_state() -> ParliamentaryState:
    """Get the current Pydantic-based parliamentary state"""
    return pydantic_state

# Update the generated operations module
def install_integrated_operations():
    """Replace the generated placeholder operations with our integrated ones"""
    import output.roberts.operations.forge as forge_ops
    
    # Replace the placeholder functions with our implementations
    forge_ops.roberts_meeting_start_execute = roberts_meeting_start_execute
    forge_ops.roberts_motion_make_execute = roberts_motion_make_execute
    forge_ops.roberts_motion_second_execute = roberts_motion_second_execute
    forge_ops.roberts_vote_record_execute = roberts_vote_record_execute
    forge_ops.roberts_point_of_order_raise_execute = roberts_point_of_order_raise_execute
    forge_ops.roberts_recognition_request_execute = roberts_recognition_request_execute
    
    print("✅ Integrated operations installed successfully")

if __name__ == "__main__":
    # Install the integrated operations
    install_integrated_operations()
    
    print("🔗 Roberts Rules Integration Complete!")
    print("   - Pydantic models provide type safety and validation")
    print("   - Generated code provides telemetry and structure")
    print("   - Integrated operations bridge both systems")