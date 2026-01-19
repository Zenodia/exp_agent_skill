---
name: example-optimizer
version: 1.0.0
description: An example optimization skill demonstrating custom task agent architecture with specialized agents for data preparation, optimization, and explanation.
author: Example Team
license: MIT
---

# Example Optimizer Skill (Full Custom)

This is an example demonstrating the **Full Custom** skill tier with customized task agents.

## Architecture

This skill uses three specialized agents working in sequence:

```
User Request → Data Preparer → Optimizer → Explainer → User
```

### Agent 1: Data Preparer
**Role**: Data analyst and preparation specialist

**Responsibilities**:
- Load and validate input data
- Transform data to optimization-ready format
- Handle missing values and outliers
- Ensure data meets constraints

**Tools**:
- `load_dataset`: Load data from various sources
- `validate_data`: Check data quality
- `transform_data`: Prepare for optimization
- `read_reference`, `read_asset`: Access skill resources

### Agent 2: Optimizer
**Role**: Optimization engine specialist

**Responsibilities**:
- Select appropriate optimization algorithm
- Configure optimization parameters
- Run optimization solver (cuOpt, SciPy, OR-Tools)
- Validate solution feasibility

**Tools**:
- `run_optimization`: Execute optimization
- `validate_solution`: Check feasibility
- `adjust_parameters`: Tune if needed

### Agent 3: Explainer
**Role**: Results interpreter and communicator

**Responsibilities**:
- Interpret optimization results
- Generate business-friendly summaries
- Create visualizations
- Provide actionable recommendations

**Tools**:
- `generate_summary`: Create result summary
- `create_visualization`: Generate charts
- `explain_decision`: Explain why solutions work
- `list_resources`: Show available references

## When to Use This Skill

Use this skill when:
- You need to solve optimization problems (routing, scheduling, resource allocation)
- Data preparation is complex and needs validation
- Results need clear explanation for stakeholders
- You want separation of concerns (data, optimization, explanation)

## Example Usage

### AI Planner Integration

```python
from skill_loader import SkillLoader

# Initialize loader
loader = SkillLoader("path/to/ExpAgentSkill")

# Get skill
skill = loader.get_skill("example-optimizer")

# Check user access
user_groups = ["engineering-team"]
has_access = skill.check_access(user_groups)

# Discover tools (will find custom task agents)
tools = loader.discover_tools("example-optimizer")
```

### Custom Agent Workflow

```python
# 1. Data Preparer Agent processes input
data_agent = skill.config["custom_settings"]["task_agents"][0]
# Agent has tools: load_dataset, validate_data, transform_data

# 2. Optimizer Agent solves problem
optimizer_agent = skill.config["custom_settings"]["task_agents"][1]
# Agent has tools: run_optimization, validate_solution

# 3. Explainer Agent presents results
explainer_agent = skill.config["custom_settings"]["task_agents"][2]
# Agent has tools: generate_summary, create_visualization
```

## Dataset Registry

The skill provides access to curated datasets:

- **historical_data**: Historical optimization data
- **constraints_library**: Standard constraint formulations
- **optimization_guide**: Best practices reference
- **example_problems**: Sample problems for testing

Access via resource tools: `read_reference`, `read_asset`, `list_resources`

## Configuration Options

Customize via `config.yaml`:

```yaml
custom_settings:
  task_agents:
    - name: data_preparer
      temperature: 0.3
      max_iterations: 5
      tools: [...]
```

Adjust per your needs:
- **temperature**: Control creativity (0.0-1.0)
- **max_iterations**: Limit agent steps
- **tools**: Assign specific tools to agents

## Access Control

This example demonstrates access control:

```yaml
user_group: 
  - engineering-team
  - data-science-team
admin_group:
  - ai-planner-admins
```

Only specified groups can use this skill.

## Comparison: Generic vs Custom

### Generic Skill (React Agent)
- ✅ Simple to set up
- ✅ Auto-discovers @skill_tool functions
- ✅ Built-in resource tools
- ❌ Single agent for all tasks
- ❌ Limited specialization

### Custom Skill (This Example)
- ✅ Multiple specialized agents
- ✅ Clear separation of concerns
- ✅ Agent-specific instructions and tools
- ✅ Complex workflows
- ❌ More configuration required
- ❌ Must define task agents

## Next Steps

To create your own Full Custom skill:

1. **Copy this template**
   ```bash
   cp -r examples/custom_skill_example my_custom_skill
   ```

2. **Modify config.yaml**
   - Define your task agents
   - Assign tools to each agent
   - Set up datasets registry

3. **Implement tools** in `scripts/`
   - Create @skill_tool decorated functions
   - Implement agent-specific logic

4. **Add resources**
   - Put documentation in `references/`
   - Put data files in `assets/`

5. **Test with AI Planner**
   - Load skill via SkillLoader
   - Test agent coordination
   - Validate access control

## Resources

- **Skill Loader**: `skill_loader.py`
- **Configuration Guide**: `docs/custom_skills_guide.md`
- **AI Planner Integration**: Link to internal docs
- **cuOpt Documentation**: https://docs.nvidia.com/cuopt/

---

**Note**: This is a template/example. Implement actual optimization logic as needed for your use case.

