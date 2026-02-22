# AGENTS.md - TaskGraph Project Guidelines

## Project Overview

TaskGraph is a Python project implementing a Domain-Driven Design (DDD) task planning system with dependency management, status tracking, and MCP server interface.

- **project_id**: TaskGraph
- **Python Version**: >=3.13
- **Package Manager**: uv

## Build, Lint, and Test Commands

### Setup
```bash
# Install dependencies
uv sync

# Install dev dependencies
uv sync --group dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/planning/application/use_cases/test_create_task.py

# Run a specific test
uv run pytest tests/planning/application/use_cases/test_create_task.py::test_create_task_success

# Run tests with verbose output
uv run pytest -v

# Run tests matching a pattern
uv run pytest -k "test_create"
```

### Running the Application
```bash
# Run MCP server
uv run task-graph-mcp

# Or run as module
uv run python -m task_graph.planning.interfaces.mcp_server
```

## Code Style Guidelines

### Imports
- **Order**: Standard library → Third-party → Local (`task_graph.*`)
- Use absolute imports for project modules
- Group imports: stdlib, third-party, local with blank lines between groups

```python
# Standard library
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID, uuid4

# Third-party
from pydantic import BaseModel, Field

# Local
from task_graph.planning.domain.aggregates import Task
from task_graph.planning.domain.enums import TaskStatus
```

### Type Hints
- Use type hints for all function parameters and return types
- Use `|` union syntax (Python 3.10+) instead of `Union` or `Optional`
- Use `list[Type]` and `set[Type]` instead of `List`/`Set` from typing

```python
def find_by_id(self, task_id: TaskId) -> Task | None:
    ...

def process_items(self, items: list[str]) -> dict[str, int]:
    ...
```

### Naming Conventions
- **Classes**: PascalCase (`TaskRepository`, `CreateTaskCommand`)
- **Functions/Variables**: snake_case (`find_by_id`, `task_status`)
- **Constants**: UPPER_SNAKE_CASE (use sparingly)
- **Private**: prefix with underscore (`_internal_method`)
- **Abstract/Base Classes**: Prefix with port/interface concept or descriptive names

### DDD Architecture Patterns

**Layer Structure**:
```
src/task_graph/planning/
├── domain/              # Core business logic
│   ├── aggregates/      # Aggregate roots (Task)
│   ├── value_objects/   # Immutable values (TaskId, StoryPoint)
│   ├── enums/           # Domain enumerations
│   ├── exceptions/      # Domain-specific errors
│   ├── services/        # Domain services
│   └── ports/           # Repository interfaces
├── application/         # Use cases
│   └── use_cases/       # Application services
└── infrastructure/      # External concerns
    ├── repositories/    # Repository implementations
    └── orm.py          # Database models
```

**Key Patterns**:
- Aggregates inherit from `Aggregate` (Pydantic BaseModel)
- Value Objects inherit from `ValueObject` (frozen Pydantic model)
- Use factory methods: `create()` for new, `reconstitute()` for persistence
- Repository Pattern: Interface in `ports/`, implementation in `infrastructure/`
- Command/Result pattern for use cases

### Model Configuration
All Pydantic models use strict configuration:

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # or for ValueObjects:
    model_config = ConfigDict(frozen=True, extra="forbid")
```

### Error Handling
- Define custom exceptions in `domain/exceptions.py`
- Use domain exceptions for business rule violations
- Use `RuntimeError` for programming errors
- Log exceptions with full traceback in application layer

```python
# In domain/exceptions.py
class TaskNotClaimableError(Exception):
    """Raised when attempting to claim a task that is not in READY state."""
    pass

# In use cases
except Exception as e:
    logger.error(e)
    import traceback
    logger.error(traceback.format_exc())
    return Result(success=False, error=str(e))
```

### Testing
- Use pytest fixtures in `conftest.py` files
- Mock external dependencies (repositories) using `unittest.mock.Mock`
- Create test fixtures for common object graphs
- In-memory repository implementations for testing

```python
# Test structure
from unittest.mock import Mock

def test_feature(mock_repo):
    use_case = MyUseCase(repository=mock_repo)
    result = use_case.execute(command)
    assert result.success is True
    mock_repo.save.assert_called_once()
```

### Comments and Documentation
- Docstrings for classes and public methods when non-obvious
- Comments in code can be in English or Chinese (project uses both)
- Keep docstrings concise and focused on "why" not "what"

### File Organization
- One class per file for major domain objects
- Group related use cases in same module
- Test files mirror source structure under `tests/`

## Project-Specific Rules

- **project_id**: Always use "TaskGraph" when referring to this project
- Task IDs are UUID-based (use `TaskId.create()` or `TaskId.reconstitute()`)
- Status flow: PENDING → READY → IN_PROGRESS → REVIEW → DONE
- Dependencies use `CompletionLogic.ALL` (default) or `CompletionLogic.ANY`
- Planning levels: INITIATIVE → MILESTONE → ARCHITECTURAL → FEATURE → ATOMIC
