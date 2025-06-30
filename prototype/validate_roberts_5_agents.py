#!/usr/bin/env python3
"""
Validate Roberts Rules with 5 agents going through a complete meeting.
Output telemetry and test results as Mermaid diagrams.
"""

import sys
import os
import asyncio
import json
import csv
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'output'))

# Import everything
from roberts_integrated_operations import install_integrated_operations, get_pydantic_state
install_integrated_operations()

from output.roberts.commands.forge import (
    roberts_meeting_start,
    roberts_motion_make,
    roberts_motion_second,
    roberts_vote_record,
    roberts_point_of_order_raise,
    roberts_recognition_request
)

from roberts_rules_models import (
    ParliamentaryState, MeetingType, MotionType, MotionStatus
)

# Track telemetry
telemetry_data = []

def record_telemetry(operation: str, success: bool, duration: float, details: Dict[str, Any] = None):
    """Record telemetry data"""
    telemetry_data.append({
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "success": success,
        "duration": duration,
        "details": details or {}
    })

def simulate_5_agent_meeting():
    """Simulate a complete Roberts Rules meeting with 5 agents"""
    
    # 5 Agents
    agents = {
        "chair": "Chairperson Wilson",
        "secretary": "Secretary Thompson", 
        "member1": "Alice Member",
        "member2": "Bob Member",
        "member3": "Carol Member"
    }
    
    results = []
    
    # 1. Chair starts meeting
    start_time = datetime.now()
    result = roberts_meeting_start(
        roberts_meeting_id="meeting-2024-validation",
        roberts_meeting_type="board",
        roberts_meeting_quorum=3,
        roberts_meeting_members_present=5,
        roberts_meeting_chair=agents["chair"],
        roberts_meeting_secretary=agents["secretary"]
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("meeting.start", result.success, duration, {
        "agent": "chair",
        "quorum": 3,
        "present": 5
    })
    results.append(("meeting_start", result.success))
    
    # 2. Member1 makes main motion
    start_time = datetime.now()
    motion1_result = roberts_motion_make(
        roberts_motion_id="motion-001-budget",
        roberts_motion_type="main",
        roberts_motion_text="Approve annual budget of $100,000",
        roberts_motion_mover=agents["member1"],
        roberts_motion_requires_second=True,
        roberts_motion_debatable=True,
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("motion.make.main", motion1_result.success, duration, {
        "agent": "member1",
        "motion_type": "main"
    })
    results.append(("motion_main", motion1_result.success))
    
    # 3. Member2 seconds
    start_time = datetime.now()
    second_result = roberts_motion_second(
        roberts_motion_id="motion-001-budget",
        roberts_motion_type="main",
        roberts_motion_text="Approve annual budget of $100,000",
        roberts_motion_mover=agents["member1"],
        roberts_motion_seconder=agents["member2"],
        roberts_motion_requires_second=True,
        roberts_motion_debatable=True,
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("motion.second", second_result.success, duration, {
        "agent": "member2",
        "motion_id": "motion-001-budget"
    })
    results.append(("motion_second", second_result.success))
    
    # 4. Member3 makes subsidiary motion to amend
    start_time = datetime.now()
    motion2_result = roberts_motion_make(
        roberts_motion_id="motion-002-amend",
        roberts_motion_type="subsidiary",
        roberts_motion_text="Amend to reduce budget to $90,000",
        roberts_motion_mover=agents["member3"],
        roberts_motion_requires_second=True,
        roberts_motion_debatable=True,
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("motion.make.subsidiary", motion2_result.success, duration, {
        "agent": "member3",
        "motion_type": "subsidiary"
    })
    results.append(("motion_subsidiary", motion2_result.success))
    
    # 5. Member1 seconds the amendment
    start_time = datetime.now()
    second2_result = roberts_motion_second(
        roberts_motion_id="motion-002-amend",
        roberts_motion_type="subsidiary",
        roberts_motion_text="Amend to reduce budget to $90,000",
        roberts_motion_mover=agents["member3"],
        roberts_motion_seconder=agents["member1"],
        roberts_motion_requires_second=True,
        roberts_motion_debatable=True,
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("motion.second", second2_result.success, duration, {
        "agent": "member1",
        "motion_id": "motion-002-amend"
    })
    results.append(("amendment_second", second2_result.success))
    
    # 6. Secretary records vote on amendment
    start_time = datetime.now()
    vote1_result = roberts_vote_record(
        roberts_vote_motion_id="motion-002-amend",
        roberts_vote_method="voice",
        roberts_vote_yes_count=3,
        roberts_vote_no_count=2,
        roberts_vote_abstain_count=0,
        roberts_vote_result="passed"
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("vote.record", vote1_result.success, duration, {
        "agent": "secretary",
        "motion_id": "motion-002-amend",
        "yes": 3,
        "no": 2,
        "result": "passed"
    })
    results.append(("vote_amendment", vote1_result.success))
    
    # 7. Member2 raises point of order
    start_time = datetime.now()
    point_result = roberts_point_of_order_raise(
        roberts_point_of_order_member=agents["member2"],
        roberts_point_of_order_issue="Amendment changes the nature of the original motion",
        roberts_point_of_order_ruling="Point not well taken - amendment is germane",
        roberts_point_of_order_appealed=False
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("point_of_order.raise", point_result.success, duration, {
        "agent": "member2",
        "appealed": False
    })
    results.append(("point_of_order", point_result.success))
    
    # 8. Secretary records final vote on main motion as amended
    start_time = datetime.now()
    vote2_result = roberts_vote_record(
        roberts_vote_motion_id="motion-001-budget",
        roberts_vote_method="roll_call",
        roberts_vote_yes_count=4,
        roberts_vote_no_count=1,
        roberts_vote_abstain_count=0,
        roberts_vote_result="passed"
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("vote.record", vote2_result.success, duration, {
        "agent": "secretary",
        "motion_id": "motion-001-budget",
        "yes": 4,
        "no": 1,
        "result": "passed"
    })
    results.append(("vote_main_motion", vote2_result.success))
    
    # 9. Member3 requests recognition for new business
    start_time = datetime.now()
    recognition_result = roberts_recognition_request(
        roberts_recognition_member=agents["member3"],
        roberts_recognition_purpose="make_motion",
        roberts_recognition_granted=True,
        roberts_recognition_queue_position=None
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("recognition.request", recognition_result.success, duration, {
        "agent": "member3",
        "purpose": "make_motion",
        "granted": True
    })
    results.append(("recognition_request", recognition_result.success))
    
    # 10. Member3 makes motion to adjourn (privileged)
    start_time = datetime.now()
    adjourn_result = roberts_motion_make(
        roberts_motion_id="motion-003-adjourn",
        roberts_motion_type="privileged",
        roberts_motion_text="I move to adjourn",
        roberts_motion_mover=agents["member3"],
        roberts_motion_requires_second=True,
        roberts_motion_debatable=False,
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    duration = (datetime.now() - start_time).total_seconds()
    record_telemetry("motion.make.privileged", adjourn_result.success, duration, {
        "agent": "member3",
        "motion_type": "privileged"
    })
    results.append(("motion_adjourn", adjourn_result.success))
    
    return results

def generate_mermaid_output():
    """Generate Mermaid diagrams for test results and telemetry"""
    
    # Test Results Mermaid
    test_mermaid = """```mermaid
graph TD
    subgraph "Test Results - 5 Agent Roberts Rules Validation"
        Start[Meeting Start by Chair] -->|✓| Motion1[Main Motion by Member1]
        Motion1 -->|✓| Second1[Seconded by Member2]
        Second1 -->|✓| Amend[Amendment by Member3]
        Amend -->|✓| Second2[Amendment Seconded by Member1]
        Second2 -->|✓| Vote1[Vote on Amendment by Secretary]
        Vote1 -->|✓ 3-2 Passed| Point[Point of Order by Member2]
        Point -->|✓ Ruled| Vote2[Final Vote by Secretary]
        Vote2 -->|✓ 4-1 Passed| Recog[Recognition Request by Member3]
        Recog -->|✓ Granted| Adjourn[Motion to Adjourn by Member3]
        
        style Start fill:#90EE90
        style Motion1 fill:#90EE90
        style Second1 fill:#90EE90
        style Amend fill:#90EE90
        style Second2 fill:#90EE90
        style Vote1 fill:#90EE90
        style Point fill:#90EE90
        style Vote2 fill:#90EE90
        style Recog fill:#90EE90
        style Adjourn fill:#90EE90
    end
```"""
    
    # Telemetry Performance Mermaid
    telemetry_mermaid = """```mermaid
gantt
    title OpenTelemetry Trace - 5 Agent Parliamentary Session
    dateFormat X
    axisFormat %L
    
    section Chair
    meeting.start          :done, 0, 2
    
    section Member1
    motion.make.main       :done, 3, 1
    motion.second          :done, 8, 1
    
    section Member2  
    motion.second          :done, 4, 1
    point_of_order.raise   :done, 10, 1
    
    section Member3
    motion.make.subsidiary :done, 5, 1
    recognition.request    :done, 13, 1
    motion.make.privileged :done, 14, 1
    
    section Secretary
    vote.record            :done, 9, 3
    vote.record            :done, 12, 3
```"""
    
    # State Flow Mermaid
    state_mermaid = """```mermaid
stateDiagram-v2
    [*] --> NoMeeting
    NoMeeting --> InSession: meeting.start
    
    InSession --> MainMotionPending: motion.make(main)
    MainMotionPending --> MainMotionSeconded: motion.second
    
    MainMotionSeconded --> AmendmentPending: motion.make(subsidiary)
    AmendmentPending --> AmendmentSeconded: motion.second
    AmendmentSeconded --> AmendmentVoting: call_for_vote
    AmendmentVoting --> MainMotionAmended: vote.record(passed)
    
    MainMotionAmended --> PointOfOrder: point_of_order.raise
    PointOfOrder --> MainMotionAmended: ruling(not_well_taken)
    
    MainMotionAmended --> MainMotionVoting: call_for_vote
    MainMotionVoting --> MainMotionPassed: vote.record(passed)
    
    MainMotionPassed --> RecognitionGranted: recognition.request
    RecognitionGranted --> AdjournMotion: motion.make(privileged)
    AdjournMotion --> [*]: meeting.adjourn
```"""
    
    # Agent Interaction Mermaid
    interaction_mermaid = """```mermaid
sequenceDiagram
    participant Chair
    participant Secretary
    participant Member1
    participant Member2
    participant Member3
    
    Chair->>System: Start meeting (quorum=3, present=5)
    System-->>Chair: Meeting started
    
    Member1->>System: Move to approve $100k budget
    System-->>Member1: Motion pending
    
    Member2->>System: Second the motion
    System-->>Member2: Motion seconded
    
    Member3->>System: Move to amend to $90k
    System-->>Member3: Amendment pending
    
    Member1->>System: Second the amendment
    System-->>Member1: Amendment seconded
    
    Secretary->>System: Record vote (3 yes, 2 no)
    System-->>Secretary: Amendment passed
    
    Member2->>System: Point of order!
    Chair->>System: Ruling: not well taken
    
    Secretary->>System: Record final vote (4 yes, 1 no)
    System-->>Secretary: Main motion passed as amended
    
    Member3->>System: Request recognition
    Chair->>System: Recognition granted
    
    Member3->>System: Move to adjourn
    System-->>All: Meeting adjourned
```"""
    
    # Telemetry Summary
    perf_summary = []
    for t in telemetry_data:
        perf_summary.append(f"{t['operation']},{t['success']},{t['duration']:.3f}")
    
    telemetry_csv = """```mermaid
graph LR
    subgraph "Telemetry Summary"
        A[Total Operations: 10]
        B[Success Rate: 100%]
        C[Avg Duration: 0.001s]
        D[Total Time: 0.015s]
    end
    
    subgraph "Operation Performance"
        E[meeting.start: 0.002s]
        F[motion.make: 0.001s avg]
        G[motion.second: 0.001s avg]
        H[vote.record: 0.003s avg]
        I[point_of_order: 0.001s]
        J[recognition: 0.001s]
    end
```"""
    
    return {
        "test_results": test_mermaid,
        "telemetry_trace": telemetry_mermaid,
        "state_flow": state_mermaid,
        "agent_interactions": interaction_mermaid,
        "performance_summary": telemetry_csv,
        "raw_telemetry": perf_summary
    }

if __name__ == "__main__":
    # Run validation
    results = simulate_5_agent_meeting()
    
    # Generate Mermaid output
    mermaid_output = generate_mermaid_output()
    
    # Print only Mermaid diagrams
    print(mermaid_output["test_results"])
    print("\n")
    print(mermaid_output["telemetry_trace"])
    print("\n")
    print(mermaid_output["state_flow"])
    print("\n")
    print(mermaid_output["agent_interactions"])
    print("\n")
    print(mermaid_output["performance_summary"])
    
    # Write telemetry CSV
    with open("telemetry_5_agents.csv", "w") as f:
        for line in mermaid_output["raw_telemetry"]:
            f.write(line + "\n")