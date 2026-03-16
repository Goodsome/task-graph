# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TaskGraph is a DAG-based task planning and orchestration engine following Domain-Driven Design (DDD). It exposes task management capabilities via MCP (Model Context Protocol) tools for LLM applications.

**Key Technologies**: Python 3.13, uv, Pydantic v2, SQLAlchemy async, dependency-injector, MCP

## Common Commands

```bash
# Setup
uv sync

# Run tests
uv run pytest
uv run pytest -v                                    # verbose
uv run pytest tests/path/to/test_file.py           # single file
uv run pytest -k "test_pattern"                    # pattern match

# Run MCP server
uv run task-graph-mcp
uv run python -m task_graph.planning.interfaces.mcp_server
```

## Architecture

```
src/task_graph/
├── planning/                    # Planning Bounded Context
│   ├── domain/                  # Core business logic (no external deps)
│   │   ├── aggregates/          # Task (aggregate root)
│   │   ├── value_objects/       # TaskId, StoryPoint, ValueScore, etc.
│   │   ├── services/            # CycleDetection, DependencyResolution, PriorityAnalysis
│   │   ├── ports/               # TaskRepository interface
│   │   ├── enums.py             # TaskStatus, PlanningLevel, CompletionLogic
│   │   └── exceptions.py
│   ├── application/             # Use cases (CQRS: Command/Query)
│   │   ├── use_cases/           # CreateTask, ClaimTask, ReviewTask, etc.
│   │   └── unit_of_work.py
│   ├── infrastructure/          # External concerns
│   │   ├── repositories/        # SqlAlchemyTaskRepository
│   │   ├── database.py
│   │   └── orm.py
│   ├── interfaces/              # MCP server
│   ├── container.py             # DI container (dependency-injector)
│   └── config.py                # Settings (pydantic-settings)
├── shared/                      # Shared kernel
│   ├── events.py, models.py
│   └── infrastructure/event_bus.py
```

## Key Patterns

### DDD Layer Dependencies
- **Domain** → No external dependencies (pure Python, Pydantic)
- **Application** → Depends on Domain (ports, entities)
- **Infrastructure** → Implements Domain ports
- **Interfaces** → Orchestrates Application use cases

### Aggregate & Value Object Pattern
- Aggregates: `Task.create()`, `Task.reconstitute()` factory methods
- Value Objects: Frozen Pydantic models with `create()` factory
- All models use `ConfigDict(extra="forbid")` or `ConfigDict(frozen=True, extra="forbid")`

### Use Case Pattern
Each use case has Command/Query and Result models:
```python
class CreateTaskCommand(BaseModel):
    project_id: str
    name: str
    ...

class CreateTaskResult(BaseModel):
    success: bool
    task_id: str
    error: str = ""
```

### Repository Pattern
- Interface: `domain/ports/task_repository.py`
- Implementation: `infrastructure/repositories/sql_alchemy_task_repository.py`
- Accessed via Unit of Work pattern for transaction management

## MCP Tools (10 total)

The MCP server exposes these tools for task management:

| Tool | Purpose |
|------|---------|
| `create_task` | Create a new planning task |
| `list_tasks` | Paginated task listing with filters |
| `get_task_details` | Get full task context |
| `suggest_next_action` | Get highest priority actionable tasks (ROI-based) |
| `claim_task` | Claim a READY task (atomic status change) |
| `submit_task_result` | Submit execution results |
| `review_task` | Approve/reject task in REVIEW state |
| `modify_task_dependencies` | Add/remove task dependencies (with cycle detection) |
| `revise_task_details` | Update task name, description, effort, value |
| `delete_task` | Remove a task |

## Task Status Flow

```
PENDING → BLOCKED → READY → IN_PROGRESS → REVIEW → DONE
                        ↓                    ↓
                   CHANGES_REQUESTED ←───────┘
```

## Code Generation

This project uses `codegen.yaml` as a DDD blueprint. Use the codegen MCP tools:
- `mcp__codegen__build` - Generate code from blueprint
- `mcp__codegen__tree` - Visualize blueprint structure
- `mcp__codegen__get/set/rm` - Query/modify blueprint

## Database Configuration

Set `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/taskgraph
```

## Testing

- Tests mirror source structure under `tests/`
- Use pytest fixtures in `conftest.py` files
- Mock repositories with `unittest.mock.Mock`
- In-memory implementations for unit tests