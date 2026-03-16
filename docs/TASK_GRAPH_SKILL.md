---
name: task-graph
description: DAG-based task planning and orchestration engine. Use when managing development tasks, tracking task dependencies, planning project milestones, or coordinating multi-step workflows via MCP tools.
origin: user
---

# TaskGraph - DAG Task Planning Engine

DAG-based task planning system for managing development tasks with dependency tracking, status transitions, and priority analysis. Exposed via MCP tools.

## When to Activate

- Creating and managing development tasks with dependencies
- Tracking task lifecycle and status transitions
- Planning project milestones and breaking down work
- Coordinating multi-step workflows with dependency constraints
- Querying highest-priority actionable tasks (ROI-based)

## MCP Tools Available

All tools are available via `mcp__task-graph__*` prefix.

### Task Management

| Tool | Description |
|------|-------------|
| `create_task` | Create a new task with dependencies |
| `list_tasks` | Paginated task listing with filters |
| `get_task_details` | Get full task context including dependencies |
| `revise_task_details` | Update task name, description, effort, value |
| `delete_task` | Remove a task |

### Workflow Operations

| Tool | Description |
|------|-------------|
| `claim_task` | Atomically claim a READY task |
| `submit_task_result` | Submit execution results |
| `review_task` | Approve or reject task in REVIEW state |
| `modify_task_dependencies` | Add/remove task dependencies (cycle-safe) |
| `suggest_next_action` | Get highest ROI actionable tasks |

## Critical: Project Isolation

**ALWAYS specify `project_id`** to isolate tasks by project. This prevents cross-project data contamination.

```
# CORRECT - Always use project_id
create_task(project_id="MyProject", name="...", ...)

# WRONG - Missing project_id causes data mixing
create_task(project_id="", name="...", ...)
```

### Recommended `project_id` Conventions

- Use the project's directory name or repository name
- Examples: `"TaskGraph"`, `"CodingAgent"`, `"agent-engine"`
- Keep consistent across all task operations in a project

## Automatic State Transitions

The system automatically manages state transitions based on dependencies and user actions.

### Dependency-Based Transitions

```
PENDING ──(all dependencies done)──> READY
PENDING ──(dependencies incomplete)──> BLOCKED
```

When creating a task with dependencies:
- Status starts as `PENDING`
- System evaluates `CompletionLogic` (ALL/ANY)
- If dependencies incomplete → status becomes `BLOCKED`
- If dependencies complete → status becomes `READY`

### Claim Flow

```
READY ──(claim_task)──> IN_PROGRESS
```

- Only tasks in `READY` state can be claimed
- Claiming is atomic - prevents race conditions
- Use `executor_id` for audit trail

### Review Flow

```
IN_PROGRESS ──(submit_task_result)──> REVIEW
REVIEW ──(review_task, approved=True)──> DONE
REVIEW ──(review_task, approved=False)──> CHANGES_REQUESTED
```

**Key automation**:
- When a task becomes `DONE`, the system automatically re-evaluates all dependent tasks
- Blocked tasks may become `READY` if all their dependencies are now complete

### Status Values Reference

| Status | Description |
|--------|-------------|
| `pending` | Initial state, dependencies not yet evaluated |
| `blocked` | Dependencies incomplete, cannot proceed |
| `ready` | All dependencies met, can be claimed |
| `in_progress` | Claimed by an executor |
| `review` | Execution complete, awaiting approval |
| `done` | Approved and completed |
| `changes_requested` | Rejected, needs rework |
| `skipped` | Intentionally skipped |
| `discarded` | Removed from consideration |

## Planning Level Hierarchy

Tasks are organized by planning granularity. Use appropriate levels:

| Level | Description | Typical Effort |
|-------|-------------|----------------|
| `initiative` | Strategic goals, multi-project scope | 13-21 |
| `milestone` | Major delivery points | 8-13 |
| `architectural` | System design decisions | 8-13 |
| `feature` | User-facing functionality | 5-8 |
| `atomic` | Code implementation tasks | 1-3 |

**Effort values must be Fibonacci numbers**: 1, 2, 3, 5, 8, 13, 21...

## Dependency Management

### Completion Logic

- `ALL` (default): All dependencies must complete before task becomes READY
- `ANY`: Any single dependency completing unblocks the task

### Cycle Prevention

The system automatically detects and prevents circular dependencies:

```
# This will be rejected if it creates a cycle
modify_task_dependencies(
    task_id="task-a",
    added_dependencies=["task-b"]  # If task-b already depends on task-a
)
```

## Priority Analysis (ROI-Based)

Use `suggest_next_action` to get the highest-priority actionable tasks:

```
suggest_next_action(top_n=3, project_id="MyProject")
```

Priority is calculated as: **ROI = Value / Effort**

Higher value and lower effort = higher priority.

## Common Workflows

### Create Task with Dependencies

```
create_task(
    project_id="MyProject",
    name="Implement auth module",
    description="Add JWT authentication to the API",
    effort=5,
    base_value=8.0,
    planning_level="feature",
    completion_logic="all",
    dependencies=["task-id-of-prerequisite-1", "task-id-of-prerequisite-2"]
)
```

### Claim and Execute

```
# 1. Find actionable tasks
suggest_next_action(top_n=3, project_id="MyProject")

# 2. Claim a task
claim_task(task_id="task-uuid")

# 3. Submit results
submit_task_result(
    task_id="task-uuid",
    summary="Implemented JWT auth with refresh tokens",
    artifacts=["src/auth/jwt.py", "src/auth/middleware.py"]
)
```

### Review and Approve

```
# Approve and auto-unblock dependents
review_task(
    task_id="task-uuid",
    approved=True,
    feedback="Looks good, merged to main"
)

# Reject with feedback
review_task(
    task_id="task-uuid",
    approved=False,
    feedback="Missing error handling for expired tokens"
)
```

### Query Tasks

```
# List all ready tasks in a project
list_tasks(
    project_id="MyProject",
    status="ready",
    page=1,
    page_size=10
)

# Search by keyword
list_tasks(
    project_id="MyProject",
    search="authentication"
)

# Filter by planning level
list_tasks(
    project_id="MyProject",
    planning_level="atomic"
)
```

## Best Practices

### 1. Always Use `project_id`

Never leave `project_id` empty. This ensures proper task isolation across projects.

### 2. Use Appropriate Planning Levels

Match the planning level to the task scope:
- `atomic` for code-level tasks (file modifications, functions)
- `feature` for user-facing features
- `architectural` for design decisions
- `milestone`/`initiative` for project planning

### 3. Set Realistic Effort Estimates

Use Fibonacci numbers and consider:
- `1-3`: Simple tasks, well-understood
- `5-8`: Moderate complexity, some unknowns
- `13+`: High complexity, significant unknowns

### 4. Define Clear Dependencies

- Express real constraints, not just ordering preferences
- Use `ANY` logic when alternatives exist
- Let the system handle blocking/unblocking

### 5. Provide Detailed Descriptions

For `atomic` tasks, include:
- File paths to modify
- Specific functions/classes to implement
- Acceptance criteria

### 6. Use Review Workflow

For quality control:
1. Submit results with `submit_task_result`
2. Use `review_task` for approval
3. This enables automatic dependent unblocking

### 7. Check Dependencies Before Creating

Use `get_task_details` to verify prerequisite tasks exist before adding dependencies.

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| Invalid planning_level | Wrong enum value | Use: `initiative`, `milestone`, `architectural`, `feature`, `atomic` |
| Invalid status | Wrong enum value | Use lowercase: `pending`, `ready`, `in_progress`, etc. |
| Task not claimable | Task not in READY state | Check current status, wait for dependencies |
| Cycle detected | Circular dependency | Remove conflicting dependencies |
| Task not found | Invalid task_id | Use `list_tasks` to find correct ID |

### Invalid Effort Value

Effort must be a Fibonacci number. Common values: 1, 2, 3, 5, 8, 13, 21.

---

**Note**: This skill is maintained in the TaskGraph project at `docs/TASK_GRAPH_SKILL.md`. Update when MCP tools or domain logic changes.