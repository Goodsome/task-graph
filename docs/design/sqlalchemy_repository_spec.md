# Design Specification: SqlAlchemy TaskRepository

## 1. Introduction
This document outlines the detailed design for implementing `SqlAlchemyTaskRepository`, a persistent storage mechanism for the TaskGraph system using SQLAlchemy. This implementation will replace the `InMemoryTaskRepository` for production use, providing durability, transaction support, and advanced querying capabilities.

## 2. Database Schema Design (ER Diagram)

We will use SQLAlchemy's Declarative Mapping system.

### 2.1 Tables

#### `tasks` Table
Stores the core attributes of the `Task` aggregate.

| Column Name        | SQL Type       | Nullable | Description                                         |
|:-------------------|:---------------|:---------|:----------------------------------------------------|
| `id`               | `VARCHAR(36)`  | No       | Primary Key (UUID as string)                        |
| `project_id`       | `VARCHAR(64)`  | No       | Project Identifier (Indexed)                        |
| `name`             | `VARCHAR(255)` | No       | Task Name                                           |
| `description`      | `TEXT`         | No       | Full Task Description                               |
| `status`           | `VARCHAR(32)`  | No       | Enum: `PENDING`, `READY`, etc. (Indexed)            |
| `planning_level`   | `VARCHAR(32)`  | No       | Enum: `INITIATIVE`, `FEATURE`, etc. (Indexed)       |
| `completion_logic` | `VARCHAR(32)`  | No       | Enum: `ALL`, `ANY`                                  |
| `effort`           | `INTEGER`      | No       | Value of `StoryPoint`                               |
| `base_value`       | `FLOAT`        | No       | Value of `ValueScore`                               |
| `output`           | `JSON`         | Yes      | Serialized `TaskOutput` value object                |
| `review_feedback`  | `JSON`         | Yes      | Serialized `ReviewFeedback` value object            |
| `created_at`       | `DATETIME`     | No       | Audit timestamp                                     |
| `updated_at`       | `DATETIME`     | No       | Audit timestamp                                     |
| `version_id`       | `INTEGER`      | No       | For Optimistic Locking                              |

**Indexes**:
- `ix_tasks_project_id`
- `ix_tasks_status`
- `ix_tasks_planning_level`

#### `task_dependencies` Table
Association table for the many-to-many self-referential relationship implementation of the DAG structure.

| Column Name | SQL Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `task_id` | `VARCHAR(36)` | No | Foreign Key -> `tasks.id` (The dependent) |
| `dependency_id` | `VARCHAR(36)` | No | Foreign Key -> `tasks.id` (The prerequisite) |

**Constraints**:
- Primary Key: (`task_id`, `dependency_id`)
- Foreign Keys with `ON DELETE CASCADE` to ensure consistency.

### 2.2 SQLAlchemy Models (Pseudo-code)

```python
from sqlalchemy import Column, String, Integer, Float, Text, Enum, ForeignKey, Table, JSON, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('task_id', String(36), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('dependency_id', String(36), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
)

class TaskModel(Base):
    __tablename__ = 'tasks'

    id = Column(String(36), primary_key=True)
    project_id = Column(String(64), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(32), index=True, nullable=False)  # Stored as string name of enum
    planning_level = Column(String(32), index=True, nullable=False)
    completion_logic = Column(String(32), nullable=False)
    effort = Column(Integer, nullable=False)
    base_value = Column(Float, nullable=False)
    
    # Store Value Objects as JSON
    output = Column(JSON, nullable=True)
    review_feedback = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version_id = Column(Integer, nullable=False, default=1) # SQLAlchemy handles incrementing this

    # Relationships
    # dependencies: tasks that this task DEPENDS ON.
    # If Task A depends on B, then (A.id, B.id) is in table.
    # A.dependencies should return [B]
    dependencies = relationship(
        'TaskModel',
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.dependency_id,
        backref='dependents',  # B.dependents should return [A]
        lazy='selectin'        # Eager load for performance
    )
    
    __mapper_args__ = {
        "version_id_col": version_id
    }
```

## 3. Repository Implementation Strategy

The repository will adhere to the `TaskRepository` interface from `task_graph.planning.domain.ports`.

### 3.1 Class Structure

```python
class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    def save(self, task: Task) -> None:
        # ... implementation ...
        pass

    # ... other methods ...
```

### 3.2 Data Mapping (DTO <-> Domain)

We need robust conversion helpers.

**`_to_domain(self, model: TaskModel) -> Task`**:
- Uses `Task.reconstitute()` factory.
- deserializes JSON fields `output` and `review_feedback` back to Value Objects.
- converts `dependencies` (list of TaskModels) to `set[TaskId]`.

**`_to_model(self, task: Task) -> TaskModel`**:
- Maps domain fields to model columns.
- serializes Value Objects to dicts/JSON.
- **Dependency Handling**: 
  - Since `task.dependencies` contains only IDs, we must query the DB to get Model instances for those IDs to set the `dependencies` relationship on the `TaskModel`, OR manually manage the association table inserts if we want to avoid fetching. 
  - *Strategy*: To preserve integrity, first fetch existing dependency TaskModels by IDs, then assign to `model.dependencies`.

### 3.3 Key Method Implementations

#### `save(task: Task)`
- **Logic**:
    1. Start Transaction.
    2. Check if task exists (by ID).
    3. If exists: Update fields. Merge dependencies (update association table).
    4. If new: Create new `TaskModel`.
    5. Commit.
- **Concurrency**: rely on `version_id` for Optimistic Locking. Handle `StaleDataError`.

#### `find_paged(...)`
- **Logic**:
    - Query `db.query(TaskModel)`.
    - Apply dynamic filters:
        - `if status: query = query.filter(TaskModel.status == status.value)`
        - `if project_id: query = query.filter(TaskModel.project_id == project_id)`
        - `if planning_level: query = query.filter(TaskModel.planning_level == planning_level.value)`
        - `if search: query = query.filter(or_(TaskModel.name.ilike(f"%{search}%"), TaskModel.description.ilike(f"%{search}%")))`
    - Count total: `total = query.count()`
    - Apply Pagination: `items = query.offset((page - 1) * page_size).limit(page_size).all()`
    - Convert to domain entities.
    - Return `(items, total)`.

#### `find_dependents(task_id: TaskId)`
- **Logic**:
    - Use the `backref` 'dependents' defined in the relationship.
    - `model = session.get(TaskModel, task_id.value)`
    - `return [self._to_domain(d) for d in model.dependents]`
    - Alternatively, direct join query for efficiency if lazy loading is off.

## 4. Configuration & Session Management

- **Connection**: Connection string provided via environment variable `DATABASE_URL`.
- **Session**:
    - The repository accepts a `session_factory` (e.g., `sessionmaker`).
    - Methods should manage their own scope if atomic, or accept an optional session for external transaction control (Unit of Work pattern). 
    - *Decision*: To strictly follow the Port interface which doesn't accept a session, the repository implementation will manage the session scope internally for each method, `with self._session_factory() as session:`.

## 5. Migration Strategy

- Use `alembic` for schema migrations.
- Initial migration script to create `tasks` and `task_dependencies` tables.
