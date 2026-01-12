"""
Calendar Assistant Agent Skill
Main implementation of calendar management capabilities

This module provides the CalendarAssistantSkill class for creating and managing
calendar events from natural language or structured inputs. Compliant with
Agent Skills Python API specification.
"""

from datetime import datetime, timedelta
from icalendar import Calendar, Event, vCalAddress, vText, Alarm
import zoneinfo
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any

try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    from langchain_core.messages import SystemMessage, HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from colorama import Fore, Style
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback for systems without colorama
    class Fore:
        YELLOW = ""
        RESET = ""
    class Style:
        RESET_ALL = ""


class CalendarAssistantSkill:
    """
    Agent Skill for calendar management and event creation
    Provides natural language parsing and ICS file generation
    
    Attributes:
        api_key (Optional[str]): NVIDIA API key for AI parsing
        default_timezone (str): Default timezone for events (IANA format)
        llm: Language model for natural language processing
    """
    
    def __init__(self, api_key: Optional[str] = None, default_timezone: str = "UTC"):
        """
        Initialize the Calendar Assistant Skill
        
        Args:
            api_key: NVIDIA API key for AI parsing (optional)
            default_timezone: Default timezone for events (default: UTC)
        
        Raises:
            ValueError: If default_timezone is not a valid IANA timezone
        """
        # Validate timezone
        try:
            zoneinfo.ZoneInfo(default_timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone: {default_timezone}. Use IANA timezone names.")
        
        self.api_key = api_key
        self.default_timezone = default_timezone
        self.llm = None
        
        if api_key and LANGCHAIN_AVAILABLE:
            self._initialize_llm()
        elif api_key and not LANGCHAIN_AVAILABLE:
            print("Warning: langchain packages not available. Install langchain-nvidia-ai-endpoints for AI parsing.")
    
    def _initialize_llm(self):
        """Initialize the NVIDIA LLM for natural language parsing"""
        try:
            self.llm = ChatNVIDIA(
                model="meta/llama-3.1-405b-instruct",
                api_key=self.api_key,
                temperature=0.3,
                max_completion_tokens=36000
            )
        except Exception as e:
            print(f"Warning: Could not initialize LLM: {e}")
            self.llm = None
    
    def parse_natural_language(
        self, 
        user_input: str, 
        reference_date: Optional[datetime] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse natural language input into structured event data
        
        Args:
            user_input: Natural language description of the event
            reference_date: Reference date for relative dates (default: now)
            
        Returns:
            Tuple of (event_data dict, error string)
            event_data contains: summary, description, start_date, start_time,
                                duration_hours, location, organizer_email, 
                                organizer_name, reminder_hours
        
        Example:
            >>> skill = CalendarAssistantSkill(api_key="your_key")
            >>> data, error = skill.parse_natural_language("Meeting tomorrow at 2pm")
            >>> if not error:
            ...     print(data['summary'])
        """
        if not self.llm:
            return None, "LLM not initialized. Please provide API key and ensure langchain packages are installed."
        
        if reference_date is None:
            reference_date = datetime.now(zoneinfo.ZoneInfo(self.default_timezone))
        
        try:
            current_date = reference_date.strftime("%Y-%m-%d")
            system_prompt = f"""You are a calendar assistant. Parse user requests into structured event data.
Return ONLY a valid JSON object with these fields:
{{
    "summary": "Event title",
    "description": "Event description",
    "start_date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "duration_hours": float,
    "location": "Location (optional)",
    "organizer_email": "email@example.com (optional)",
    "organizer_name": "Name (optional)",
    "reminder_hours": 1
}}

Current date for reference: {current_date}
Timezone: {self.default_timezone}

Example input: "Schedule a team meeting tomorrow at 2pm for 2 hours about Q4 planning"
Example output: {{"summary": "Team Meeting - Q4 Planning", "start_date": "2026-01-13", "start_time": "14:00", "duration_hours": 2.0, "description": "Quarterly planning discussion", "reminder_hours": 1}}

IMPORTANT: Return ONLY the JSON object, no explanations.
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Extract JSON from potential markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            
            if COLORAMA_AVAILABLE:
                print(Fore.YELLOW + f"AI extracted calendar info: {response_text}" + Style.RESET_ALL)
            else:
                print(f"AI extracted calendar info: {response_text}")
            
            event_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['summary', 'start_date', 'start_time']
            for field in required_fields:
                if field not in event_data:
                    return None, f"Missing required field: {field}"
            
            return event_data, None
            
        except json.JSONDecodeError as e:
            return None, f"Error parsing JSON response: {str(e)}"
        except Exception as e:
            return None, f"Error parsing with AI: {str(e)}"
    
    def create_calendar_event(
        self,
        summary: str,
        start_datetime: datetime,
        duration_hours: float = 1.0,
        description: str = "",
        location: str = "",
        organizer_email: str = "",
        organizer_name: str = "",
        attendees: Optional[List[Dict[str, str]]] = None,
        reminder_hours: float = 1.0,
        recurrence: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Create an iCalendar event (RFC 5545 compliant)
        
        Args:
            summary: Event title (required)
            start_datetime: Start date and time (timezone-aware recommended)
            duration_hours: Event duration in hours (default: 1.0)
            description: Event description
            location: Event location
            organizer_email: Organizer's email address
            organizer_name: Organizer's name
            attendees: List of attendee dicts with 'email', 'name', 'role'
            reminder_hours: Hours before event to trigger reminder (default: 1.0)
            recurrence: Recurrence rules (optional, for future use)
            
        Returns:
            bytes: ICS file content ready to save or send
        
        Raises:
            ValueError: If required parameters are invalid
        
        Example:
            >>> from datetime import datetime, timedelta
            >>> import zoneinfo
            >>> skill = CalendarAssistantSkill()
            >>> start = datetime.now(zoneinfo.ZoneInfo("UTC")) + timedelta(days=1)
            >>> ics = skill.create_calendar_event(
            ...     summary="Team Meeting",
            ...     start_datetime=start,
            ...     duration_hours=2.0
            ... )
            >>> with open("event.ics", "wb") as f:
            ...     f.write(ics)
        """
        if not summary:
            raise ValueError("Event summary is required")
        
        if not isinstance(start_datetime, datetime):
            raise ValueError("start_datetime must be a datetime object")
        
        cal = Calendar()
        cal.add('prodid', '-//Calendar Assistant Agent Skill//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        
        event = Event()
        event.add('summary', summary)
        
        # Ensure datetime has timezone
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(
                tzinfo=zoneinfo.ZoneInfo(self.default_timezone)
            )
        
        event.add('dtstart', start_datetime)
        
        # Calculate end time
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        event.add('dtend', end_datetime)
        
        # Add timestamp (current time in UTC)
        event.add('dtstamp', datetime.now(zoneinfo.ZoneInfo("UTC")))
        
        # Generate unique UID
        uid_base = f"{summary}{start_datetime.isoformat()}"
        uid_hash = hashlib.md5(uid_base.encode()).hexdigest()
        event['uid'] = f"{uid_hash}@calendar-assistant-skill"
        
        if location:
            event.add('location', location)
        
        if description:
            event.add('description', description)
        
        # Add organizer
        if organizer_email:
            organizer = vCalAddress(f'mailto:{organizer_email}')
            if organizer_name:
                organizer.params['CN'] = organizer_name
            event['organizer'] = organizer
        
        # Add attendees
        if attendees:
            for attendee in attendees:
                if 'email' not in attendee:
                    continue
                attendee_addr = vCalAddress(f'mailto:{attendee["email"]}')
                attendee_addr.params['CN'] = attendee.get('name', attendee['email'])
                attendee_addr.params['ROLE'] = attendee.get('role', 'REQ-PARTICIPANT')
                event.add('attendee', attendee_addr, encode=0)
        
        # Add reminder alarm
        if reminder_hours > 0:
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('trigger', timedelta(hours=-reminder_hours))
            alarm.add('description', f'Reminder: {summary}')
            event.add_component(alarm)
        
        # Add recurrence if specified
        if recurrence:
            event.add('rrule', recurrence)
        
        cal.add_component(event)
        
        return cal.to_ical()
    
    def create_event_from_data(self, event_data: Dict[str, Any]) -> bytes:
        """
        Create calendar event from parsed data dictionary
        
        Args:
            event_data: Dictionary with event fields from parse_natural_language()
                       Must contain: summary, start_date, start_time
                       Optional: duration_hours, description, location, etc.
            
        Returns:
            bytes: ICS file content
        
        Raises:
            KeyError: If required fields are missing
            ValueError: If date/time parsing fails
        
        Example:
            >>> data = {
            ...     "summary": "Meeting",
            ...     "start_date": "2026-01-13",
            ...     "start_time": "14:00",
            ...     "duration_hours": 1.0
            ... }
            >>> ics = skill.create_event_from_data(data)
        """
        # Parse datetime
        try:
            start_date = datetime.strptime(event_data['start_date'], '%Y-%m-%d')
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid or missing start_date: {e}")
        
        if event_data.get('start_time'):
            try:
                hour, minute = map(int, event_data['start_time'].split(':'))
                start_date = start_date.replace(hour=hour, minute=minute)
            except ValueError as e:
                raise ValueError(f"Invalid start_time format: {e}")
        
        # Add timezone
        start_date = start_date.replace(tzinfo=zoneinfo.ZoneInfo(self.default_timezone))
        
        return self.create_calendar_event(
            summary=event_data['summary'],
            start_datetime=start_date,
            duration_hours=float(event_data.get('duration_hours', 1.0)),
            description=event_data.get('description', ''),
            location=event_data.get('location', ''),
            organizer_email=event_data.get('organizer_email', ''),
            organizer_name=event_data.get('organizer_name', ''),
            reminder_hours=float(event_data.get('reminder_hours', 1.0))
        )
    
    def natural_language_to_ics(
        self, 
        user_input: str
    ) -> Tuple[Optional[bytes], Optional[str], Optional[Dict[str, Any]]]:
        """
        Complete pipeline: natural language -> parsed data -> ICS file
        
        This is the main entry point for AI agents using natural language.
        
        Args:
            user_input: Natural language event description
            
        Returns:
            Tuple of (ics_content bytes, error string, parsed_data dict)
            - If successful: (bytes, None, dict)
            - If error: (None, error_message, None) or (None, error_message, partial_data)
        
        Example:
            >>> skill = CalendarAssistantSkill(api_key="your_key")
            >>> ics, error, data = skill.natural_language_to_ics(
            ...     "Schedule team meeting tomorrow at 2pm for 2 hours"
            ... )
            >>> if not error:
            ...     with open("meeting.ics", "wb") as f:
            ...         f.write(ics)
        """
        # Parse natural language
        event_data, error = self.parse_natural_language(user_input)
        
        if error:
            return None, error, None
        
        try:
            # Create ICS file
            ics_content = self.create_event_from_data(event_data)
            return ics_content, None, event_data
        except Exception as e:
            return None, f"Error creating ICS: {str(e)}", event_data
    
    def get_skill_info(self) -> Dict[str, Any]:
        """
        Get information about this skill's capabilities
        
        Returns:
            Dict with skill metadata including:
            - name: Skill identifier
            - version: Skill version
            - capabilities: List of supported operations
            - status: Initialization status
            - llm_available: Whether AI parsing is available
            - default_timezone: Configured timezone
        
        Example:
            >>> skill = CalendarAssistantSkill()
            >>> info = skill.get_skill_info()
            >>> print(info['capabilities'])
        """
        return {
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
            "llm_available": self.llm is not None,
            "langchain_available": LANGCHAIN_AVAILABLE,
            "default_timezone": self.default_timezone
        }


# Convenience functions for skill discovery
def get_skill_metadata() -> Dict[str, Any]:
    """
    Get skill metadata without initialization
    
    Returns:
        Dict with basic skill information
    """
    return {
        "name": "calendar-assistant",
        "version": "1.0.0",
        "description": "Calendar management skill for creating events from natural language",
        "runtime": "python",
        "entry_point": "calendar_skill.py"
    }


def create_skill_instance(api_key: Optional[str] = None, **kwargs) -> CalendarAssistantSkill:
    """
    Factory function to create skill instance
    
    Args:
        api_key: NVIDIA API key (optional)
        **kwargs: Additional initialization parameters
    
    Returns:
        CalendarAssistantSkill instance
    """
    return CalendarAssistantSkill(api_key=api_key, **kwargs)


# Example usage function for testing
def example_usage():
    """Example of how to use the Calendar Assistant Skill"""
    import os
    
    # Initialize skill with API key from environment
    api_key = os.environ.get('NVIDIA_API_KEY')
    skill = CalendarAssistantSkill(api_key=api_key, default_timezone="Europe/Paris")
    
    print("=" * 60)
    print("Calendar Assistant Skill - Agent Skills API Compliant")
    print("=" * 60)
    print(json.dumps(skill.get_skill_info(), indent=2))
    
    # Example 1: Create event manually
    print("\n=== Example 1: Manual Event Creation ===")
    start_time = datetime.now(zoneinfo.ZoneInfo("Europe/Paris")) + timedelta(days=1, hours=9)
    ics_content = skill.create_calendar_event(
        summary="Team Standup",
        start_datetime=start_time,
        duration_hours=0.5,
        description="Daily team synchronization",
        location="Conference Room A",
        reminder_hours=0.25
    )
    print(f"✅ Created ICS file ({len(ics_content)} bytes)")
    
    # Example 2: Natural language parsing
    if api_key:
        print("\n=== Example 2: Natural Language Parsing ===")
        ics_content, error, parsed_data = skill.natural_language_to_ics(
            "Schedule a client presentation next Tuesday at 3pm for 2 hours"
        )
        if error:
            print(f"❌ Error: {error}")
        else:
            print("✅ Parsed data:", json.dumps(parsed_data, indent=2))
            print(f"✅ Created ICS file ({len(ics_content)} bytes)")
    else:
        print("\n=== Example 2: Skipped (no API key) ===")
        print("Set NVIDIA_API_KEY environment variable to test AI parsing")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    example_usage()

