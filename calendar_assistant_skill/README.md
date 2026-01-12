# Calendar Assistant Agent Skill

[![Agent Skills](https://img.shields.io/badge/Agent_Skills-v1.0-blue)](https://agentskills.io)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A comprehensive calendar management skill that enables AI agents to create, parse, and manage calendar events using natural language or structured inputs. Fully compliant with the [Agent Skills Python API](https://github.com/agentskills/agentskills) specification.

## 🎯 Overview

This skill transforms natural language scheduling requests into RFC 5545 compliant iCalendar (ICS) files that can be imported into any calendar application.

**Key Features:**
- 🗣️ Natural language event parsing ("Schedule a meeting tomorrow at 2pm")
- 📅 RFC 5545 compliant ICS file generation
- 🌍 Multi-timezone support
- ⏰ Configurable reminders and alarms
- 👥 Attendee and organizer management
- 🔌 Easy integration with AI agents, web apps, and CLI tools

## 📦 Installation

### Option 1: Direct Usage

```bash
# Clone or download this skill directory
cd calendar_assistant_skill

# Install dependencies
pip install -r requirements.txt
```

### Option 2: As a Package

```bash
# Install from the skill directory
pip install -e .
```

### Option 3: Minimal Installation (without AI parsing)

```bash
# Install only core dependencies
pip install icalendar python-dateutil
```

## 🚀 Quick Start

### Natural Language Event Creation

```python
import os
from scripts.calendar_skill import CalendarAssistantSkill

# Initialize skill with API key
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
    with open("meeting.ics", "wb") as f:
        f.write(ics_content)
    print(f"✅ Event created: {parsed_data['summary']}")
else:
    print(f"❌ Error: {error}")
```

### Structured Event Creation

```python
from datetime import datetime, timedelta
import zoneinfo

# Create event with precise control
start_time = datetime.now(zoneinfo.ZoneInfo("UTC")) + timedelta(days=1, hours=14)

ics_content = skill.create_calendar_event(
    summary="Team Meeting",
    start_datetime=start_time,
    duration_hours=2.0,
    description="Quarterly planning discussion",
    location="Conference Room A",
    reminder_hours=1.0
)

with open("meeting.ics", "wb") as f:
    f.write(ics_content)
```

## 📋 Requirements

### Core Dependencies (Required)
- `icalendar >= 5.0.0` - ICS file generation
- `python-dateutil >= 2.8.0` - Date parsing utilities

### Optional Dependencies
- `langchain-nvidia-ai-endpoints >= 0.1.0` - AI-powered natural language parsing
- `langchain-core >= 0.1.0` - LangChain framework support
- `colorama >= 0.4.0` - Enhanced terminal output

## 🔧 Configuration

### Environment Variables

```bash
# Required for natural language parsing (optional feature)
export NVIDIA_API_KEY="your_nvidia_api_key_here"

# Optional: Set default timezone
export DEFAULT_TIMEZONE="America/New_York"
```

### Initialization Options

```python
skill = CalendarAssistantSkill(
    api_key="your_api_key",         # Optional, for AI parsing
    default_timezone="UTC"           # Default: UTC
)
```

## 📖 Usage Examples

### Example 1: Simple Meeting

```python
ics, error, data = skill.natural_language_to_ics(
    "Schedule a team meeting tomorrow at 2pm for 2 hours"
)
```

### Example 2: Appointment with Location

```python
ics, error, data = skill.natural_language_to_ics(
    "Add a dentist appointment on December 5th at 10:30am at Downtown Dental"
)
```

### Example 3: Event with Attendees

```python
from datetime import datetime
import zoneinfo

start = datetime(2026, 1, 15, 14, 0, tzinfo=zoneinfo.ZoneInfo("UTC"))

ics = skill.create_calendar_event(
    summary="Quarterly Review",
    start_datetime=start,
    duration_hours=2.0,
    attendees=[
        {"email": "john@company.com", "name": "John Doe", "role": "REQ-PARTICIPANT"},
        {"email": "jane@company.com", "name": "Jane Smith", "role": "OPT-PARTICIPANT"}
    ],
    organizer_email="manager@company.com",
    organizer_name="Manager Name"
)
```

For more examples, see [examples.md](examples.md).

## 🛠️ Integration

### Web Applications (Gradio)

```python
import gradio as gr

def create_event(user_input):
    ics, error, data = skill.natural_language_to_ics(user_input)
    if error:
        return f"Error: {error}", None
    return f"Event created: {data['summary']}", ics

interface = gr.Interface(
    fn=create_event,
    inputs="text",
    outputs=["text", gr.File(label="Download ICS")]
)
interface.launch()
```

### Command-Line Tool

```bash
# Create a simple CLI wrapper
python -c "
from scripts.calendar_skill import CalendarAssistantSkill
import sys, os

skill = CalendarAssistantSkill(api_key=os.environ.get('NVIDIA_API_KEY'))
ics, err, data = skill.natural_language_to_ics(sys.argv[1])

if not err:
    with open('event.ics', 'wb') as f:
        f.write(ics)
    print('✅ Event created: event.ics')
else:
    print(f'❌ Error: {err}')
" "Meeting tomorrow at 2pm"
```

### AI Agent Integration

```python
# Agent discovers skill via SKILL.md
# Agent reads instructions and examples
# Agent invokes skill based on user intent

def handle_calendar_request(user_message):
    if any(word in user_message.lower() for word in ["schedule", "calendar", "meeting", "appointment"]):
        skill = CalendarAssistantSkill(api_key=api_key)
        ics, error, data = skill.natural_language_to_ics(user_message)
        
        if not error:
            # Save and notify user
            return f"Created event: {data['summary']}", ics
        else:
            return f"Error: {error}", None
```

## 🌍 Timezone Support

The skill uses IANA timezone database for accurate timezone handling:

```python
# Common timezones
skill_utc = CalendarAssistantSkill(default_timezone="UTC")
skill_ny = CalendarAssistantSkill(default_timezone="America/New_York")
skill_paris = CalendarAssistantSkill(default_timezone="Europe/Paris")
skill_tokyo = CalendarAssistantSkill(default_timezone="Asia/Tokyo")
```

Events automatically handle daylight saving time and timezone conversions when imported into calendar applications.

## 📊 Skill Capabilities

Query skill information:

```python
info = skill.get_skill_info()
print(info)
```

Output:
```json
{
  "name": "calendar-assistant",
  "version": "1.0.0",
  "capabilities": [
    "parse_natural_language_to_event",
    "create_ics_calendar_event",
    "manage_event_reminders",
    "handle_multi_timezone_events",
    "export_calendar_files",
    "manage_attendees",
    "create_event_alarms"
  ],
  "status": "initialized",
  "llm_available": true,
  "default_timezone": "UTC"
}
```

## 🧪 Testing

```bash
# Run the example usage script
cd scripts
python calendar_skill.py
```

Expected output:
```
============================================================
Calendar Assistant Skill - Agent Skills API Compliant
============================================================
{
  "name": "calendar-assistant",
  "version": "1.0.0",
  ...
}

=== Example 1: Manual Event Creation ===
✅ Created ICS file (XXX bytes)

=== Example 2: Natural Language Parsing ===
✅ Parsed data: {...}
✅ Created ICS file (XXX bytes)
============================================================
```

## 🏗️ Architecture

```
calendar_assistant_skill/
├── SKILL.md                    # Main skill specification (Agent Skills format)
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── examples.md                 # Detailed usage examples
└── scripts/
    ├── __init__.py            # Package initialization
    └── calendar_skill.py      # Main implementation
```

### File Descriptions

- **SKILL.md**: Agent Skills specification with frontmatter metadata and instructions
- **scripts/calendar_skill.py**: Core implementation with `CalendarAssistantSkill` class
- **examples.md**: Comprehensive examples for various use cases
- **requirements.txt**: Python package dependencies

## 🔒 Security

- API keys should be provided via environment variables
- No code execution from user input
- All text inputs are validated
- RFC 5545 compliant output (safe for calendar imports)
- No script injection in ICS files

## 🤝 Agent Skills Compliance

This skill is fully compliant with the [Agent Skills Python API](https://github.com/agentskills/agentskills) specification:

- ✅ SKILL.md with YAML frontmatter
- ✅ Structured scripts/ directory
- ✅ Comprehensive documentation
- ✅ Clear capability definitions
- ✅ Environment variable configuration
- ✅ Detailed examples
- ✅ Error handling and validation

For more information about Agent Skills, see:
- [Agent Skills Specification](https://agentskills.io)
- [Python API Reference](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- [Deep Dive Article](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions are welcome! This skill follows the Agent Skills format, making it:
- **Reusable**: Use across different AI agent systems
- **Discoverable**: Self-documenting format
- **Composable**: Works with other Agent Skills
- **Maintainable**: Clear structure and conventions

## 🔗 Links

- [Agent Skills Repository](https://github.com/agentskills/agentskills)
- [Agent Skills Documentation](https://agentskills.io)
- [RFC 5545 (iCalendar)](https://datatracker.ietf.org/doc/html/rfc5545)
- [IANA Time Zone Database](https://www.iana.org/time-zones)

## 📞 Support

For issues or questions:
1. Check the [examples.md](examples.md) for common use cases
2. Review the [SKILL.md](SKILL.md) for detailed instructions
3. Consult the [Agent Skills documentation](https://agentskills.io)

---

**Made with ❤️ for the Agent Skills community**

