# Agent Skills - 5-Step Process Flow Diagram

## 📊 Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER SUBMITS QUERY                           │
│          "Schedule a team meeting tomorrow at 2pm"              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1-2: DISCOVER & LOAD METADATA (Already Done at Startup)  │
├─────────────────────────────────────────────────────────────────┤
│  📂 Scanned: ExpAgentSkill/                                     │
│  ✅ Found: calendar_assistant_skill/SKILL.md                    │
│  ✅ Found: nvidia_ideagen_skill/SKILL.md                        │
│                                                                 │
│  📋 Loaded Metadata:                                            │
│     • calendar-assistant: "A comprehensive calendar..."        │
│     • nvidia-ideagen: "AI-powered idea generation..."          │
│                                                                 │
│  💾 Status: 2 skills ready                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: MATCH USER TASK TO RELEVANT SKILL                     │
├─────────────────────────────────────────────────────────────────┤
│  🔍 Analyzing Query: "Schedule a team meeting..."               │
│                                                                 │
│  🎯 Keyword Matching:                                           │
│     ├─ calendar-assistant:                                      │
│     │   ✓ "schedule" found                                     │
│     │   ✓ "meeting" found                                      │
│     │   → Score: 2                                             │
│     │                                                           │
│     └─ nvidia-ideagen:                                          │
│         ✗ No matches                                            │
│         → Score: 0                                              │
│                                                                 │
│  ✅ BEST MATCH: calendar-assistant (score: 2)                  │
│     Reasoning: "Matched 2 keywords: schedule, meeting"         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: ACTIVATE SKILL (Load Full Instructions)               │
├─────────────────────────────────────────────────────────────────┤
│  ⚡ Loading: calendar-assistant                                 │
│                                                                 │
│  📖 Reading SKILL.md:                                           │
│     • Full content: 3,200 characters                           │
│     • Capabilities: Natural language → ICS                     │
│     • Usage examples: Meetings, appointments, deadlines        │
│                                                                 │
│  🔧 Discovering Tools:                                          │
│     • natural_language_to_ics                                  │
│     • create_calendar_event                                    │
│     • parse_calendar_event                                     │
│     • read_reference                                           │
│     → Total: 4 tools                                           │
│                                                                 │
│  📁 Checking Resources:                                         │
│     ✓ references/ directory exists                             │
│     ✓ assets/ directory exists                                 │
│                                                                 │
│  ✅ ACTIVATION COMPLETE                                         │
│     Status: Ready to execute with 4 tools                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: EXECUTE SCRIPTS & ACCESS RESOURCES                    │
├─────────────────────────────────────────────────────────────────┤
│  🚀 Executing Tool: natural_language_to_ics                     │
│                                                                 │
│  📥 Input:                                                      │
│     Query: "Schedule a team meeting tomorrow at 2pm"           │
│                                                                 │
│  ⚙️ Processing:                                                 │
│     1. Parse natural language with LLM                         │
│     2. Extract event details:                                  │
│        • Summary: "Team Meeting"                               │
│        • Date: 2026-01-20                                      │
│        • Time: 14:00                                           │
│        • Duration: 1 hour                                      │
│     3. Generate ICS file format                                │
│     4. Add VEVENT components                                   │
│     5. Set reminders (1 hour before)                           │
│                                                                 │
│  📤 Output Generated:                                           │
│     • ICS file: 524 bytes                                      │
│     • Format: iCalendar RFC 5545                               │
│     • Compatible with: Google Cal, Outlook, Apple Cal          │
│                                                                 │
│  📊 Resources Used:                                             │
│     • references/ available (not accessed)                     │
│     • assets/ available (not accessed)                         │
│     • Tool: natural_language_to_ics                            │
│     • Execution time: 2026-01-19T15:30:45                      │
│                                                                 │
│  ✅ EXECUTION COMPLETE                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE TO USER                             │
├─────────────────────────────────────────────────────────────────┤
│  🔄 Agent Skills Process                                        │
│                                                                 │
│  ✅ Steps 1-2: Discover & Load Metadata                        │
│     Found 2 skills: calendar-assistant, nvidia-ideagen         │
│                                                                 │
│  ✅ Step 3: Match Complete                                     │
│     Selected: calendar-assistant (Matched 2 keywords)          │
│                                                                 │
│  ✅ Step 4: Activation Complete                                │
│     Loaded 4 tools, 3200 chars of instructions                 │
│                                                                 │
│  ✅ Step 5: Execution Complete                                 │
│     Running calendar-assistant tools...                        │
│                                                                 │
│  ───────────────────────────────────────                       │
│                                                                 │
│  📤 Skill Output:                                               │
│                                                                 │
│  ✅ Calendar Event Created!                                    │
│                                                                 │
│  📅 Event Details:                                             │
│  • Title: Team Meeting                                         │
│  • Date: 2026-01-20                                            │
│  • Time: 14:00                                                 │
│  • Duration: 1 hour                                            │
│  • Location: Not specified                                     │
│  • Description: Not specified                                  │
│  • Reminder: 1 hour before                                     │
│                                                                 │
│  📥 Download the .ics file using the button on the right →     │
│                                                                 │
│  ℹ️ Execution Info: Used tool natural_language_to_ics,        │
│     generated 524 bytes                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Step-by-Step Breakdown

### **STEP 1-2: Discover & Load** (Startup Only)
```
When:     At application startup
Duration: ~500ms
Output:   Dictionary of available skills with metadata
Status:   Shown as "✅ already completed" in UI
```

**What Happens:**
1. Scan `ExpAgentSkill/` directory
2. Find all folders with `SKILL.md` files
3. Parse YAML frontmatter for name and description
4. Load `config.yaml` for each skill
5. Store in `SkillLoader.skills` dictionary

**Displayed:**
```
✅ Steps 1-2: Discover & Load Metadata
   Found 2 skills: calendar-assistant, nvidia-ideagen
```

---

### **STEP 3: Match** (Per Query)
```
When:     For each user query
Duration: ~50ms
Output:   Best matching skill name + reasoning
Status:   Shown as "⏳" then "✅"
```

**What Happens:**
1. Convert query to lowercase
2. Check query against keyword triggers for each skill
3. Count keyword matches and score each skill
4. Return skill with highest score

**Displayed:**
```
⏳ Step 3: Matching Task to Skill - Analyzing query...
✅ Step 3: Match Complete
   Selected skill: `calendar-assistant`
   (Matched 2 keyword(s): schedule, meeting)
```

---

### **STEP 4: Activate** (Per Query)
```
When:     After successful match
Duration: ~100ms
Output:   Activation metadata (tools, instructions, resources)
Status:   Shown as "⏳" then "✅"
```

**What Happens:**
1. Retrieve skill from SkillLoader
2. Load full `SKILL.md` content (not just frontmatter)
3. Discover @skill_tool decorated functions
4. Check for references/ and assets/ directories
5. Prepare skill for execution

**Displayed:**
```
⏳ Step 4: Activating Skill - Loading `calendar-assistant` instructions...
✅ Step 4: Activation Complete
   Loaded 4 tools, 3200 chars of instructions
```

---

### **STEP 5: Execute** (Per Query)
```
When:     After successful activation
Duration: ~1-5 seconds (depends on skill)
Output:   Skill execution results (text, files, etc.)
Status:   Shown as "⏳" then "✅"
```

**What Happens:**
1. Call appropriate tool/function from skill
2. Pass user query and parameters
3. Skill accesses resources if needed (references/, assets/)
4. Generate output (text, ICS file, JSON, etc.)
5. Return results with execution metadata

**Displayed:**
```
⏳ Step 5: Executing Skill - Running `calendar-assistant` tools...

───

📤 Skill Output:

✅ Calendar Event Created!
...

ℹ️ Execution Info: Used tool `natural_language_to_ics`,
   generated 524 bytes
```

---

## 🔄 Alternative Flow: No Skill Match

```
STEP 3: MATCH
    ↓
    ✗ No keywords matched any skill
    ↓
⊘ Step 3: No Skill Match
   "No skill matched, using general AI response"
    ↓
Skip to General LLM Response
    ↓
Use NVIDIA Nemotron for general Q&A
```

---

## ⚠️ Error Handling Flow

```
Any Step Fails
    ↓
❌ Step X: Failed
   Error: [specific error message]
    ↓
Return error to user
    ↓
Suggest retry or provide debugging info
```

---

## 📊 Performance Metrics

| Step | Average Duration | UI Indicator |
|------|-----------------|--------------|
| 1-2 (Startup) | 500ms | ✅ (pre-completed) |
| 3 (Match) | 50ms | ⏳ → ✅ |
| 4 (Activate) | 100ms | ⏳ → ✅ |
| 5 (Execute) | 1-5s | ⏳ → ✅ |
| **Total** | **1.15-5.15s** | Complete flow |

---

## 🎨 Visual Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Completed successfully |
| ⏳ | In progress |
| ⊘ | Skipped (e.g., no match) |
| ❌ | Failed with error |
| 🔍 | Searching/analyzing |
| ⚡ | Loading/activating |
| 🚀 | Executing |
| 📤 | Output generated |

---

## 🔗 References

- **Agent Skills Specification**: https://agentskills.io/integrate-skills#overview
- **Implementation**: `gradio_agent_chatbot.py`
- **SkillLoader**: `skill_loader.py`
- **Test Suite**: `test_skill.py`

---

**Created**: January 19, 2026  
**Status**: ✅ Implementation Complete

