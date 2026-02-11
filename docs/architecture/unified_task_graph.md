# Architecture Design: Unified TaskGraph Service

## 1. Introduction
This document outlines the architectural changes required to transform the `TaskGraph` module from an embedded component within `CodingAgent` into a standalone, unified service capable of managing tasks across multiple projects and planning granularities.

## 2. Problem Statement
Currently, `TaskGraph` operates within the context of a single agent instance, lacking:
1.  **Spatial Awareness**: No distinction between different projects (`project_id`).
2.  **Vertical Scalability**: Limited to `ARCHITECTURAL`, `FEATURE`, `ATOMIC` levels, missing higher-level strategic planning (`INITIATIVE`, `MILESTONE`).
3.  **Cross-Project Dependencies**: Cannot link tasks across project boundaries (e.g., Frontend requiring Backend API).
4.  **Accessibility**: Tightly coupled with the agent's internal logic, not exposed as a general-purpose service.

## 3. Goals & Requirements
- **Unified Service**: Deployable as a standalone MCP Server or HTTP Service.
- **Multi-Project Support**: Segregate tasks by `project_id`.
- **Extended Hierarchy**: Support `INITIATIVE` -> `MILESTONE` -> `ARCHITECTURAL` -> `FEATURE` -> `ATOMIC`.
- **Global Dependency Graph**: Allow dependencies between any two tasks regardless of project, maintaining DAG constraints globally.

## 4. Domain Model Changes

### 4.1. Task Aggregate
We will enhance the `Task` entity with the following fields:

```python
class Task:
    id: TaskId
    project_id: str  # New: Identifies the project scope (e.g., "backend", "frontend")
    name: str
    description: str
    status: TaskStatus
    planning_level: PlanningLevel
    # ... existing fields
```

### 4.2. Planning Level Extension
The `PlanningLevel` enum will be expanded:

```python
class PlanningLevel(Enum):
    INITIATIVE = "initiative"       # Strategic goals, multi-project scope
    MILESTONE = "milestone"         # Major delivery points
    ARCHITECTURAL = "architectural" # System design
    FEATURE = "feature"             # User-facing functionality
    ATOMIC = "atomic"               # Code implementation
```

### 4.3. Dependency Logic
Dependencies remain a set of `TaskId`. The `CycleDetectionService` will continue to function on the global graph.
Cross-project dependencies are naturally supported as `TaskId` is globally unique (UUID).
The `DependencyResolutionService` must ensure that checking `dependents` works across projects.

## 5. API Interface Design (MCP)
The service will expose the following tools via MCP:

### 5.1. Task Management
- `create_task(project_id: str, ...)` -> `task_id`
- `list_tasks(project_id: str | None, ...)` -> `list[Task]`
  - If `project_id` is None, requires admin/global view permissions (or returns all if no auth).
- `get_task_details(task_id: str)` -> `Task`

### 5.2. Cross-Project Interactions
- `modify_task_dependencies(task_id, added_dependencies=[...])`
  - Validates that `added_dependencies` exist, possibly in other projects.

## 6. Infrastructure & Deployment
- **Standalone Package**: The core logic will be packaged as `task-graph-service`.
- **MCP Server**: A specialized entry point `mcp_server.py` will expose the functionality.
- **Storage**:
    - *Current*: `YamlTaskRepository` (File-based).
    - *Migration*: Move to `SQLite` or `PostgreSQL` for concurrent access and robustness in a standalone service scenario. For now, we keep YAML but split by `project_id` or use a single global file with `project_id` field.
    - *Decision*: Extend `YamlTaskRepository` to store `project_id`.

## 7. Migration Strategy
1.  **Refactor Domain**: Update `Task` entity and `PlanningLevel` enum.
2.  **Update Repository**: Modify `YamlTaskRepository` to persist `project_id`.
3.  **Expose MCP**: Ensure `mcp_server.py` is configured to run independently.
4.  **Client Update**: Update `CodingAgent` to use `task-graph` via MCP client instead of direct import (Long-term goal).

## 8. Definition of Done
- [ ] `Task` entity includes `project_id`.
- [ ] `PlanningLevel` includes `INITIATIVE`, `MILESTONE`.
- [ ] MCP Tools updated to accept `project_id`.
- [ ] Tests covering cross-project dependency scenarios pass.
