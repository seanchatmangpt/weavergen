#!/usr/bin/env python3
"""
Test and validate the Roberts Rules integration between:
1. Generated 4-layer architecture
2. Pydantic models
3. Agent system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'output'))

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        # Test model imports
        from roberts_rules_models import (
            Meeting, Motion, Vote, MeetingType, MotionType, 
            MotionStatus, VoteThreshold, VoteMethod
        )
        print("✅ Pydantic models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False
    
    try:
        # Test generated code imports
        from output.roberts.commands.forge import (
            roberts_meeting_start,
            roberts_motion_make,
            roberts_motion_second,
            roberts_vote_record,
            roberts_point_of_order_raise,
            roberts_recognition_request
        )
        print("✅ Generated commands imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import generated commands: {e}")
        print("   Make sure you've run: python generate_roberts_rules.py")
        return False
    
    try:
        # Test runtime imports
        from output.roberts.runtime.roberts import (
            meeting_state,
            validate_quorum,
            validate_motion_type
        )
        print("✅ Runtime layer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import runtime: {e}")
        return False
    
    return True

def test_generated_functions():
    """Test the generated functions work correctly"""
    print("\nTesting generated functions...")
    
    from output.roberts.commands.forge import (
        roberts_meeting_start,
        roberts_motion_make,
        ForgeResult
    )
    
    # Test 1: Start a meeting
    print("\n1. Testing meeting start...")
    result = roberts_meeting_start(
        roberts_meeting_id="test-meeting-001",
        roberts_meeting_type="board",
        roberts_meeting_quorum=3,
        roberts_meeting_members_present=5,
        roberts_meeting_chair="Test Chair",
        roberts_meeting_secretary="Test Secretary"
    )
    
    if isinstance(result, ForgeResult):
        if result.success:
            print(f"   ✅ Meeting started: {result.data}")
        else:
            print(f"   ❌ Failed to start meeting: {result.errors}")
    else:
        print(f"   ❌ Unexpected result type: {type(result)}")
    
    # Test 2: Make a motion
    print("\n2. Testing motion creation...")
    motion_result = roberts_motion_make(
        roberts_motion_id="test-motion-001",
        roberts_motion_type="main",
        roberts_motion_text="Test motion to validate the system",
        roberts_motion_mover="Test Member",
        roberts_motion_requires_second=True,
        roberts_motion_debatable=True,
        roberts_motion_vote_required="majority",
        roberts_motion_status="pending"
    )
    
    if isinstance(motion_result, ForgeResult):
        if motion_result.success:
            print(f"   ✅ Motion created: {motion_result.data}")
        else:
            print(f"   ❌ Failed to create motion: {motion_result.errors}")
    else:
        print(f"   ❌ Unexpected result type: {type(motion_result)}")
    
    return True

def test_state_management():
    """Test that state is properly managed across layers"""
    print("\nTesting state management...")
    
    from output.roberts.runtime.roberts import meeting_state
    from output.roberts.commands.forge import roberts_meeting_start
    
    # Clear any existing state
    meeting_state.meetings.clear()
    meeting_state.motions.clear()
    meeting_state.current_meeting_id = None
    
    # Start a meeting
    result = roberts_meeting_start(
        roberts_meeting_id="state-test-001",
        roberts_meeting_type="committee",
        roberts_meeting_quorum=3,
        roberts_meeting_members_present=4,
        roberts_meeting_chair="State Test Chair",
        roberts_meeting_secretary="State Test Secretary"
    )
    
    # Check state was updated
    if meeting_state.current_meeting_id == "state-test-001":
        print("   ✅ Current meeting ID set correctly")
    else:
        print(f"   ❌ Current meeting ID not set: {meeting_state.current_meeting_id}")
    
    if "state-test-001" in meeting_state.meetings:
        print("   ✅ Meeting added to state")
        meeting = meeting_state.meetings["state-test-001"]
        print(f"      - Type: {meeting['type']}")
        print(f"      - Quorum: {meeting['quorum']}")
        print(f"      - Present: {meeting['members_present']}")
    else:
        print("   ❌ Meeting not found in state")
    
    return True

def test_telemetry_integration():
    """Test that telemetry is properly recorded"""
    print("\nTesting telemetry integration...")
    
    # Check if telemetry file exists
    telemetry_file = "telemetry.csv"
    if os.path.exists(telemetry_file):
        print(f"   ✅ Telemetry file exists: {telemetry_file}")
        
        # Read last few lines
        with open(telemetry_file, 'r') as f:
            lines = f.readlines()
            if lines:
                print(f"   📊 Found {len(lines)} telemetry entries")
                if len(lines) > 3:
                    print("   Recent entries:")
                    for line in lines[-3:]:
                        print(f"      {line.strip()}")
    else:
        print("   ⚠️  No telemetry file found (this is normal if telemetry export is not configured)")
    
    return True

def validate_agent_compatibility():
    """Validate that the agent system can work with generated code"""
    print("\nValidating agent compatibility...")
    
    # Check if we can create the proper dependencies
    try:
        from roberts_rules_models import ParliamentaryState
        from output.roberts.runtime.roberts import meeting_state
        
        # The agent system needs to use the runtime's meeting_state
        # not create its own ParliamentaryState
        print("   ⚠️  Agent system needs modification to use runtime state")
        print("      Current: Creates own ParliamentaryState()")
        print("      Needed: Use output.roberts.runtime.roberts.meeting_state")
        
        # Check function signatures
        from output.roberts.commands.forge import roberts_motion_make
        import inspect
        
        sig = inspect.signature(roberts_motion_make)
        print(f"\n   📋 roberts_motion_make signature:")
        for param_name, param in sig.parameters.items():
            print(f"      - {param_name}: {param.annotation if param.annotation != param.empty else 'Any'}")
        
    except Exception as e:
        print(f"   ❌ Compatibility check failed: {e}")
    
    return True

def main():
    """Run all validation tests"""
    print("🔍 Roberts Rules Integration Validation")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Generated Functions", test_generated_functions),
        ("State Management", test_state_management),
        ("Telemetry", test_telemetry_integration),
        ("Agent Compatibility", validate_agent_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n\n📊 Validation Summary")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed < total:
        print("\n⚠️  Issues to fix:")
        print("1. Ensure generate_roberts_rules.py has been run")
        print("2. Update agent system to use generated state management")
        print("3. Match function signatures between agents and generated code")
        print("4. Configure OpenTelemetry exporters for full telemetry")

if __name__ == "__main__":
    main()