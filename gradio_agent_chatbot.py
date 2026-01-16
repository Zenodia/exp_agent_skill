#!/usr/bin/env python3
"""
Agent Skills Chatbot - Gradio Demo
Demonstrates agentic tool usage with skill discovery and execution
Following Agent Skills API specification: https://github.com/agentskills/agentskills
"""

import os
import sys
import re
import yaml
import json
import gradio as gr
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from openai import OpenAI
from datetime import datetime
import zoneinfo
import tiktoken
from colorama import Fore, Style
import tempfile

# Import skills for actual execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'calendar_assistant_skill', 'scripts'))
from calendar_skill import CalendarAssistantSkill

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nvidia_ideagen_skill', 'scripts'))
from ideagen_skill import NvidiaIdeaGenSkill

class AgentSkillsOrchestrator:
    """
    Orchestrator for discovering and managing Agent Skills
    Following Agent Skills API specification for prompt integration
    """
    
    def __init__(self, skills_directories: List[str], api_key: Optional[str] = None):
        """
        Initialize the orchestrator with skill directories
        
        Args:
            skills_directories: List of directory paths to scan for skills
            api_key: NVIDIA API key (defaults to NVIDIA_API_KEY env var)
        """
        self.skills_directories = [Path(d) for d in skills_directories]
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "NVIDIA_API_KEY must be set as environment variable or passed to constructor. "
                "Get your key at: https://build.nvidia.com/"
            )
        
        # Initialize OpenAI client with NVIDIA endpoint
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )
        
        self.model = "nvidia/llama-3.1-nemotron-nano-8b-v1"
        
        # Initialize calendar skill for actual execution
        try:
            self.calendar_skill = CalendarAssistantSkill(api_key=self.api_key)
            print("✅ Calendar skill initialized for direct execution")
        except Exception as e:
            print(f"⚠️  Calendar skill initialization failed: {e}")
            self.calendar_skill = None
        
        # Initialize nvidia-ideagen skill for actual execution
        try:
            self.ideagen_skill = NvidiaIdeaGenSkill(api_key=self.api_key)
            print("✅ NVIDIA IdeaGen skill initialized for direct execution")
        except Exception as e:
            print(f"⚠️  NVIDIA IdeaGen skill initialization failed: {e}")
            self.ideagen_skill = None
        
        # Discover skills at startup
        self.skills = self.discover_all_skills()
        print(f"\n✅ Discovered {len(self.skills)} skills: {list(self.skills.keys())}")
    
    def discover_all_skills(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all Agent Skills in configured directories
        
        Following Agent Skills spec:
        1. Scan configured directories for SKILL.md files
        2. Parse only the frontmatter (name and description) at startup
        3. Keep initial context usage low (~50-100 tokens per skill)
        
        Returns:
            Dict of skill_name -> skill_metadata
        """
        skills = {}
        
        for directory in self.skills_directories:
            if not directory.exists():
                continue
            
            # Find all SKILL.md files
            for skill_md in directory.rglob("SKILL.md"):
                try:
                    skill_data = self._parse_skill_md(skill_md)
                    if skill_data:
                        skill_name = skill_data['name']
                        skills[skill_name] = skill_data
                except Exception as e:
                    print(f"⚠️  Error parsing {skill_md}: {e}")
                    continue
        
        return skills
    
    def _parse_skill_md(self, skill_md_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse SKILL.md file for metadata and instructions
        
        Args:
            skill_md_path: Path to SKILL.md file
            
        Returns:
            Dict with metadata, or None if parsing fails
        """
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        if not content.startswith("---"):
            return None
        
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        
        try:
            metadata = yaml.safe_load(parts[1])
            # Store the full SKILL.md content (instructions) for later activation
            metadata['full_instructions'] = parts[2].strip()
            metadata['location'] = str(skill_md_path.absolute())
            metadata['path'] = str(skill_md_path.parent.absolute())
            return metadata
        except yaml.YAMLError as e:
            print(f"⚠️  YAML parsing error: {e}")
            return None
    
    def build_available_skills_xml(self) -> str:
        """
        Generate the <available_skills> XML block for agent context injection
        
        This follows the Agent Skills specification:
        https://agentskills.io/integrate-skills#injecting-into-context
        
        Returns:
            XML string with skill metadata for system prompt
        """
        if not self.skills:
            return ""
        
        xml_parts = ["<available_skills>"]
        
        for skill_name, skill_data in self.skills.items():
            print(f"skillname:{skill_name},\n skill_data:{skill_data['location']}")
            xml_parts.append(f"""  <skill>
    <name>{skill_name}</name>
    <description>{skill_data['description']}</description>
    <location>{skill_data['location']}</location>
  </skill>""")
        
        xml_parts.append("</available_skills>")
        
        return "\n".join(xml_parts)
    
    def detect_skill_trigger(self, user_query: str) -> Optional[str]:
        """
        Detect which skill (if any) should be triggered based on user query
        
        Args:
            user_query: User's question or request
            
        Returns:
            Skill name if matched, None otherwise
        """
        query_lower = user_query.lower()
        
        # Define trigger keywords for each skill
        triggers = {
            'calendar-assistant': [
                'calendar', 'meeting', 'appointment', 'schedule', 'event',
                'book', 'create event', 'add to calendar', 'set up meeting'
            ],
            'nvidia-ideagen': [
                'idea', 'brainstorm', 'generate ideas', 'creative', 'concept',
                'ideation', 'innovation', 'suggest', 'come up with'
            ]
        }
        
        # Score each skill based on trigger keyword matches
        skill_scores = {}
        for skill_name, keywords in triggers.items():
            if skill_name in self.skills:
                score = sum(1 for kw in keywords if kw in query_lower)
                if score > 0:
                    skill_scores[skill_name] = score
        
        # Return skill with highest score
        if skill_scores:
            return max(skill_scores, key=skill_scores.get)
        
        return None
    
    def build_system_prompt(
        self, 
        activated_skill: Optional[str] = None,
        include_full_instructions: bool = True
    ) -> str:
        """
        Build the complete system prompt with Agent Skills integration
        
        Following Agent Skills specification:
        1. Always include available_skills metadata
        2. If a skill is activated, include its full SKILL.md instructions
        
        Args:
            activated_skill: Name of skill to activate (if any)
            include_full_instructions: Whether to include full skill instructions
            
        Returns:
            Complete system prompt string
        """
        # Base system prompt
        base_prompt = """You are an intelligent AI assistant with access to specialized skills.

When responding to user queries:
1. Analyze if the query matches any available skill's purpose
2. If a skill is activated, follow its instructions precisely
3. Use the skill's capabilities to provide accurate, helpful responses
4. If no skill matches, respond normally using your general knowledge

Current date for reference: {current_date}
Current time for reference: {current_time}
""".format(
            current_date=datetime.now().strftime("%Y-%m-%d"),
            current_time=datetime.now().strftime("%H:%M:%S")
        )
        
        # Initialize token encoder for counting
        encoding = tiktoken.get_encoding("cl100k_base")
        
        # Add available skills metadata
        skills_xml = self.build_available_skills_xml()
        
        # Count tokens
        cnt_base_prompt = len(encoding.encode(base_prompt))
        cnt_skill_prompt = len(encoding.encode(skills_xml))
        
        print(Fore.YELLOW + "base_prompt token count: " + str(cnt_base_prompt) + Style.RESET_ALL)
        print(Fore.BLUE + "skills_xml token count: " + str(cnt_skill_prompt) + Style.RESET_ALL)
        print(Fore.GREEN + "Total system prompt token count: " + str(cnt_base_prompt + cnt_skill_prompt) + Style.RESET_ALL)
        
        prompt = base_prompt + "\n" + skills_xml + "\n"
        
        # If a skill is activated, add its full instructions
        if activated_skill and activated_skill in self.skills and include_full_instructions:
            skill_data = self.skills[activated_skill]
            prompt += f"\n# ACTIVATED SKILL: {activated_skill}\n\n"
            prompt += "## Skill Instructions:\n\n"
            prompt += skill_data['full_instructions']
            prompt += "\n\n## End of Skill Instructions\n"
            prompt += f"\nYou MUST follow the above skill instructions for this query.\n"
        
        return prompt
    
    def chat_stream(
        self, 
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Tuple[str, str, Optional[bytes]]:
        """
        Process user query with streaming response
        
        Args:
            user_query: User's question or request
            temperature: LLM temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Tuple of (response_chunk, activated_skill_name, ics_content_bytes)
        """
        # Detect which skill to trigger
        activated_skill = self.detect_skill_trigger(user_query)
        
        # If calendar skill detected, execute it directly
        if activated_skill == "calendar-assistant" and self.calendar_skill:
            try:
                ics_content, error, parsed_data = self.calendar_skill.natural_language_to_ics(user_query)
                
                if error:
                    yield f"❌ Error creating calendar event: {error}\n\nPlease provide more details about the event.", activated_skill, None
                    return
                
                # Generate success message
                success_msg = f"""✅ **Calendar Event Created!**

📅 **Event Details:**
- **Title:** {parsed_data['summary']}
- **Date:** {parsed_data['start_date']}
- **Time:** {parsed_data.get('start_time', 'All day')}
- **Duration:** {parsed_data.get('duration_hours', 1)} hours
- **Location:** {parsed_data.get('location', 'Not specified')}
- **Description:** {parsed_data.get('description', 'Not specified')}
- **Reminder:** {parsed_data.get('reminder_hours', 1)} hours before

📥 **How to Add to Your Calendar:**
1. Click the **Download** button below
2. Find the downloaded `.ics` file
3. **Double-click** the file - it will open in your calendar app!

Or import manually into Google Calendar, Outlook, or Apple Calendar.

✨ The ICS file is ready for download and can be viewed in the preview panel!"""
                
                yield success_msg, activated_skill, ics_content
                return
                
            except Exception as e:
                yield f"❌ Error executing calendar skill: {str(e)}", activated_skill, None
                return
        
        # If nvidia-ideagen skill detected, execute it directly
        if activated_skill == "nvidia-ideagen" and self.ideagen_skill:
            try:
                # Parse the query to extract number of ideas if specified
                import re
                num_ideas_match = re.search(r'(\d+)\s+ideas?', user_query.lower())
                num_ideas = int(num_ideas_match.group(1)) if num_ideas_match and 1 <= int(num_ideas_match.group(1)) <= 10 else 5
                
                # Extract topic (remove the number of ideas part)
                topic = re.sub(r'generate|brainstorm|give me|create|come up with|i need', '', user_query, flags=re.IGNORECASE)
                topic = re.sub(r'\d+\s+ideas?\s+(for|about|on)?', '', topic, flags=re.IGNORECASE)
                topic = topic.strip()
                
                if not topic:
                    topic = user_query
                
                # Stream ideas generation
                for chunk in self.ideagen_skill.generate_ideas_stream(
                    topic=topic,
                    num_ideas=num_ideas,
                    creativity=temperature
                ):
                    yield chunk, activated_skill, None
                
                return
                
            except Exception as e:
                yield f"❌ Error executing idea generation skill: {str(e)}", activated_skill, None
                return
        
        # Build system prompt for other skills
        system_prompt = self.build_system_prompt(activated_skill=activated_skill)
        
        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        # Stream response from LLM
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                top_p=0.95,
                max_tokens=max_tokens,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content, activated_skill, None
        
        except Exception as e:
            error_msg = f"\n\n❌ Error: {str(e)}\n\nPlease try again or check your API key."
            yield error_msg, None, None
    
    def chat(
        self, 
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Tuple[str, Optional[str], Optional[bytes]]:
        """
        Process user query (non-streaming version)
        
        Args:
            user_query: User's question or request
            temperature: LLM temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (complete_response, activated_skill_name, ics_content_bytes)
        """
        response = ""
        activated_skill = None
        ics_content_bytes = None
        
        for chunk, skill, ics_bytes in self.chat_stream(user_query, temperature, max_tokens):
            response += chunk
            if skill and not activated_skill:
                activated_skill = skill
            if ics_bytes:
                ics_content_bytes = ics_bytes
        
        return response, activated_skill, ics_content_bytes


class GradioAgentUI:
    """Gradio UI wrapper for Agent Skills Chatbot"""
    
    def __init__(self, orchestrator: AgentSkillsOrchestrator):
        self.orchestrator = orchestrator
        self.chat_history = []
    
    def save_ics_file(self, ics_content: str, summary: str = "event") -> str:
        """
        Save ICS content to a temporary file
        
        Args:
            ics_content: The ICS file content (string)
            summary: Event summary for filename
            
        Returns:
            Path to the temporary file
        """
        # Clean summary for filename
        event_name_safe = "".join(c for c in summary if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        if not event_name_safe:
            event_name_safe = "event"
        
        filename = f"event_{event_name_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
        
        # Create temp file in binary mode (matching calendar_gradio_app_with_skill.py)
        temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.ics', prefix='')
        temp_file.write(ics_content.encode('utf-8'))
        temp_file.close()
        
        return temp_file.name
    
    def process_message(
        self, 
        user_message: str, 
        history: List[List[str]],
        temperature: float
    ):
        """
        Process user message and stream response
        
        Args:
            user_message: User's input message
            history: Chat history (list of [user_msg, bot_msg] tuples)
            temperature: LLM temperature
            
        Yields:
            Tuple of (history, file_path, ics_preview)
        """
        if not user_message or not user_message.strip():
            yield history, None, ""
            return
        
        # Add user message to history
        history = history or []
        history.append([user_message, ""])
        
        # Stream response
        activated_skill = None
        response = ""
        ics_content_bytes = None
        
        for chunk, skill, ics_bytes in self.orchestrator.chat_stream(
            user_message, 
            temperature=temperature
        ):
            response += chunk
            if skill and not activated_skill:
                activated_skill = skill
                # Prepend skill activation notice
                skill_notice = f"🎯 **Using Skill:** `{activated_skill}`\n\n---\n\n"
                response = skill_notice + response
                history[-1][1] = response
            else:
                history[-1][1] = response
            
            # Store ICS content if returned
            if ics_bytes:
                ics_content_bytes = ics_bytes
            
            yield history, None, ""
        
        # After streaming completes, check if we have ICS content from calendar skill
        if activated_skill == "calendar-assistant" and ics_content_bytes:
            # Decode ICS content for preview
            ics_preview = ics_content_bytes.decode('utf-8')
            
            # Extract summary for filename
            summary_match = re.search(r'SUMMARY:(.*?)(?:\r?\n)', ics_preview)
            summary = summary_match.group(1) if summary_match else "event"
            
            # Save to temp file
            file_path = self.save_ics_file(ics_preview, summary)
            
            # Return with file and preview
            yield history, file_path, ics_preview
            return
        
        # Final yield for non-calendar responses
        yield history, None, ""
    
    def clear_history(self):
        """Clear chat history"""
        return []
    
    def build_interface(self) -> gr.Blocks:
        """Build and return Gradio interface"""
        
        with gr.Blocks(
            title="Agent Skills Chatbot"
        ) as interface:
            
            gr.Markdown(
                """
                # 🤖 Agent Skills Chatbot Demo
                
                This chatbot demonstrates **agentic tool usage** with skill discovery and execution.
                
                ## Available Skills:
                """
            )
            
            # Display available skills
            skills_info = ""
            for skill_name, skill_data in self.orchestrator.skills.items():
                skills_info += f"- **{skill_name}**: {skill_data['description']}\n"
            
            gr.Markdown(skills_info)
            
            gr.Markdown(
                """
                ---
                
                ### How it works:
                1. Ask a question about **idea generation** or **calendar booking**
                2. The agent will automatically detect and activate the relevant skill
                3. The skill's instructions are loaded and used to respond accurately
                4. Responses are streamed in real-time powered by NVIDIA's Nemotron model
                5. For calendar events: **Download the .ics file** and import to your calendar app!
                
                ---
                """
            )
            
            # Chat interface with right sidebar
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="Chat",
                        height=500,
                        show_label=True,                        
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="Your message",
                            placeholder="Ask me to generate ideas or book a calendar event...",
                            scale=4,
                            lines=2
                        )
                        submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Column(scale=1):
                    # Calendar file download section
                    gr.Markdown("### 📅 Calendar Event File")
                    ics_download = gr.File(
                        label="📥 Download .ics File",
                        visible=True,
                        interactive=False
                    )
                    gr.Markdown("""
                    **How to use:**
                    1. Download the .ics file above (when available)
                    2. Double-click to open in your calendar app
                    3. Or import manually in your calendar settings
                    """)
                    
                    # Examples moved here
                    gr.Examples(
                        examples=[
                            "Schedule a team meeting tomorrow at 2pm for 2 hours",
                            "Create a calendar event for my dentist appointment next Monday at 10am",
                            "Book a lunch meeting on Friday at noon with the marketing team",
                            "Generate 3 innovative ideas for sustainable urban living",
                            "I need ideas for a mobile app that helps people learn languages",
                            "Brainstorm concepts for AI-powered productivity tools"
                        ],
                        inputs=user_input,
                        label="💡 Try these examples"
                    )
            
            # Advanced Settings and Clear button
            with gr.Accordion("⚙️ Advanced Settings", open=False):
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="Temperature (creativity)",
                    info="Higher = more creative, Lower = more focused"
                )
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Chat")
            
            # Hidden textbox for ICS preview (no longer displayed but needed for output)
            ics_preview = gr.Textbox(visible=False)
            
            # Event handlers
            submit_btn.click(
                fn=self.process_message,
                inputs=[user_input, chatbot, temperature],
                outputs=[chatbot, ics_download, ics_preview]
            ).then(
                fn=lambda: "",
                outputs=[user_input]
            )
            
            user_input.submit(
                fn=self.process_message,
                inputs=[user_input, chatbot, temperature],
                outputs=[chatbot, ics_download, ics_preview]
            ).then(
                fn=lambda: "",
                outputs=[user_input]
            )
            
            clear_btn.click(
                fn=self.clear_history,
                outputs=[chatbot]
            )
            
            gr.Markdown(
                """
                ---
                
                ### Technical Details:
                - **Framework**: Following [Agent Skills API Specification](https://github.com/agentskills/agentskills)
                - **LLM**: NVIDIA Llama 3.1 Nemotron Nano 8B via NVIDIA API Catalog
                - **Skills**: Discovered dynamically from SKILL.md files
                - **Prompt Integration**: Strictly following Agent Skills prompt integration guidelines
                
                ---
                
                💡 **Tip**: The agent automatically detects when to use skills based on your query keywords.
                Watch for the "Using Skill" indicator in responses!
                """
            )
        
        return interface


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("Agent Skills Chatbot - Gradio Demo")
    print("="*80 + "\n")
    
    # Check for API key
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ Error: NVIDIA_API_KEY environment variable not set")
        print("\nPlease set it using:")
        print("  PowerShell: $env:NVIDIA_API_KEY='your-key-here'")
        print("  CMD:        set NVIDIA_API_KEY=your-key-here")
        print("  Linux/Mac:  export NVIDIA_API_KEY='your-key-here'")
        print("\nGet your key at: https://build.nvidia.com/")
        sys.exit(1)
    
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Define skill directories to scan
    skill_directories = [
        str(project_dir / "calendar_assistant_skill"),
        str(project_dir / "nvidia_ideagen_skill")
    ]
    
    print("🔍 Scanning for skills in:")
    for d in skill_directories:
        print(f"   - {d}")
    
    try:
        # Initialize orchestrator
        orchestrator = AgentSkillsOrchestrator(
            skills_directories=skill_directories,
            api_key=api_key
        )
        
        # Display discovered skills
        print("\n📋 Skills Summary:")
        for skill_name, skill_data in orchestrator.skills.items():
            print(f"\n  🎯 {skill_name}")
            print(f"     Version: {skill_data.get('version', 'unknown')}")
            print(f"     Description: {skill_data['description'][:100]}...")
        
        print("\n" + "="*80)
        print("✅ Initialization complete! Launching Gradio interface...")
        print("="*80 + "\n")
        
        # Build and launch UI
        ui = GradioAgentUI(orchestrator)
        interface = ui.build_interface()
        
        # Launch with public link option
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

