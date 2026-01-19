#!/usr/bin/env python3
"""
Agent Skills Chatbot - Enhanced with SkillLoader Integration
Demonstrates agentic tool usage with skill discovery and execution
Now using skill_loader.py for OpenSkills + AI Planner integration
"""

import os
import sys
import re
import gradio as gr
from pathlib import Path
from typing import List, Optional, Tuple
from openai import OpenAI
from datetime import datetime
import tempfile

# Import the new SkillLoader infrastructure
from skill_loader import SkillLoader

# Import skills for direct execution
sys.path.insert(0, str(Path(__file__).parent / 'calendar_assistant_skill' / 'scripts'))
from calendar_skill import CalendarAssistantSkill

sys.path.insert(0, str(Path(__file__).parent / 'nvidia_ideagen_skill' / 'scripts'))
from ideagen_skill import NvidiaIdeaGenSkill


class AgentSkillsChatbot:
    """
    Enhanced Agent Skills Chatbot using SkillLoader
    
    Implements the 5-step Agent Skills integration process:
    1. Discover skills in configured directories
    2. Load metadata (name and description) at startup
    3. Match user tasks to relevant skills
    4. Activate skills by loading full instructions
    5. Execute scripts and access resources as needed
    
    Reference: https://agentskills.io/integrate-skills#overview
    """
    
    def __init__(self, skills_base_path: str, api_key: Optional[str] = None):
        """
        Initialize chatbot with SkillLoader
        
        Args:
            skills_base_path: Base path containing skill directories
            api_key: NVIDIA API key (defaults to NVIDIA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "NVIDIA_API_KEY must be set as environment variable or passed to constructor. "
                "Get your key at: https://build.nvidia.com/"
            )
        
        # STEP 1: Discover skills in configured directories
        print(f"🔍 Step 1: Discovering skills from: {skills_base_path}")
        self.skill_loader = SkillLoader(Path(skills_base_path))
        
        # STEP 2: Load metadata (name and description) at startup
        print(f"📋 Step 2: Loading metadata at startup")
        self.skills = self.skill_loader.list_skills()
        print(f"✅ Discovered {len(self.skills)} skill(s):")
        for skill in self.skills:
            print(f"   📦 {skill.name} - {skill.skill_type}")
            print(f"      {skill.description[:80]}...")
        
        # Initialize OpenAI client with NVIDIA endpoint
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )
        self.model = "nvidia/llama-3.1-nemotron-nano-8b-v1"
        
        # Initialize skill instances for direct execution (Step 5 preparation)
        self._init_skill_instances()
    
    def _init_skill_instances(self):
        """Initialize skill instances for direct execution"""
        # Calendar skill
        try:
            self.calendar_skill = CalendarAssistantSkill(api_key=self.api_key)
            print("✅ Calendar skill initialized for execution")
        except Exception as e:
            print(f"⚠️  Calendar skill initialization failed: {e}")
            self.calendar_skill = None
        
        # IdeaGen skill
        try:
            self.ideagen_skill = NvidiaIdeaGenSkill(api_key=self.api_key)
            print("✅ IdeaGen skill initialized for execution")
        except Exception as e:
            print(f"⚠️  IdeaGen skill initialization failed: {e}")
            self.ideagen_skill = None
    
    # ========================================================================
    # STEP 3: Match user tasks to relevant skills
    # Reference: https://agentskills.io/integrate-skills#overview
    # ========================================================================
    
    def step3_match_skill(self, user_query: str) -> Tuple[Optional[str], dict]:
        """
        STEP 3: Match user task to relevant skill
        
        Analyzes user query and scores each skill based on keyword matching
        and semantic similarity to skill descriptions.
        
        Args:
            user_query: User's question or request
            
        Returns:
            Tuple of (skill_name, match_info_dict)
            match_info includes: score, matched_keywords, reasoning
        """
        query_lower = user_query.lower()
        
        # Define trigger keywords for each skill
        triggers = {
            'calendar-assistant': [
                'calendar', 'meeting', 'appointment', 'schedule', 'event',
                'book', 'create event', 'add to calendar', 'set up meeting',
                'remind', 'deadline'
            ],
            'nvidia-ideagen': [
                'idea', 'brainstorm', 'generate ideas', 'creative', 'concept',
                'ideation', 'innovation', 'suggest', 'come up with', 'think of'
            ]
        }
        
        # Score each discovered skill based on trigger keyword matches
        skill_scores = {}
        skill_matches = {}
        
        for skill in self.skills:
            if skill.name in triggers:
                keywords = triggers[skill.name]
                matched_kw = [kw for kw in keywords if kw in query_lower]
                score = len(matched_kw)
                
                if score > 0:
                    skill_scores[skill.name] = score
                    skill_matches[skill.name] = {
                        'score': score,
                        'matched_keywords': matched_kw,
                        'description': skill.description[:100]
                    }
        
        # Return skill with highest score
        if skill_scores:
            best_skill = max(skill_scores, key=skill_scores.get)
            match_info = skill_matches[best_skill]
            match_info['reasoning'] = f"Matched {match_info['score']} keyword(s): {', '.join(match_info['matched_keywords'][:3])}"
            return best_skill, match_info
        
        return None, {'reasoning': 'No skill matched the query'}
    
    # ========================================================================
    # STEP 4: Activate skills by loading full instructions
    # Reference: https://agentskills.io/integrate-skills#overview
    # ========================================================================
    
    def step4_activate_skill(self, skill_name: str) -> dict:
        """
        STEP 4: Activate skill by loading full instructions
        
        Loads the complete SKILL.md content including all instructions,
        capabilities, and usage guidelines.
        
        Args:
            skill_name: Name of skill to activate
            
        Returns:
            Dict with activation info: instructions_loaded, content_length, capabilities
        """
        skill = self.skill_loader.get_skill(skill_name)
        
        if not skill:
            return {
                'success': False,
                'error': f"Skill '{skill_name}' not found",
                'instructions_loaded': False
            }
        
        activation_info = {
            'success': True,
            'skill_name': skill_name,
            'skill_type': skill.skill_type,
            'instructions_loaded': bool(skill.skill_md_content),
            'content_length': len(skill.skill_md_content) if skill.skill_md_content else 0,
            'has_config': bool(skill.config),
            'has_references': (skill.skill_path / 'references').exists(),
            'has_assets': (skill.skill_path / 'assets').exists()
        }
        
        # Check for tools
        tools = self.skill_loader.discover_tools(skill_name)
        activation_info['tools_discovered'] = len(tools)
        activation_info['tool_names'] = [t._tool_name for t in tools[:5]]  # First 5
        
        return activation_info
    
    def build_system_prompt(
        self, 
        activated_skill: Optional[str] = None
    ) -> str:
        """
        Build system prompt with skills XML from SkillLoader
        Includes activated skill's full instructions if provided
        
        Args:
            activated_skill: Name of skill to activate (if any)
            
        Returns:
            Complete system prompt string
        """
        # Base system prompt
        base_prompt = f"""You are an intelligent AI assistant with access to specialized skills.

When responding to user queries:
1. Analyze if the query matches any available skill's purpose
2. If a skill is activated, follow its instructions precisely
3. Use the skill's capabilities to provide accurate, helpful responses
4. If no skill matches, respond normally using your general knowledge

Current date: {datetime.now().strftime("%Y-%m-%d")}
Current time: {datetime.now().strftime("%H:%M:%S")}

"""
        
        # Add skills XML from SkillLoader
        skills_xml = self.skill_loader.generate_skills_xml()
        prompt = base_prompt + skills_xml + "\n"
        
        # If a skill is activated, add its full SKILL.md content
        if activated_skill:
            skill = self.skill_loader.get_skill(activated_skill)
            if skill and skill.skill_md_content:
                prompt += f"\n# ACTIVATED SKILL: {activated_skill}\n\n"
                prompt += "## Skill Instructions:\n\n"
                prompt += skill.skill_md_content
                prompt += "\n\n## End of Skill Instructions\n"
                prompt += f"\nYou MUST follow the above skill instructions for this query.\n"
        
        return prompt
    
    # ========================================================================
    # STEP 5: Execute scripts and access resources as needed
    # Reference: https://agentskills.io/integrate-skills#overview
    # ========================================================================
    
    def step5_execute_calendar_skill(self, user_query: str) -> dict:
        """
        STEP 5: Execute calendar skill scripts and access resources
        
        Args:
            user_query: User's calendar request
            
        Returns:
            Dict with execution results: success, output, resources_used
        """
        if not self.calendar_skill:
            return {
                'success': False,
                'error': 'Calendar skill not available',
                'resources_used': []
            }
        
        execution_info = {
            'tool_used': 'natural_language_to_ics',
            'resources_used': [],
            'execution_time': datetime.now().isoformat()
        }
        
        try:
            ics_content, error, parsed_data = self.calendar_skill.natural_language_to_ics(user_query)
            
            if error:
                execution_info['success'] = False
                execution_info['error'] = error
                return execution_info
            
            execution_info['success'] = True
            execution_info['parsed_data'] = parsed_data
            execution_info['output_size'] = len(ics_content)
            execution_info['ics_content'] = ics_content
            
            # Check what resources were potentially accessed
            skill = self.skill_loader.get_skill('calendar-assistant')
            if skill:
                if (skill.skill_path / 'references').exists():
                    execution_info['resources_used'].append('references/ available')
                if (skill.skill_path / 'assets').exists():
                    execution_info['resources_used'].append('assets/ available')
            
            return execution_info
        
        except Exception as e:
            execution_info['success'] = False
            execution_info['error'] = str(e)
            return execution_info
    
    def step5_execute_ideagen_skill(self, user_query: str, temperature: float):
        """
        STEP 5: Execute IdeaGen skill scripts with streaming
        
        Args:
            user_query: User's idea generation request
            temperature: Creativity level
            
        Yields:
            Tuple of (chunk, execution_info)
        """
        if not self.ideagen_skill:
            yield "❌ IdeaGen skill not available", {'success': False, 'error': 'Skill not available'}
            return
        
        execution_info = {
            'tool_used': 'generate_ideas_stream',
            'resources_used': [],
            'execution_time': datetime.now().isoformat(),
            'success': True
        }
        
        try:
            # Parse query to extract parameters
            num_ideas_match = re.search(r'(\d+)\s+ideas?', user_query.lower())
            num_ideas = int(num_ideas_match.group(1)) if num_ideas_match and 1 <= int(num_ideas_match.group(1)) <= 10 else 5
            
            # Extract topic
            topic = re.sub(r'generate|brainstorm|give me|create|come up with|i need', '', user_query, flags=re.IGNORECASE)
            topic = re.sub(r'\d+\s+ideas?\s+(for|about|on)?', '', topic, flags=re.IGNORECASE)
            topic = topic.strip() or user_query
            
            execution_info['parameters'] = {
                'topic': topic,
                'num_ideas': num_ideas,
                'creativity': temperature
            }
            
            # Check what resources are available
            skill = self.skill_loader.get_skill('nvidia-ideagen')
            if skill:
                if (skill.skill_path / 'references').exists():
                    execution_info['resources_used'].append('references/ available')
                if (skill.skill_path / 'assets').exists():
                    execution_info['resources_used'].append('assets/ available')
            
            # Stream ideas generation
            for chunk in self.ideagen_skill.generate_ideas_stream(
                topic=topic,
                num_ideas=num_ideas,
                creativity=temperature
            ):
                yield chunk, execution_info
        
        except Exception as e:
            execution_info['success'] = False
            execution_info['error'] = str(e)
            yield f"❌ Error executing idea generation skill: {str(e)}", execution_info
    
    def chat_stream(
        self, 
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Process user query with streaming response
        Implements the 5-step Agent Skills process with visible progress
        
        Args:
            user_query: User's question or request
            temperature: LLM temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Tuple of (response_chunk, step_info_dict, ics_content_bytes)
            step_info includes: step, skill_name, details
        """
        # Display steps progress header
        progress_header = """**🔄 Agent Skills Process**
        
Following the 5-step integration from [agentskills.io](https://agentskills.io/integrate-skills#overview):

"""
        yield progress_header, {'step': 'header'}, None
        
        # ===== STEP 1 & 2: Already done at startup =====
        step_info = {
            'step': 1,
            'name': 'Discover & Load',
            'status': 'completed',
            'details': f'Found {len(self.skills)} skills: {", ".join([s.name for s in self.skills])}'
        }
        yield f"**✅ Steps 1-2: Discover & Load Metadata** - {step_info['details']}\n\n", step_info, None
        
        # ===== STEP 3: Match user task to relevant skill =====
        step_info = {'step': 3, 'name': 'Match', 'status': 'in_progress'}
        yield f"**⏳ Step 3: Matching Task to Skill** - Analyzing query...\n", step_info, None
        
        matched_skill, match_info = self.step3_match_skill(user_query)
        
        if matched_skill:
            step_info['status'] = 'completed'
            step_info['skill_name'] = matched_skill
            step_info['details'] = match_info['reasoning']
            yield f"**✅ Step 3: Match Complete** - Selected skill: `{matched_skill}` ({match_info['reasoning']})\n\n", step_info, None
        else:
            step_info['status'] = 'skipped'
            step_info['details'] = match_info['reasoning']
            yield f"**⊘ Step 3: No Skill Match** - {match_info['reasoning']}, using general AI response\n\n", step_info, None
            
            # No skill matched, use general LLM
            system_prompt = self.build_system_prompt()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
            
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    top_p=0.95,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                yield "**💬 Response:**\n\n", {'step': 'response'}, None
                
                for chunk in completion:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content, {'step': 'response'}, None
            except Exception as e:
                yield f"\n\n❌ Error: {str(e)}", {'step': 'error'}, None
            return
        
        # ===== STEP 4: Activate skill by loading full instructions =====
        step_info = {'step': 4, 'name': 'Activate', 'status': 'in_progress', 'skill_name': matched_skill}
        yield f"**⏳ Step 4: Activating Skill** - Loading `{matched_skill}` instructions...\n", step_info, None
        
        activation_info = self.step4_activate_skill(matched_skill)
        
        if activation_info['success']:
            step_info['status'] = 'completed'
            step_info['details'] = f"Loaded {activation_info['tools_discovered']} tools, {activation_info['content_length']} chars of instructions"
            yield f"**✅ Step 4: Activation Complete** - {step_info['details']}\n\n", step_info, None
        else:
            step_info['status'] = 'failed'
            step_info['error'] = activation_info.get('error', 'Unknown error')
            yield f"**❌ Step 4: Activation Failed** - {step_info['error']}\n\n", step_info, None
            return
        
        # ===== STEP 5: Execute scripts and access resources =====
        step_info = {'step': 5, 'name': 'Execute', 'status': 'in_progress', 'skill_name': matched_skill}
        yield f"**⏳ Step 5: Executing Skill** - Running `{matched_skill}` tools...\n\n", step_info, None
        
        yield "---\n\n**📤 Skill Output:**\n\n", {'step': 'output'}, None
        
        # Execute based on skill type
        if matched_skill == "calendar-assistant":
            exec_info = self.step5_execute_calendar_skill(user_query)
            
            if exec_info['success']:
                # Generate success message
                parsed_data = exec_info['parsed_data']
                success_msg = f"""✅ **Calendar Event Created!**

📅 **Event Details:**
- **Title:** {parsed_data['summary']}
- **Date:** {parsed_data['start_date']}
- **Time:** {parsed_data.get('start_time', 'All day')}
- **Duration:** {parsed_data.get('duration_hours', 1)} hours
- **Location:** {parsed_data.get('location', 'Not specified')}
- **Description:** {parsed_data.get('description', 'Not specified')}
- **Reminder:** {parsed_data.get('reminder_hours', 1)} hours before

📥 **Download the .ics file** using the button on the right →

---

**ℹ️ Execution Info:** Used tool `{exec_info['tool_used']}`, generated {exec_info['output_size']} bytes"""
                
                step_info['status'] = 'completed'
                yield success_msg, step_info, exec_info['ics_content']
            else:
                step_info['status'] = 'failed'
                yield f"❌ Error: {exec_info.get('error', 'Unknown error')}", step_info, None
        
        elif matched_skill == "nvidia-ideagen":
            for chunk, exec_info in self.step5_execute_ideagen_skill(user_query, temperature):
                step_info['status'] = 'executing'
                yield chunk, step_info, None
            
            # Mark as completed
            step_info['status'] = 'completed'
            yield f"\n\n---\n\n**ℹ️ Execution Info:** Used tool `{exec_info['tool_used']}` with parameters: {exec_info.get('parameters', {})}", step_info, None


class GradioUI:
    """Gradio UI for Agent Skills Chatbot"""
    
    def __init__(self, chatbot: AgentSkillsChatbot):
        self.chatbot = chatbot
    
    def save_ics_file(self, ics_content: bytes, summary: str = "event") -> str:
        """Save ICS content to a temporary file"""
        # Clean summary for filename
        safe_name = "".join(c for c in summary if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        safe_name = safe_name or "event"
        
        filename = f"event_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
        
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.ics')
        temp_file.write(ics_content)
        temp_file.close()
        
        return temp_file.name
    
    def process_message(
        self, 
        user_message: str, 
        history: List[List[str]],
        temperature: float
    ):
        """
        Process user message and stream response with 5-step progress
        
        Now displays each step of the Agent Skills process as it executes
        """
        if not user_message or not user_message.strip():
            yield history, None, ""
            return
        
        # Add user message to history
        history = history or []
        history.append([user_message, ""])
        
        # Stream response with step-by-step progress
        response = ""
        ics_content_bytes = None
        activated_skill = None
        
        for chunk, step_info, ics_bytes in self.chatbot.chat_stream(
            user_message, 
            temperature=temperature
        ):
            response += chunk
            
            # Track which skill was activated
            if step_info and 'skill_name' in step_info and not activated_skill:
                activated_skill = step_info['skill_name']
            
            # Update chat with current response
            history[-1][1] = response
            
            # Store ICS content if returned
            if ics_bytes:
                ics_content_bytes = ics_bytes
            
            yield history, None, ""
        
        # If we have ICS content, save it
        if ics_content_bytes:
            # Decode ICS content for preview
            ics_preview = ics_content_bytes.decode('utf-8')
            
            # Extract summary for filename
            summary_match = re.search(r'SUMMARY:(.*?)(?:\r?\n)', ics_preview)
            summary = summary_match.group(1) if summary_match else "event"
            
            # Save to temp file
            file_path = self.save_ics_file(ics_content_bytes, summary)
            
            # Return with file and preview
            yield history, file_path, ics_preview
            return
        
        # Final yield
        yield history, None, ""
    
    def clear_history(self):
        """Clear chat history"""
        return []
    
    def build_interface(self) -> gr.Blocks:
        """Build Gradio interface"""
        
        with gr.Blocks(title="Agent Skills Chatbot - Enhanced") as interface:
            
            gr.Markdown(
                """
                # 🤖 Agent Skills Chatbot - 5-Step Process Visualization
                
                Powered by **skill_loader.py** - Following [Agent Skills Integration Guide](https://agentskills.io/integrate-skills#overview)
                
                ## 🔄 The 5-Step Process:
                
                1. **Discover** - Scan directories for skills (at startup)
                2. **Load Metadata** - Parse skill names & descriptions (at startup)
                3. **Match** - Analyze query and select relevant skill
                4. **Activate** - Load full skill instructions and tools
                5. **Execute** - Run skill scripts and access resources
                
                *Watch the steps execute in real-time below!*
                
                ---
                
                ## 🎯 Available Skills:
                """
            )
            
            # Display discovered skills
            skills_info = ""
            for skill in self.chatbot.skills:
                skills_info += f"- **{skill.name}** ({skill.skill_type})\n"
                skills_info += f"  - {skill.description}\n"
            
            gr.Markdown(skills_info)
            
            gr.Markdown(
                """
                ---
                
                ### ✨ What You'll See:
                
                Each query triggers the **5-step Agent Skills process** visualized in real-time:
                
                - ✅ **Steps 1-2** are completed at startup (skills discovered and loaded)
                - ⏳ **Step 3** analyzes your query to find the best matching skill
                - ⏳ **Step 4** activates the chosen skill and loads its full capabilities
                - ⏳ **Step 5** executes the skill's tools and generates your result
                
                **Try it!** Ask a question and watch the process unfold step-by-step.
                
                ---
                """
            )
            
            # Chat interface
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
                    # Calendar file download
                    gr.Markdown("### 📅 Calendar Event")
                    ics_download = gr.File(
                        label="📥 Download .ics File",
                        visible=True,
                        interactive=False
                    )
                    gr.Markdown("""
                    **How to use:**
                    1. Download the .ics file
                    2. Double-click to open
                    3. Import to your calendar
                    """)
                    
                    # Examples
                    gr.Examples(
                        examples=[
                            "Schedule a team meeting tomorrow at 2pm for 2 hours",
                            "Create a dentist appointment next Monday at 10am",
                            "Book lunch Friday at noon with marketing team",
                            "Generate 3 ideas for sustainable urban living",
                            "I need ideas for a language learning mobile app",
                            "Brainstorm AI-powered productivity tools"
                        ],
                        inputs=user_input,
                        label="💡 Try these examples"
                    )
            
            # Settings
            with gr.Accordion("⚙️ Settings", open=False):
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="Temperature (creativity)",
                    info="Higher = more creative"
                )
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Chat")
            
            # Hidden preview textbox
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
                
                ### 🔧 Technical Details:
                
                **Architecture**: Implements the [Agent Skills Specification](https://agentskills.io/integrate-skills#overview)
                
                - **5-Step Process**: Discover → Load → Match → Activate → Execute
                - **Skill Loader**: `skill_loader.py` with `@skill_tool` auto-discovery
                - **LLM**: NVIDIA Llama 3.1 Nemotron Nano 8B
                - **Skills Format**: `config.yaml` + `SKILL.md` + `scripts/` + `references/` + `assets/`
                - **Tool Integration**: LangChain StructuredTool compatible
                
                ---
                
                💡 **Features**:
                - ✅ **Step-by-step visualization** of skill execution process
                - ✅ **Auto skill discovery** from directory structure
                - ✅ **Tool auto-discovery** with `@skill_tool` decorator
                - ✅ **Access control aware** via config.yaml
                - ✅ **Resource access** (read_reference, read_asset)
                - ✅ **Streaming responses** with real-time progress
                
                📚 **Reference**: [agentskills.io/integrate-skills](https://agentskills.io/integrate-skills#overview)
                """
            )
        
        return interface


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("Agent Skills Chatbot - Enhanced with SkillLoader")
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
    
    print(f"📂 Project directory: {project_dir}")
    
    try:
        # Initialize chatbot with SkillLoader
        chatbot = AgentSkillsChatbot(
            skills_base_path=str(project_dir),
            api_key=api_key
        )
        
        # Display discovered skills summary
        print("\n📋 Skills Summary:")
        for skill in chatbot.skills:
            print(f"\n  🎯 {skill.name}")
            print(f"     Type: {skill.skill_type}")
            print(f"     Version: {skill.skill_md_metadata.get('version', 'unknown')}")
            print(f"     Description: {skill.description[:100]}...")
        
        # Discover tools for each skill
        print("\n🔧 Discovered Tools:")
        for skill in chatbot.skills:
            tools = chatbot.skill_loader.discover_tools(skill.name)
            if tools:
                print(f"\n  📦 {skill.name}: {len(tools)} tool(s)")
                for tool in tools[:3]:  # Show first 3
                    print(f"     - {tool._tool_name}")
        
        print("\n" + "="*80)
        print("✅ Initialization complete! Launching Gradio interface...")
        print("="*80 + "\n")
        
        # Build and launch UI
        ui = GradioUI(chatbot)
        interface = ui.build_interface()
        
        # Launch
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
