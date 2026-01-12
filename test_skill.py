#!/usr/bin/env python3
"""
Test script to verify Calendar Assistant Agent Skill
Agent Skills Python API Compliance Check
"""

import os
import sys
from datetime import datetime, timedelta
import zoneinfo

# Add skill to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'calendar_assistant_skill', 'scripts'))

try:
    from calendar_skill import CalendarAssistantSkill, get_skill_metadata
    print("✅ Successfully imported CalendarAssistantSkill from scripts/")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_skill_metadata():
    """Test skill metadata retrieval"""
    print("\n" + "="*60)
    print("TEST 1: Skill Metadata")
    print("="*60)
    
    metadata = get_skill_metadata()
    print(f"✅ Skill Name: {metadata['name']}")
    print(f"✅ Version: {metadata['version']}")
    print(f"✅ Runtime: {metadata['runtime']}")
    print(f"✅ Entry Point: {metadata['entry_point']}")

def test_skill_initialization():
    """Test skill initialization"""
    print("\n" + "="*60)
    print("TEST 2: Skill Initialization")
    print("="*60)
    
    api_key = os.environ.get('NVIDIA_API_KEY')
    skill = CalendarAssistantSkill(api_key=api_key, default_timezone='UTC')
    
    info = skill.get_skill_info()
    print(f"✅ Skill initialized: {info['name']} v{info['version']}")
    print(f"✅ Status: {info['status']}")
    print(f"✅ Timezone: {info['default_timezone']}")
    print(f"✅ AI Available: {info['llm_available']}")
    print(f"✅ Capabilities: {len(info['capabilities'])} capabilities")
    
    return skill

def test_manual_event_creation(skill):
    """Test manual event creation"""
    print("\n" + "="*60)
    print("TEST 3: Manual Event Creation")
    print("="*60)
    
    start_time = datetime.now(zoneinfo.ZoneInfo("UTC")) + timedelta(days=1, hours=14)
    
    try:
        ics_content = skill.create_calendar_event(
            summary="Test Meeting",
            start_datetime=start_time,
            duration_hours=1.0,
            description="This is a test event",
            location="Test Location",
            reminder_hours=1.0
        )
        
        print(f"✅ ICS file generated: {len(ics_content)} bytes")
        
        # Save test file
        with open("test_event.ics", "wb") as f:
            f.write(ics_content)
        print("✅ Test event saved to: test_event.ics")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_natural_language_parsing(skill):
    """Test natural language parsing (requires API key)"""
    print("\n" + "="*60)
    print("TEST 4: Natural Language Parsing")
    print("="*60)
    
    if not skill.llm:
        print("⚠️  Skipped: No API key available for AI parsing")
        print("   Set NVIDIA_API_KEY environment variable to test this feature")
        return None
    
    test_input = "Schedule a team meeting tomorrow at 2pm for 2 hours"
    print(f"Input: '{test_input}'")
    
    try:
        ics_content, error, parsed_data = skill.natural_language_to_ics(test_input)
        
        if error:
            print(f"❌ Error: {error}")
            return False
        
        print("✅ Successfully parsed natural language input")
        print(f"   Summary: {parsed_data['summary']}")
        print(f"   Date: {parsed_data['start_date']}")
        print(f"   Time: {parsed_data['start_time']}")
        print(f"   Duration: {parsed_data['duration_hours']} hours")
        
        # Save test file
        with open("test_nl_event.ics", "wb") as f:
            f.write(ics_content)
        print("✅ Natural language event saved to: test_nl_event.ics")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_agent_skills_compliance():
    """Verify Agent Skills API compliance"""
    print("\n" + "="*60)
    print("TEST 5: Agent Skills API Compliance")
    print("="*60)
    
    import os
    skill_dir = os.path.join(os.path.dirname(__file__), 'calendar_assistant_skill')
    
    required_files = {
        'SKILL.md': 'Main skill specification with frontmatter',
        'README.md': 'User-facing documentation',
        'requirements.txt': 'Python dependencies',
        'examples.md': 'Usage examples',
        'scripts/calendar_skill.py': 'Main implementation',
        'scripts/__init__.py': 'Python package marker'
    }
    
    all_present = True
    for file, description in required_files.items():
        file_path = os.path.join(skill_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file}: {description}")
        else:
            print(f"❌ {file}: MISSING")
            all_present = False
    
    if all_present:
        print("\n✅ All required Agent Skills files are present")
    else:
        print("\n❌ Some required files are missing")
    
    return all_present

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CALENDAR ASSISTANT AGENT SKILL - VERIFICATION TEST")
    print("Agent Skills Python API Compliance Check")
    print("="*60)
    
    results = []
    
    # Test 1: Metadata
    try:
        test_skill_metadata()
        results.append(("Metadata", True))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Metadata", False))
    
    # Test 2 & 3: Initialization and Manual Creation
    try:
        skill = test_skill_initialization()
        results.append(("Initialization", True))
        
        manual_result = test_manual_event_creation(skill)
        results.append(("Manual Event Creation", manual_result))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Initialization", False))
        results.append(("Manual Event Creation", False))
        skill = None
    
    # Test 4: Natural Language (optional)
    if skill:
        try:
            nl_result = test_natural_language_parsing(skill)
            if nl_result is not None:
                results.append(("Natural Language Parsing", nl_result))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(("Natural Language Parsing", False))
    
    # Test 5: Compliance
    try:
        compliance_result = test_agent_skills_compliance()
        results.append(("Agent Skills Compliance", compliance_result))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        results.append(("Agent Skills Compliance", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Skill is Agent Skills API compliant.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

