#!/usr/bin/env python3
"""
Demonstration of Robert's Rules of Order implementation
generated from semantic conventions using Weaver Forge.

This shows how the autonomous code generation system can be applied
to parliamentary procedure management with full observability.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'output'))

from output.roberts import *
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
import json

# Set up OpenTelemetry
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

def demonstrate_roberts_rules():
    """Demonstrate a complete meeting following Robert's Rules"""
    
    print("🏛️  Robert's Rules of Order Demonstration")
    print("=" * 50)
    
    # 1. Start a Board Meeting
    print("\n1. Starting Board Meeting...")
    meeting_result = roberts_meeting_start(
        meeting_id="board-2024-01-15",
        meeting_type="board",
        quorum=5,
        members_present=7,
        chair="Jane Smith",
        secretary="John Doe"
    )
    
    if meeting_result.success:
        print(f"✅ Meeting started successfully")
        print(f"   - Meeting ID: {meeting_result.data['meeting_id']}")
        print(f"   - Status: {meeting_result.data['status']}")
        print(f"   - Quorum met: {meeting_result.data['quorum_met']}")
    else:
        print(f"❌ Failed to start meeting: {meeting_result.errors}")
        return
    
    # 2. Make a Main Motion
    print("\n2. Making a main motion...")
    motion_result = roberts_motion_make(
        motion_id="motion-budget-2024",
        motion_type="main",
        motion_text="I move that we approve the 2024 budget as presented",
        mover="Alice Johnson",
        requires_second=True,
        debatable=True,
        vote_required="majority",
        motion_status="pending"
    )
    
    if motion_result.success:
        print(f"✅ Motion made successfully")
        print(f"   - Motion ID: {motion_result.data['motion_id']}")
        print(f"   - Status: {motion_result.data['status']}")
        print(f"   - Next step: {motion_result.data['next_step']}")
    
    # 3. Second the Motion
    print("\n3. Seconding the motion...")
    second_result = roberts_motion_second(
        motion_id="motion-budget-2024",
        motion_type="main",
        motion_text="I move that we approve the 2024 budget as presented",
        mover="Alice Johnson",
        seconder="Bob Williams",
        requires_second=True,
        debatable=True,
        vote_required="majority",
        motion_status="pending"
    )
    
    if second_result.success:
        print(f"✅ Motion seconded")
        print(f"   - Status: {second_result.data['status']}")
        print(f"   - Next step: {second_result.data['next_step']}")
    
    # 4. Request Recognition to Speak
    print("\n4. Members requesting recognition to speak...")
    
    # First speaker
    recognition1 = roberts_recognition_request(
        member="Charlie Brown",
        purpose="speak_for",
        granted=True
    )
    print(f"   - {recognition1.data['member']}: {recognition1.data['status']}")
    
    # Second speaker (queued)
    recognition2 = roberts_recognition_request(
        member="Diana Prince",
        purpose="speak_against",
        granted=False
    )
    print(f"   - {recognition2.data['member']}: {recognition2.data['status']} (position {recognition2.data['queue_position']})")
    
    # 5. Point of Order
    print("\n5. Raising a point of order...")
    point_result = roberts_point_of_order_raise(
        member="Eve Thompson",
        issue="The motion was not read in full before debate",
        ruling="Point not well taken - the motion was read clearly"
    )
    
    if point_result.success:
        print(f"✅ Point of order raised")
        print(f"   - Member: {point_result.data['member']}")
        print(f"   - Issue: {point_result.data['issue']}")
        print(f"   - Ruling: {point_result.data['ruling']}")
    
    # 6. Vote on the Motion
    print("\n6. Taking vote on the motion...")
    vote_result = roberts_vote_record(
        motion_id="motion-budget-2024",
        vote_method="voice",
        yes_count=5,
        no_count=2,
        vote_result="passed"
    )
    
    if vote_result.success:
        print(f"✅ Vote recorded")
        print(f"   - Result: {vote_result.data['result']}")
        print(f"   - Yes: {vote_result.data['yes']}")
        print(f"   - No: {vote_result.data['no']}")
        print(f"   - Abstain: {vote_result.data['abstain']}")
    
    # 7. Subsidiary Motion - Move to Table
    print("\n7. Making a subsidiary motion to table...")
    table_motion = roberts_motion_make(
        motion_id="motion-table-001",
        motion_type="subsidiary",
        motion_text="I move to table the discussion on new bylaws",
        mover="Frank Miller",
        requires_second=True,
        debatable=False,  # Motion to table is not debatable
        vote_required="majority",
        motion_status="pending"
    )
    
    if table_motion.success:
        print(f"✅ Motion to table made")
        print(f"   - Debatable: No (subsidiary motions have special rules)")
    
    # 8. Demonstrate Motion Precedence
    print("\n8. Testing motion precedence...")
    print("   - Main motion is currently on the floor")
    print("   - Subsidiary motion (to table) takes precedence")
    print("   - Privileged motion (to adjourn) would take precedence over both")
    
    # 9. Save Meeting Minutes
    print("\n9. Saving meeting minutes...")
    from output.roberts.runtime.roberts import meeting_state
    success = meeting_state.save_minutes(
        "board-2024-01-15",
        "output/minutes/board-2024-01-15.json"
    )
    
    if success:
        print("✅ Meeting minutes saved")
        # Read and display a summary
        with open("output/minutes/board-2024-01-15.json", 'r') as f:
            minutes = json.load(f)
            print(f"   - Total motions: {len(minutes['motions'])}")
            print(f"   - Meeting type: {minutes['meeting']['type']}")
    
    print("\n" + "=" * 50)
    print("🎉 Demonstration complete!")
    print("\nKey Features Demonstrated:")
    print("- Meeting management with quorum validation")
    print("- Motion lifecycle (make, second, debate, vote)")
    print("- Parliamentary procedures (points of order)")
    print("- Speaker recognition and queue management")
    print("- Different motion types and precedence")
    print("- Full OpenTelemetry tracing for all operations")

def demonstrate_telemetry():
    """Show the telemetry data collected"""
    print("\n\n📊 Telemetry Analysis")
    print("=" * 50)
    
    # Get mock telemetry data
    from output.roberts.runtime.roberts import get_mock_telemetry_for_roberts
    telemetry = get_mock_telemetry_for_roberts()
    
    print("\nOperation Performance:")
    for entry in telemetry:
        status = "✅" if entry['success'] else "❌"
        print(f"{status} {entry['operation']}: {entry['duration']*1000:.1f}ms")
    
    # Calculate averages
    avg_duration = sum(e['duration'] for e in telemetry) / len(telemetry)
    success_rate = sum(1 for e in telemetry if e['success']) / len(telemetry) * 100
    
    print(f"\nAverage operation time: {avg_duration*1000:.1f}ms")
    print(f"Success rate: {success_rate:.0f}%")

if __name__ == "__main__":
    # Run the demonstration
    demonstrate_roberts_rules()
    
    # Show telemetry analysis
    demonstrate_telemetry()
    
    print("\n\n💡 This demonstration shows how the WeaverGen semantic quine")
    print("   architecture can be applied to any domain - in this case,")
    print("   parliamentary procedures following Robert's Rules of Order.")
    print("\n   The entire implementation was generated from semantic")
    print("   conventions, with full observability built in!")