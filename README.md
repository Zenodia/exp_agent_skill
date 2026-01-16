# ExpAgentSkill - AI Agent Skills Playground

Experimental AI Agent Skills implementations following the [Agent Skills specification](https://agentskills.io).

## 📦 What's Included

### 1. **Calendar Assistant Skill** 
Natural language calendar event creation with iCalendar (ICS) file generation.

- **Location**: `calendar_assistant_skill/`
- **Features**: Parse natural language dates, create RFC 5545 compliant events
- **Integration**: Gradio app, command-line, notebooks

### 2. **NVIDIA Idea Generation Skill** ⭐ NEW
AI-powered brainstorming and idea generation using NVIDIA's Nemotron model.

- **Location**: `nvidia_ideagen_skill/` (metadata) + `ideagen_skill.py` (implementation)
- **Features**: Generate ideas, brainstorm with constraints, expand ideas, save library
- **Integration**: Gradio app with Excalidraw, Agent Skills compliant

### 3. **Agent Skills Chatbot** 🤖 NEW
Intelligent chatbot demonstrating agentic tool usage with dynamic skill discovery.

- **File**: `gradio_agent_chatbot.py`
- **Features**: Auto skill detection, streaming responses, Agent Skills compliant
- **Integration**: NVIDIA Nemotron model, both calendar and ideagen skills

### 4. **Excalidraw Drawing Board**
Interactive whiteboard with embedded Excalidraw + AI idea generation.

- **File**: `excalidraw_gradio_app.py`
- **Features**: Hand-drawn diagrams, PNG/JSON export, integrated idea generation

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements_excalidraw.txt

# Set NVIDIA API key (for idea generation)
# Windows PowerShell:
$env:NVIDIA_API_KEY="your-api-key-here"

# Linux/Mac:
export NVIDIA_API_KEY='your-api-key-here'
```

Get your NVIDIA API key at: https://build.nvidia.com/

### Run the Apps

**Agent Skills Chatbot (Port 7860) - RECOMMENDED:**
```bash
python gradio_agent_chatbot.py
# Or use the launcher with pre-flight checks:
python launch_gradio_app.py
```

**Excalidraw + Idea Generation (Port 7861):**
```bash
python excalidraw_gradio_app.py
```

**Calendar Assistant (Port 7860):**
```bash
python calendar_gradio_app_with_skill.py
```

### Test the Skills

**Test NVIDIA Idea Generation Skill:**
```bash
python test_ideagen_skill.py
```

**Test Standalone Idea Generation:**
```bash
python ideagen_skill.py
```

## 📁 Project Structure

```
ExpAgentSkill/
├── calendar_assistant_skill/      # Calendar skill (Agent Skills compliant)
│   ├── SKILL.md                   # Skill metadata + instructions
│   ├── README.md                  # Documentation
│   ├── examples.md                # Usage examples
│   ├── requirements.txt           # Dependencies
│   └── scripts/
│       └── calendar_skill.py      # Implementation
│
├── nvidia_ideagen_skill/          # Idea generation skill (Agent Skills compliant)
│   ├── SKILL.md                   # Skill metadata + instructions
│   ├── README.md                  # Documentation
│   ├── examples.md                # Usage examples
│   └── requirements.txt           # Dependencies
│
├── ideagen_skill.py               # Idea generation implementation (root level)
├── test_ideagen_skill.py          # Agent Skills compliance tests
├── test_skill.py                  # Comprehensive skill testing
│
├── gradio_agent_chatbot.py        # Gradio app: Agent Skills Chatbot (RECOMMENDED)
├── launch_gradio_app.py           # Launcher with pre-flight checks
├── excalidraw_gradio_app.py       # Gradio app: Drawing + Idea Generation
├── calendar_gradio_app_with_skill.py  # Gradio app: Calendar Assistant
│
├── requirements_gradio.txt        # Chatbot dependencies
├── requirements_excalidraw.txt    # Excalidraw app dependencies
├── GRADIO_APP_README.md           # Chatbot documentation
├── AGENT_SKILLS_INTEGRATION.md    # Integration guide
└── README.md                      # This file
```

## 🎯 Agent Skills Integration

Both skills follow the [Agent Skills specification](https://agentskills.io/integrate-skills):

### Discovery Phase
Agents scan for `SKILL.md` files to discover available skills:

```python
from ideagen_skill import discover_skills

skills = discover_skills(["/path/to/skills"])
# Returns: [{"name": "nvidia-ideagen", "description": "...", "location": "..."}]
```

### Injection Phase
Skill metadata is injected into agent system prompts:

```python
from ideagen_skill import generate_skills_xml

xml = generate_skills_xml(skills)
# Returns: <available_skills>...</available_skills>
```

### Activation Phase
When needed, agents read full `SKILL.md` for detailed instructions:

```bash
cat nvidia_ideagen_skill/SKILL.md
```

### Execution Phase
Agents call the implementation following SKILL.md guidance:

```python
from ideagen_skill import NvidiaIdeaGenSkill

skill = NvidiaIdeaGenSkill()
ideas = skill.generate_ideas("sustainable transportation", num_ideas=5)
```

See [AGENT_SKILLS_INTEGRATION.md](AGENT_SKILLS_INTEGRATION.md) for complete details.

## 🎨 Applications

### 1. Agent Skills Chatbot (RECOMMENDED)

**Features:**
- 🤖 Intelligent skill detection and activation
- 💬 Natural language conversation interface
- 🎯 Auto-routing to calendar or ideagen skills
- 📡 Streaming responses for better UX
- 🔧 Agent Skills API compliant prompt integration
- ⚙️ Adjustable creativity settings

**Usage:**
```bash
python gradio_agent_chatbot.py
# Or with pre-flight checks:
python launch_gradio_app.py
# Opens at http://localhost:7860
```

**Example queries:**
- "Generate 3 ideas for sustainable urban living"
- "Schedule a team meeting tomorrow at 2pm"
- "Brainstorm concepts for AI productivity tools"
- "Book a lunch meeting Friday at noon"

See [GRADIO_APP_README.md](GRADIO_APP_README.md) for complete documentation.

### 2. Excalidraw + AI Idea Generation

**Features:**
- ✏️ Hand-drawn style whiteboard (Excalidraw)
- 💡 AI idea generation (NVIDIA Nemotron)
- 🧠 Deep brainstorming with constraints
- 🔍 Idea expansion (detailed, technical, creative, business)
- 💾 Save drawings and ideas
- 📊 Library management

**Usage:**
```bash
python excalidraw_gradio_app.py
# Opens at http://localhost:7861
```

### 3. Calendar Assistant

**Features:**
- 🗣️ Natural language event parsing
- 📅 RFC 5545 compliant ICS generation
- 🌍 Multi-timezone support
- ⏰ Configurable reminders
- 👥 Attendee management

**Usage:**
```bash
python calendar_gradio_app_with_skill.py
# Opens at http://localhost:7860
```

## 📚 Documentation

- **[AGENT_SKILLS_INTEGRATION.md](AGENT_SKILLS_INTEGRATION.md)**: Complete integration guide
- **[nvidia_ideagen_skill/SKILL.md](nvidia_ideagen_skill/SKILL.md)**: Idea generation skill instructions
- **[nvidia_ideagen_skill/README.md](nvidia_ideagen_skill/README.md)**: Idea generation documentation
- **[nvidia_ideagen_skill/examples.md](nvidia_ideagen_skill/examples.md)**: Usage examples
- **[calendar_assistant_skill/SKILL.md](calendar_assistant_skill/SKILL.md)**: Calendar skill instructions
- **[calendar_assistant_skill/README.md](calendar_assistant_skill/README.md)**: Calendar documentation
- **[EXCALIDRAW_README.md](EXCALIDRAW_README.md)**: Excalidraw integration guide

## 🧪 Testing

### Test NVIDIA Idea Generation Skill

```bash
python test_ideagen_skill.py
```

Verifies:
- ✅ Skill directory structure
- ✅ SKILL.md with proper frontmatter
- ✅ Skill discovery mechanism
- ✅ XML generation for system prompts
- ✅ System prompt integration
- ✅ Implementation functionality
- ✅ Agent Skills specification compliance

### Manual Testing

**Test idea generation:**
```bash
python ideagen_skill.py
```

**Test calendar skill:**
```bash
cd calendar_assistant_skill/scripts
python calendar_skill.py
```

## 🔑 API Keys

### NVIDIA API Key (Required for Idea Generation)

1. Visit https://build.nvidia.com/
2. Sign up/log in (free)
3. Get your API key
4. Set environment variable:

```powershell
# Windows PowerShell
$env:NVIDIA_API_KEY="your-key-here"
```

```bash
# Linux/Mac
export NVIDIA_API_KEY='your-key-here'
```

### Calendar Skill

Optional: Set `NVIDIA_API_KEY` for natural language parsing.  
Works without API key using structured input only.

## 💡 Usage Examples

### Idea Generation in Python

```python
from ideagen_skill import NvidiaIdeaGenSkill

skill = NvidiaIdeaGenSkill()

# Generate ideas
ideas = skill.generate_ideas(
    topic="mobile apps for remote work",
    num_ideas=5,
    creativity=0.7
)
print(ideas)

# Brainstorm with constraints
for chunk in skill.brainstorm_concepts(
    domain="Healthcare Technology",
    focus_area="Patient monitoring",
    constraints=["Must be cost-effective", "Should work offline"]
):
    print(chunk, end="", flush=True)

# Expand an idea
for chunk in skill.expand_idea(
    idea="A platform for local food delivery",
    expansion_type="business"
):
    print(chunk, end="", flush=True)
```

### Calendar Events in Python

```python
from calendar_assistant_skill.scripts.calendar_skill import CalendarAssistantSkill

skill = CalendarAssistantSkill(api_key="your-key")

# Natural language
ics, error, data = skill.natural_language_to_ics(
    "Schedule a team meeting tomorrow at 2pm for 2 hours"
)

if not error:
    with open("meeting.ics", "wb") as f:
        f.write(ics)
```

## 🎓 Learning Resources

### Agent Skills
- **Specification**: https://agentskills.io
- **Integration Guide**: https://agentskills.io/integrate-skills
- **Python Reference**: https://github.com/agentskills/agentskills

### Inspiration
- **DeepTutor**: https://github.com/Zenodia/DeepTutor (IdeaGen module inspiration)
- **Excalidraw**: https://excalidraw.com/
- **NVIDIA Build**: https://build.nvidia.com/

## 🤝 Agent Skills Compliance

Both skills are fully compliant with the Agent Skills specification:

- ✅ `SKILL.md` with YAML frontmatter
- ✅ Structured directory layout
- ✅ Comprehensive documentation
- ✅ Clear capability definitions
- ✅ Environment variable configuration
- ✅ Detailed examples
- ✅ Error handling and validation
- ✅ Progressive disclosure (metadata → full instructions)

## 🔮 Future Enhancements

### Idea Generation Skill
- [ ] Multi-model support (OpenAI, Anthropic, local models)
- [ ] Knowledge base integration
- [ ] Idea combination and synthesis
- [ ] Template-based generation
- [ ] Export to PDF/DOCX

### Calendar Skill
- [ ] Recurring events support
- [ ] Event conflict detection
- [ ] Calendar file merging
- [ ] Video conferencing links
- [ ] Multi-language support

### Integration
- [ ] Cross-skill workflows
- [ ] Shared context between skills
- [ ] Skill composition patterns

## 📄 License

MIT License - See individual skill directories for details

## 🙏 Acknowledgments

- **Agent Skills Community** - Specification and standards
- **NVIDIA** - Nemotron model and API
- **DeepTutor Team** - IdeaGen module inspiration
- **Excalidraw** - Whiteboard component
- **Gradio Team** - UI framework

---

**Built with ❤️ for the Agent Skills ecosystem**

*Experimental playground for Agent Skills implementations*

