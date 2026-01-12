"""
Gradio-based Enhanced Calendar Creator with Agent Skill Integration
Demonstrates the Calendar Assistant Agent Skill in a web interface
"""

import gradio as gr
from datetime import datetime, timedelta
import zoneinfo
import json
import os
import tempfile
import sys

# Import the Calendar Assistant Agent Skill (Agent Skills API compliant)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'calendar_assistant_skill', 'scripts'))
from calendar_skill import CalendarAssistantSkill

# ===========================
# Initialize Agent Skill
# ===========================

# Get API key from environment
api_key = os.environ.get('NVIDIA_API_KEY')
calendar_skill = CalendarAssistantSkill(
    api_key=api_key,
    default_timezone="Europe/Paris"  # UTC+1
)

print("🤖 Calendar Assistant Agent Skill Loaded")
print(json.dumps(calendar_skill.get_skill_info(), indent=2))

# ===========================
# Gradio Interface Functions (Using Agent Skill)
# ===========================

def create_event_manual(date_value, time_str, duration, title, location, 
                       description, organizer_name, organizer_email, reminder_hours):
    """Create event from manual input using Agent Skill"""
    
    if not title:
        return None, "❌ Please provide an event title", ""
    
    if not date_value:
        return None, "❌ Please select a date", ""
    
    try:
        # Parse datetime
        if 'T' in date_value:
            dt = datetime.fromisoformat(date_value.replace('Z', '+01:00'))
        else:
            dt = datetime.strptime(date_value, '%Y-%m-%d')
        
        if time_str and ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
            dt = dt.replace(hour=hour, minute=minute)
        
        # Add timezone
        dt = dt.replace(tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
        
        # Use Agent Skill to create event
        ics_content = calendar_skill.create_calendar_event(
            summary=title,
            start_datetime=dt,
            duration_hours=float(duration),
            description=description,
            location=location,
            organizer_email=organizer_email,
            organizer_name=organizer_name,
            reminder_hours=float(reminder_hours)
        )
        
        # Save to temp file
        event_name_safe = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"event_{event_name_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
        temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.ics', prefix='')
        temp_file.write(ics_content)
        temp_file.close()
        
        success_msg = f"""
✅ **Event Created Successfully via Agent Skill!**

🤖 **Powered by:** Calendar Assistant Agent Skill v1.0.0

📅 **Event Details:**
- **Title:** {title}
- **Date & Time:** {dt.strftime('%Y-%m-%d %H:%M')} (UTC+1)
- **Duration:** {duration} hours
- **Location:** {location if location else 'Not specified'}
- **Description:** {description if description else 'Not specified'}

📥 **How to Add to Your Calendar:**

**Option 1 - Double-click (Easiest):**
1. Click the **Download** button below
2. Find the downloaded `.ics` file
3. **Double-click** the file - it will open in your calendar app!

**Option 2 - Right-click:**
1. Right-click the downloaded `.ics` file
2. Select **"Open with"** → Choose Outlook or your calendar app

💡 **File:** `{filename}`
"""
        
        preview = ics_content.decode('utf-8')
        return temp_file.name, success_msg, preview
        
    except Exception as e:
        return None, f"❌ Error creating event: {str(e)}", ""


def create_event_with_ai(ai_input):
    """Create event using Agent Skill's natural language parsing"""
    
    if not ai_input:
        return None, "❌ Please describe the event you want to create", ""
    
    if not calendar_skill.llm:
        return None, "❌ NVIDIA_API_KEY not found. Agent Skill requires API key for natural language parsing.", ""
    
    try:
        # Use Agent Skill's complete pipeline
        ics_content, error, parsed_data = calendar_skill.natural_language_to_ics(ai_input)
        
        if error:
            return None, f"❌ {error}", ""
        
        # Save to temp file
        event_name_safe = "".join(c for c in parsed_data['summary'] if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"event_{event_name_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
        temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.ics', prefix='')
        temp_file.write(ics_content)
        temp_file.close()
        
        # Parse datetime for display
        start_dt = datetime.strptime(parsed_data['start_date'], '%Y-%m-%d')
        if parsed_data.get('start_time'):
            hour, minute = map(int, parsed_data['start_time'].split(':'))
            start_dt = start_dt.replace(hour=hour, minute=minute)
        start_dt = start_dt.replace(tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
        
        success_msg = f"""
✅ **Event Parsed and Created Successfully!**

🤖 **Powered by:** Calendar Assistant Agent Skill v1.0.0
📡 **AI Model:** NVIDIA Llama 3.1 405B Instruct

🧠 **AI Interpretation:**
```json
{json.dumps(parsed_data, indent=2)}
```

📅 **Event Details:**
- **Title:** {parsed_data['summary']}
- **Date & Time:** {start_dt.strftime('%Y-%m-%d %H:%M')} (UTC+1)
- **Duration:** {parsed_data['duration_hours']} hours
- **Location:** {parsed_data.get('location', 'Not specified')}
- **Description:** {parsed_data.get('description', 'Not specified')}
- **Reminder:** {parsed_data.get('reminder_hours', 1)} hours before

📥 **How to Add to Your Calendar:**

**Option 1 - Double-click (Easiest):**
1. Click the **Download** button below
2. Find the downloaded `.ics` file
3. **Double-click** the file - opens automatically!

**Option 2 - Import manually:**
- **Outlook:** File → Open & Export → Import iCalendar
- **Google Calendar:** Settings → Import & Export
- **Apple Calendar:** File → Import

💡 **File:** `{filename}`

---
🎯 **Agent Skill Benefits:**
- Intelligent date/time parsing
- Context-aware interpretation
- RFC 5545 compliant output
- Reusable across agent systems
"""
        
        preview = ics_content.decode('utf-8')
        return temp_file.name, success_msg, preview
        
    except Exception as e:
        return None, f"❌ Error creating event with AI: {str(e)}", ""


def show_skill_info():
    """Display Agent Skill information"""
    info = calendar_skill.get_skill_info()
    
    capabilities_list = "\n".join([f"  • {cap}" for cap in info['capabilities']])
    
    return f"""
## 🤖 Agent Skill Information

**Skill Name:** {info['name']}  
**Version:** {info['version']}  
**Status:** {info['status']}  
**LLM Available:** {'✅ Yes' if info['llm_available'] else '❌ No (API key required)'}  
**Default Timezone:** {info['default_timezone']}

### Capabilities:
{capabilities_list}

### What is an Agent Skill?

Agent Skills are modular, reusable capabilities that AI agents can discover and use. 
This Calendar Assistant Skill follows the Agent Skills specification from Anthropic,
making it:

- **Portable:** Works across different agent systems
- **Discoverable:** Self-documenting with instructions and examples
- **Composable:** Can be combined with other skills
- **Maintainable:** Single source of truth for calendar functionality

### Benefits of Agent Skills:

1. **Write Once, Use Everywhere:** This skill can be integrated into any agent framework
2. **Consistent Behavior:** Same calendar logic across all integrations
3. **Easy Updates:** Update the skill once, all integrations benefit
4. **Clear Documentation:** Instructions and examples built-in
5. **Testable:** Isolated functionality for better testing

### Files in This Skill:

- `skill.json` - Metadata and dependencies
- `calendar_skill.py` - Core implementation
- `instructions.txt` - Agent usage instructions
- `examples.json` - Test cases and examples
- `README.txt` - Human documentation

This Gradio app is a demonstration of the skill in action!
"""


# ===========================
# Gradio Interface
# ===========================

def create_gradio_interface():
    """Create the Gradio web interface with Agent Skill integration"""
    
    with gr.Blocks(title="Calendar Assistant Agent Skill Demo", theme=gr.themes.Soft()) as app:
        
        gr.Markdown("""
        # 🤖 Calendar Assistant Agent Skill Demo
        
        **Powered by Agent Skills** - A modular, reusable AI capability for calendar management
        
        Create calendar events using the Calendar Assistant Agent Skill, demonstrating
        how Agent Skills can be integrated into web applications.
        """)
        
        with gr.Tabs() as tabs:
            
            # ===========================
            # Agent Skill Info Tab
            # ===========================
            
            with gr.Tab("🤖 Agent Skill Info"):
                gr.Markdown(show_skill_info())
                
                gr.Markdown("""
                ---
                ### Try the Skill:
                
                Use the tabs above to:
                - **Manual Entry:** Create events with form inputs
                - **AI Assistant:** Use natural language parsing
                
                Both modes use the same underlying Agent Skill!
                """)
            
            # ===========================
            # Manual Entry Tab
            # ===========================
            
            with gr.Tab("📝 Manual Entry"):
                gr.Markdown("""
                ### Create events using visual controls
                
                This tab uses the Agent Skill's `create_calendar_event()` method directly.
                """)
                
                with gr.Row():
                    with gr.Column(scale=2):
                        manual_title = gr.Textbox(
                            label="Event Title *",
                            placeholder="e.g., Team Meeting, Doctor Appointment",
                            lines=1
                        )
                        
                        with gr.Row():
                            manual_date = gr.Textbox(
                                label="📅 Date (YYYY-MM-DD) *",
                                placeholder="2026-01-15",
                                value=datetime.now().strftime("%Y-%m-%d"),
                                info="Format: YYYY-MM-DD",
                                max_lines=1
                            )
                            
                            manual_time = gr.Textbox(
                                label="🕐 Time (HH:MM) - UTC+1",
                                placeholder="14:00",
                                value="09:00",
                                info="24-hour format",
                                max_lines=1
                            )
                        
                        with gr.Row():
                            manual_duration = gr.Slider(
                                label="⏱️ Duration (hours)",
                                minimum=0.25,
                                maximum=8,
                                step=0.25,
                                value=1.0
                            )
                            
                            manual_reminder = gr.Slider(
                                label="🔔 Reminder (hours before)",
                                minimum=0,
                                maximum=48,
                                step=0.25,
                                value=1.0
                            )
                        
                        manual_location = gr.Textbox(
                            label="📍 Location",
                            placeholder="e.g., Conference Room A",
                            lines=1
                        )
                        
                        manual_description = gr.Textbox(
                            label="📄 Description",
                            placeholder="Event details...",
                            lines=3
                        )
                        
                        with gr.Accordion("👤 Organizer (Optional)", open=False):
                            manual_org_name = gr.Textbox(label="Name", placeholder="John Doe")
                            manual_org_email = gr.Textbox(label="Email", placeholder="john@example.com")
                        
                        manual_create_btn = gr.Button("🎯 Create Event with Agent Skill", variant="primary", size="lg")
                    
                    with gr.Column(scale=1):
                        manual_status = gr.Markdown("ℹ️ Fill form and click Create Event")
                        manual_download = gr.File(label="📥 Download .ics File", visible=True)
                        
                        with gr.Accordion("👁️ ICS Preview", open=False):
                            manual_preview = gr.Textbox(label="ICS Content", lines=15, show_copy_button=True)
                
                manual_create_btn.click(
                    fn=create_event_manual,
                    inputs=[
                        manual_date, manual_time, manual_duration,
                        manual_title, manual_location, manual_description,
                        manual_org_name, manual_org_email, manual_reminder
                    ],
                    outputs=[manual_download, manual_status, manual_preview]
                )
            
            # ===========================
            # AI Assistant Tab
            # ===========================
            
            with gr.Tab("🤖 AI Assistant"):
                gr.Markdown("""
                ### Use natural language to create events
                
                This tab uses the Agent Skill's `natural_language_to_ics()` method,
                which provides the complete AI parsing pipeline.
                
                **Examples:**
                - "Schedule a team meeting tomorrow at 2pm for 2 hours"
                - "Create a dentist appointment on December 5th at 10:30am"
                - "Add project deadline next Friday at 5pm"
                
                **Note:** Requires `NVIDIA_API_KEY` environment variable
                """)
                
                with gr.Row():
                    with gr.Column(scale=2):
                        ai_input = gr.Textbox(
                            label="📝 Describe Your Event",
                            placeholder="e.g., Schedule a product demo next Tuesday at 3pm for 90 minutes",
                            lines=4
                        )
                        
                        ai_examples = gr.Examples(
                            examples=[
                                ["Schedule a team standup tomorrow at 9am for 30 minutes"],
                                ["Create a client presentation on January 20th at 2pm for 2 hours"],
                                ["Add lunch meeting with Sarah next Monday at noon"],
                                ["Book conference room for quarterly review next Friday 3-5pm"],
                            ],
                            inputs=ai_input
                        )
                        
                        ai_create_btn = gr.Button("🚀 Create Event with AI Skill", variant="primary", size="lg")
                    
                    with gr.Column(scale=1):
                        ai_status = gr.Markdown("ℹ️ Enter event description")
                        ai_download = gr.File(label="📥 Download .ics File", visible=True)
                        
                        with gr.Accordion("👁️ ICS Preview", open=False):
                            ai_preview = gr.Textbox(label="ICS Content", lines=15, show_copy_button=True)
                
                ai_create_btn.click(
                    fn=create_event_with_ai,
                    inputs=[ai_input],
                    outputs=[ai_download, ai_status, ai_preview]
                )
            
            # ===========================
            # Help Tab
            # ===========================
            
            with gr.Tab("ℹ️ Help"):
                gr.Markdown("""
                ## 📚 About This Demo
                
                This application demonstrates the **Calendar Assistant Agent Skill** - a modular,
                reusable capability that follows the Agent Skills specification.
                
                ### How It Works
                
                1. **Agent Skill Layer:** Core calendar logic in `calendar_skill.py`
                2. **Integration Layer:** This Gradio app imports and uses the skill
                3. **User Interface:** Web UI for easy interaction
                
                ### Agent Skill Architecture
                
                ```
                ┌─────────────────────────────────────┐
                │   Gradio Web Interface (This App)  │
                │   - Manual Entry Form               │
                │   - AI Natural Language Input       │
                └─────────────┬───────────────────────┘
                              │
                              ▼
                ┌─────────────────────────────────────┐
                │   Calendar Assistant Agent Skill    │
                │   - parse_natural_language()        │
                │   - create_calendar_event()         │
                │   - natural_language_to_ics()       │
                └─────────────┬───────────────────────┘
                              │
                              ▼
                ┌─────────────────────────────────────┐
                │   ICS File Output                   │
                │   - RFC 5545 Compliant              │
                │   - Universal Calendar Format       │
                └─────────────────────────────────────┘
                ```
                
                ### Why Agent Skills?
                
                **Traditional Approach:**
                - Calendar logic embedded in each app
                - Duplicate code across projects
                - Hard to maintain and update
                
                **Agent Skills Approach:**
                - Calendar logic in reusable skill
                - Import and use in any project
                - Update once, benefit everywhere
                - Self-documenting and testable
                
                ### Importing to Calendar Apps
                
                **Double-click method (easiest):**
                1. Download the .ics file
                2. Find it in your Downloads folder
                3. Double-click the file
                4. Your calendar app opens automatically
                5. Click Save/Add to confirm
                
                **Manual import:**
                - **Google Calendar:** Settings → Import & Export
                - **Outlook:** File → Open & Export → Import iCalendar
                - **Apple Calendar:** File → Import
                
                ### API Key Setup
                
                For AI features, set your NVIDIA API key:
                
                **Windows PowerShell:**
                ```powershell
                $env:NVIDIA_API_KEY="nvapi-xxxxx"
                ```
                
                **Linux/Mac:**
                ```bash
                export NVIDIA_API_KEY="nvapi-xxxxx"
                ```
                
                Get your key at [build.nvidia.com](https://build.nvidia.com/)
                
                ---
                
                ## 🔗 Resources
                
                - [Agent Skills Specification](https://github.com/agentskills/agentskills)
                - [NVIDIA AI Endpoints](https://build.nvidia.com/)
                - [iCalendar RFC 5545](https://tools.ietf.org/html/rfc5545)
                - [Gradio Documentation](https://gradio.app/)
                
                ---
                
                **Made with ❤️ using Agent Skills, Gradio, NVIDIA AI, and Python**
                """)
        
        gr.Markdown("""
        ---
        💡 **Agent Skill Advantage:** This same calendar skill can be used in CLI tools, 
        web apps, desktop apps, or integrated into larger AI agent systems!
        """)
    
    return app


# ===========================
# Main Entry Point
# ===========================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 Calendar Assistant Agent Skill - Gradio Integration")
    print("="*60)
    print("\nSkill Status:")
    print(json.dumps(calendar_skill.get_skill_info(), indent=2))
    print("\n" + "="*60 + "\n")
    
    app = create_gradio_interface()
    
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )

