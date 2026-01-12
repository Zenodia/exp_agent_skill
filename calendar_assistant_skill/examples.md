# Calendar Assistant Skill - Examples

This document provides practical examples of using the Calendar Assistant Agent Skill in various scenarios.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Natural Language Parsing](#natural-language-parsing)
- [Structured Event Creation](#structured-event-creation)
- [Advanced Features](#advanced-features)
- [Integration Examples](#integration-examples)
- [Error Handling](#error-handling)

---

## Basic Usage

### Example 1: Simple Meeting

**User Input:**
```
"Schedule a team meeting tomorrow at 2pm for 2 hours"
```

**Code:**
```python
import os
from scripts.calendar_skill import CalendarAssistantSkill

# Initialize skill
skill = CalendarAssistantSkill(
    api_key=os.environ.get('NVIDIA_API_KEY'),
    default_timezone='UTC'
)

# Create event from natural language
ics_content, error, parsed_data = skill.natural_language_to_ics(
    "Schedule a team meeting tomorrow at 2pm for 2 hours"
)

if not error:
    # Save ICS file
    with open("team_meeting.ics", "wb") as f:
        f.write(ics_content)
    print(f"✅ Event created: {parsed_data['summary']}")
    print(f"   Start: {parsed_data['start_date']} {parsed_data['start_time']}")
    print(f"   Duration: {parsed_data['duration_hours']} hours")
else:
    print(f"❌ Error: {error}")
```

**Expected Output:**
```json
{
  "summary": "Team Meeting",
  "description": "",
  "start_date": "2026-01-13",
  "start_time": "14:00",
  "duration_hours": 2.0,
  "location": "",
  "reminder_hours": 1
}
```

---

### Example 2: Appointment with Location

**User Input:**
```
"Add a dentist appointment on December 5th at 10:30am at Downtown Dental"
```

**Code:**
```python
ics_content, error, parsed_data = skill.natural_language_to_ics(
    "Add a dentist appointment on December 5th at 10:30am at Downtown Dental"
)

if not error:
    with open("dentist_appointment.ics", "wb") as f:
        f.write(ics_content)
    print(f"✅ Appointment created at {parsed_data['location']}")
```

**Expected Parsed Data:**
```json
{
  "summary": "Dentist Appointment",
  "description": "",
  "start_date": "2026-12-05",
  "start_time": "10:30",
  "duration_hours": 1.0,
  "location": "Downtown Dental",
  "reminder_hours": 1
}
```

---

### Example 3: Project Deadline

**User Input:**
```
"Create a project deadline for next Friday at 5pm"
```

**Code:**
```python
ics_content, error, parsed_data = skill.natural_language_to_ics(
    "Create a project deadline for next Friday at 5pm"
)

if not error:
    with open("project_deadline.ics", "wb") as f:
        f.write(ics_content)
    print(f"✅ Deadline set for {parsed_data['start_date']}")
```

---

## Natural Language Parsing

### Example 4: Relative Dates

The skill understands various relative date expressions:

```python
test_inputs = [
    "Meeting tomorrow at 9am",
    "Conference next Monday at 2pm",
    "Review session in 3 days at noon",
    "Presentation this Friday at 3:30pm",
    "Workshop next week Wednesday at 10am"
]

for user_input in test_inputs:
    ics_content, error, parsed_data = skill.natural_language_to_ics(user_input)
    if not error:
        print(f"✅ {user_input}")
        print(f"   → {parsed_data['start_date']} at {parsed_data['start_time']}")
    else:
        print(f"❌ {user_input}: {error}")
```

### Example 5: Duration Expressions

```python
test_durations = [
    "Meeting for 30 minutes",
    "Conference for 3 hours",
    "Workshop for 90 minutes",
    "All-day event",
]

for user_input in test_durations:
    ics_content, error, parsed_data = skill.natural_language_to_ics(
        f"{user_input} tomorrow at 10am"
    )
    if not error:
        print(f"✅ Duration: {parsed_data['duration_hours']} hours")
```

---

## Structured Event Creation

### Example 6: Manual Event with All Details

```python
from datetime import datetime, timedelta
import zoneinfo

# Create precise event
start_time = datetime(2026, 1, 15, 14, 30, tzinfo=zoneinfo.ZoneInfo("America/New_York"))

ics_content = skill.create_calendar_event(
    summary="Quarterly Business Review",
    start_datetime=start_time,
    duration_hours=2.5,
    description="Q4 2025 performance review and Q1 2026 planning",
    location="Executive Conference Room",
    organizer_email="ceo@company.com",
    organizer_name="CEO Name",
    attendees=[
        {"email": "cfo@company.com", "name": "CFO Name", "role": "REQ-PARTICIPANT"},
        {"email": "cto@company.com", "name": "CTO Name", "role": "REQ-PARTICIPANT"},
        {"email": "vp@company.com", "name": "VP Name", "role": "OPT-PARTICIPANT"}
    ],
    reminder_hours=24  # 1 day before
)

with open("quarterly_review.ics", "wb") as f:
    f.write(ics_content)
print("✅ Detailed event created with attendees")
```

### Example 7: Multiple Events

```python
events = [
    {
        "summary": "Daily Standup",
        "start": datetime.now(zoneinfo.ZoneInfo("UTC")) + timedelta(days=1, hours=9),
        "duration": 0.25,  # 15 minutes
    },
    {
        "summary": "Sprint Planning",
        "start": datetime.now(zoneinfo.ZoneInfo("UTC")) + timedelta(days=1, hours=10),
        "duration": 2.0,
    },
    {
        "summary": "Client Demo",
        "start": datetime.now(zoneinfo.ZoneInfo("UTC")) + timedelta(days=1, hours=14),
        "duration": 1.0,
    }
]

for event in events:
    ics_content = skill.create_calendar_event(
        summary=event["summary"],
        start_datetime=event["start"],
        duration_hours=event["duration"]
    )
    filename = f"{event['summary'].lower().replace(' ', '_')}.ics"
    with open(filename, "wb") as f:
        f.write(ics_content)
    print(f"✅ Created {filename}")
```

---

## Advanced Features

### Example 8: Timezone Handling

```python
from datetime import datetime
import zoneinfo

# Different timezones for different users
timezones = ["UTC", "America/New_York", "Europe/Paris", "Asia/Tokyo"]

for tz in timezones:
    skill_local = CalendarAssistantSkill(default_timezone=tz)
    
    # Event at 2pm local time in each timezone
    start = datetime.now(zoneinfo.ZoneInfo(tz)) + timedelta(days=1, hours=14)
    
    ics_content = skill_local.create_calendar_event(
        summary=f"Global Team Meeting ({tz})",
        start_datetime=start,
        duration_hours=1.0
    )
    
    with open(f"meeting_{tz.replace('/', '_')}.ics", "wb") as f:
        f.write(ics_content)
    print(f"✅ Created event for {tz}")
```

### Example 9: Custom Reminders

```python
# Different reminder times for different event types
reminder_configs = {
    "urgent_meeting": 0.5,      # 30 minutes before
    "regular_meeting": 1.0,     # 1 hour before
    "important_deadline": 24.0,  # 1 day before
    "project_milestone": 72.0    # 3 days before
}

for event_type, reminder_hours in reminder_configs.items():
    start = datetime.now(zoneinfo.ZoneInfo("UTC")) + timedelta(days=7)
    
    ics_content = skill.create_calendar_event(
        summary=f"{event_type.replace('_', ' ').title()}",
        start_datetime=start,
        duration_hours=1.0,
        reminder_hours=reminder_hours
    )
    
    print(f"✅ {event_type}: {reminder_hours}h reminder")
```

---

## Integration Examples

### Example 10: Web Application (Gradio)

```python
import gradio as gr
from scripts.calendar_skill import CalendarAssistantSkill
import os

skill = CalendarAssistantSkill(
    api_key=os.environ.get('NVIDIA_API_KEY'),
    default_timezone='UTC'
)

def create_event_from_text(user_input):
    """Handler for Gradio interface"""
    ics_content, error, parsed_data = skill.natural_language_to_ics(user_input)
    
    if error:
        return f"❌ Error: {error}", None
    
    # Save to temp file
    filename = "event.ics"
    with open(filename, "wb") as f:
        f.write(ics_content)
    
    summary = f"""
✅ Event Created Successfully!

📅 {parsed_data['summary']}
🕐 {parsed_data['start_date']} at {parsed_data['start_time']}
⏱️  Duration: {parsed_data['duration_hours']} hour(s)
📍 Location: {parsed_data.get('location', 'Not specified')}
🔔 Reminder: {parsed_data.get('reminder_hours', 1)} hour(s) before
"""
    
    return summary, filename

# Create Gradio interface
interface = gr.Interface(
    fn=create_event_from_text,
    inputs=gr.Textbox(
        lines=3,
        placeholder="Describe your event in natural language...",
        label="Event Description"
    ),
    outputs=[
        gr.Textbox(label="Result"),
        gr.File(label="Download ICS File")
    ],
    title="📅 Calendar Assistant",
    description="Create calendar events from natural language!",
    examples=[
        ["Schedule a team meeting tomorrow at 2pm for 2 hours"],
        ["Add dentist appointment next Monday at 10:30am"],
        ["Create project deadline for Friday at 5pm"]
    ]
)

if __name__ == "__main__":
    interface.launch()
```

### Example 11: Command-Line Tool

```python
#!/usr/bin/env python3
"""
calendar_cli.py - Command-line calendar event creator
Usage: python calendar_cli.py "Schedule meeting tomorrow at 2pm"
"""

import sys
import os
from scripts.calendar_skill import CalendarAssistantSkill

def main():
    if len(sys.argv) < 2:
        print("Usage: python calendar_cli.py \"<event description>\"")
        print("\nExamples:")
        print("  python calendar_cli.py \"Meeting tomorrow at 2pm\"")
        print("  python calendar_cli.py \"Dentist appointment next Monday at 10am\"")
        sys.exit(1)
    
    # Initialize skill
    api_key = os.environ.get('NVIDIA_API_KEY')
    if not api_key:
        print("⚠️  Warning: NVIDIA_API_KEY not set. AI parsing may not work.")
    
    skill = CalendarAssistantSkill(api_key=api_key, default_timezone='UTC')
    
    # Get user input
    user_input = sys.argv[1]
    print(f"Creating event: {user_input}")
    
    # Create event
    ics_content, error, parsed_data = skill.natural_language_to_ics(user_input)
    
    if error:
        print(f"❌ Error: {error}")
        sys.exit(1)
    
    # Save ICS file
    filename = "event.ics"
    with open(filename, "wb") as f:
        f.write(ics_content)
    
    print(f"✅ Event created successfully!")
    print(f"   Title: {parsed_data['summary']}")
    print(f"   Date: {parsed_data['start_date']}")
    print(f"   Time: {parsed_data['start_time']}")
    print(f"   Duration: {parsed_data['duration_hours']} hour(s)")
    print(f"   File: {filename}")

if __name__ == "__main__":
    main()
```

### Example 12: Jupyter Notebook

```python
# Cell 1: Setup
from scripts.calendar_skill import CalendarAssistantSkill
from IPython.display import FileLink, display
import os

skill = CalendarAssistantSkill(
    api_key=os.environ.get('NVIDIA_API_KEY'),
    default_timezone='America/New_York'
)

print("✅ Calendar Assistant Skill loaded")
print(skill.get_skill_info())

# Cell 2: Interactive creation
user_input = input("Describe your event: ")

ics_content, error, parsed_data = skill.natural_language_to_ics(user_input)

if not error:
    # Display parsed data
    print("📋 Parsed Event Data:")
    for key, value in parsed_data.items():
        print(f"  {key}: {value}")
    
    # Save and provide download link
    filename = "notebook_event.ics"
    with open(filename, "wb") as f:
        f.write(ics_content)
    
    print("\n✅ Event created! Click below to download:")
    display(FileLink(filename))
else:
    print(f"❌ Error: {error}")

# Cell 3: Batch creation
events = [
    "Morning standup tomorrow at 9am for 15 minutes",
    "Lunch meeting next week Wednesday at noon for 1 hour",
    "Project review Friday at 3pm for 2 hours"
]

for event_desc in events:
    ics, err, data = skill.natural_language_to_ics(event_desc)
    if not err:
        print(f"✅ {data['summary']}")
    else:
        print(f"❌ Failed: {event_desc}")
```

---

## Error Handling

### Example 13: Graceful Error Handling

```python
def safe_create_event(user_input, skill):
    """Create event with comprehensive error handling"""
    try:
        ics_content, error, parsed_data = skill.natural_language_to_ics(user_input)
        
        if error:
            # Handle parsing errors
            if "LLM not initialized" in error:
                print("❌ AI parsing unavailable. Please provide API key.")
                print("💡 Try using structured input instead.")
                return None
            elif "Error parsing" in error:
                print(f"❌ Could not understand: {user_input}")
                print("💡 Try being more specific with dates and times.")
                return None
            else:
                print(f"❌ Error: {error}")
                return None
        
        # Success
        filename = f"event_{parsed_data['start_date']}.ics"
        with open(filename, "wb") as f:
            f.write(ics_content)
        
        print(f"✅ Event created: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

# Test with various inputs
test_cases = [
    "Meeting tomorrow at 2pm",
    "Some ambiguous event sometime",
    "Conference on 32nd of January",  # Invalid date
]

for test_input in test_cases:
    print(f"\nTesting: {test_input}")
    safe_create_event(test_input, skill)
```

### Example 14: Fallback to Manual Entry

```python
def create_event_with_fallback(user_input, skill):
    """Try AI parsing, fall back to manual entry if needed"""
    
    # Try natural language parsing
    ics_content, error, parsed_data = skill.natural_language_to_ics(user_input)
    
    if not error:
        # Success with AI
        return ics_content, parsed_data
    
    # Fallback: Manual entry
    print("⚠️  AI parsing failed. Let's create the event manually.")
    
    # Prompt for details
    summary = input("Event title: ")
    date_str = input("Date (YYYY-MM-DD): ")
    time_str = input("Time (HH:MM): ")
    duration = float(input("Duration (hours): "))
    
    # Parse manually
    from datetime import datetime
    import zoneinfo
    
    start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    start_dt = start_dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
    
    # Create event
    ics_content = skill.create_calendar_event(
        summary=summary,
        start_datetime=start_dt,
        duration_hours=duration
    )
    
    parsed_data = {
        "summary": summary,
        "start_date": date_str,
        "start_time": time_str,
        "duration_hours": duration
    }
    
    return ics_content, parsed_data
```

### Example 15: Validation

```python
def validate_and_create_event(user_input, skill):
    """Create event with validation"""
    
    ics_content, error, parsed_data = skill.natural_language_to_ics(user_input)
    
    if error:
        return False, error
    
    # Validate parsed data
    print("📋 Event Details:")
    print(f"   Title: {parsed_data['summary']}")
    print(f"   Date: {parsed_data['start_date']}")
    print(f"   Time: {parsed_data['start_time']}")
    print(f"   Duration: {parsed_data['duration_hours']} hour(s)")
    
    # Ask for confirmation
    confirm = input("\n✅ Proceed with creating this event? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        filename = "confirmed_event.ics"
        with open(filename, "wb") as f:
            f.write(ics_content)
        return True, f"Event saved to {filename}"
    else:
        return False, "Event creation cancelled by user"

# Use with validation
success, message = validate_and_create_event(
    "Important meeting tomorrow at 3pm for 2 hours",
    skill
)
print(message)
```

---

## Best Practices

### Example 16: Skill Information Query

```python
# Check skill capabilities before use
info = skill.get_skill_info()

print("📊 Skill Information:")
print(f"   Name: {info['name']}")
print(f"   Version: {info['version']}")
print(f"   Status: {info['status']}")
print(f"   AI Available: {info['llm_available']}")
print(f"   Timezone: {info['default_timezone']}")
print(f"\n🛠️  Capabilities:")
for cap in info['capabilities']:
    print(f"   - {cap}")
```

---

## Summary

This examples document covers:

1. ✅ **Basic natural language event creation**
2. ✅ **Structured event creation with full control**
3. ✅ **Timezone handling across regions**
4. ✅ **Integration with web apps, CLI, and notebooks**
5. ✅ **Comprehensive error handling**
6. ✅ **Validation and confirmation workflows**

For more details, see the main SKILL.md documentation.

