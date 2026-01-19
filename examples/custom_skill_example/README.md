# Example Optimizer Skill - Full Custom Tier

This is a **reference implementation** demonstrating the **Full Custom** skill tier for AI Planner / NAT integration.

## Purpose

This example shows how to create a skill with:
- **Multiple specialized agents** (data_preparer, optimizer, explainer)
- **Sequential agent coordination**
- **Dataset registry** with access control
- **Agent-specific tools and instructions**
- **Resource access** (references and assets)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                Example Optimizer Skill               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────┐                                │
│  │  Data Preparer  │  Load, validate, transform     │
│  │     Agent       │  Temperature: 0.3              │
│  └────────┬────────┘                                │
│           │                                          │
│           ▼                                          │
│  ┌─────────────────┐                                │
│  │   Optimizer     │  Run cuOpt/SciPy/OR-Tools      │
│  │     Agent       │  Temperature: 0.2              │
│  └────────┬────────┘                                │
│           │                                          │
│           ▼                                          │
│  ┌─────────────────┐                                │
│  │   Explainer     │  Summarize, visualize          │
│  │     Agent       │  Temperature: 0.6              │
│  └─────────────────┘                                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Key Features

### 1. Multi-Agent Architecture

Three specialized agents with distinct roles:

**Data Preparer**:
- Tools: `load_dataset`, `validate_data`, `transform_data`
- Temperature: 0.3 (conservative)
- Max iterations: 5

**Optimizer**:
- Tools: `run_optimization`, `validate_solution`, `adjust_parameters`
- Temperature: 0.2 (very conservative)
- Max iterations: 10

**Explainer**:
- Tools: `generate_summary`, `create_visualization`, `explain_decision`
- Temperature: 0.6 (balanced)
- Max iterations: 3

### 2. Dataset Registry

Curated datasets with access control:

```yaml
datasets:
  - name: historical_data
    type: asset
    access_control: user_group
  
  - name: constraints_library
    type: reference
    access_control: all
```

### 3. Access Control

```yaml
user_group: 
  - engineering-team
  - data-science-team
admin_group:
  - ai-planner-admins
```

Only authorized users can access this skill.

### 4. Resource Access Tools

Built-in tools automatically added:
- `read_reference`: Read docs from references/
- `read_asset`: Read data from assets/
- `list_resources`: List available resources

## Directory Structure

```
custom_skill_example/
├── config.yaml              # Skill configuration with custom agents
├── SKILL.md                 # Skill instructions and metadata
├── README.md                # This file
├── scripts/
│   ├── __init__.py
│   └── optimizer_skill.py   # Implementation with @skill_tool functions
├── references/
│   ├── constraints.md       # Constraint formulations
│   └── optimization_best_practices.md
└── assets/
    ├── historical_data.csv
    └── example_problems/
        ├── routing_problem.json
        └── scheduling_problem.json
```

## Configuration Breakdown

### Task Agents Definition

```yaml
task_agents:
  - name: data_preparer
    role: "Data analyst and preparation specialist"
    instructions: |
      You are a data preparation expert...
    tools:
      - load_dataset
      - validate_data
      - transform_data
    temperature: 0.3
    max_iterations: 5
```

### Coordination Strategy

```yaml
coordination:
  type: "sequential"
  flow:
    - data_preparer -> optimizer
    - optimizer -> explainer
  error_handling: "retry_with_context"
```

## Usage with AI Planner

### 1. Load Skill

```python
from skill_loader import SkillLoader

loader = SkillLoader("path/to/ExpAgentSkill")
skill = loader.get_skill("example-optimizer")
```

### 2. Check Access

```python
user_groups = ["engineering-team"]
has_access = skill.check_access(user_groups)
```

### 3. Get Custom Agents

```python
custom_settings = skill.config["custom_settings"]
task_agents = custom_settings["task_agents"]

for agent in task_agents:
    print(f"Agent: {agent['name']}")
    print(f"Role: {agent['role']}")
    print(f"Tools: {agent['tools']}")
```

### 4. Discover Tools

```python
tools = loader.discover_tools("example-optimizer")
# Returns @skill_tool decorated functions from scripts/
```

### 5. Access Resources

```python
# Built-in resource tools are automatically added
# when enable_resource_tools: true in config
```

## Comparison with Generic Skills

| Aspect | Generic Skill | Custom Skill (This Example) |
|--------|---------------|----------------------------|
| Agents | 1 ReAct agent | 3 specialized agents |
| Configuration | Minimal | Detailed agent definitions |
| Tool Assignment | Auto-discover all | Assign specific tools per agent |
| Workflow | Flat | Sequential/hierarchical |
| Use Case | Simple tasks | Complex multi-step workflows |
| Setup Time | Minutes | Hours |
| Flexibility | Medium | High |

## When to Use Full Custom

Choose Full Custom when:
- ✅ Task requires multiple specialized roles
- ✅ Clear separation of concerns needed
- ✅ Different agents need different configurations
- ✅ Complex workflows with coordination
- ✅ Agent-specific instructions are valuable
- ✅ Data access needs fine-grained control

Stick with Generic when:
- ✅ Simple, single-purpose tasks
- ✅ Rapid prototyping
- ✅ Standard ReAct pattern sufficient
- ✅ No need for agent specialization

## Extending This Example

### Add More Agents

```yaml
task_agents:
  - name: validator
    role: "Solution validator"
    instructions: "Validate optimization results..."
    tools: [validate_constraints, check_feasibility]
```

### Change Coordination

```yaml
coordination:
  type: "hierarchical"  # Add coordinator agent
  coordinator: planner_agent
  workers: [data_preparer, optimizer, explainer]
```

### Add Datasets

```yaml
datasets:
  - name: my_new_dataset
    type: asset
    path: assets/my_data.parquet
    description: "Custom dataset"
    access_control: admin_group
```

## Testing

```bash
# Test skill discovery
python skill_loader.py

# Test custom skill
cd examples/custom_skill_example
python scripts/optimizer_skill.py
```

## Real-World Inspiration

This example is inspired by:
- **Supply chain optimization** (mentioned in user's context)
- **cuOpt integration** for routing/scheduling
- **Data access controls** for sensitive datasets
- **Multi-agent workflows** in AI Planner

## Resources

- **AI Planner Design Doc**: [link]
- **Skills Documentation**: `../../README.md`
- **Skill Loader**: `../../skill_loader.py`
- **cuOpt Documentation**: https://docs.nvidia.com/cuopt/

## License

MIT

---

**Note**: This is a template. Implement actual optimization logic as needed.

