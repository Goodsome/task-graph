import pytest
from sqlalchemy.orm import Session
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.enums import TaskStatus, PlanningLevel, CompletionLogic
from task_graph.planning.infrastructure.repositories.sql_alchemy_task_repository import SqlAlchemyTaskRepository
from task_graph.planning.infrastructure.orm import TaskModel

@pytest.fixture
def repository(session_factory):
    # Retrieve a single session for the repository tests
    session = session_factory()
    return SqlAlchemyTaskRepository(session=session)

def test_save_and_get_task(repository):
    # Given
    task = Task.create(
        project_id="test-project",
        name="Test Task",
        description="Detailed description",
        effort=StoryPoint.create(3),
        base_value=ValueScore.create(5.0),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        planning_level=PlanningLevel.ATOMIC
    )

    # When
    repository.save(task)
    retrieved_task = repository.get(task.id)

    # Then
    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.name == "Test Task"
    assert retrieved_task.project_id == "test-project"
    assert retrieved_task.status == TaskStatus.PENDING # Default from Task.create

def test_delete_task(repository):
    # Given
    task = Task.create(
        project_id="test-project",
        name="To Delete",
        description="...",
        effort=StoryPoint.create(1),
        base_value=ValueScore.create(1.0),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        planning_level=PlanningLevel.ATOMIC
    )
    repository.save(task)
    
    # When
    repository.delete(task.id)
    retrieved_task = repository.get(task.id)
    
    # Then
    assert retrieved_task is None

def test_find_paged(repository):
    # Given
    for i in range(15):
        task = Task.create(
            project_id="test-project",
            name=f"Task {i}",
            description="...",
            effort=StoryPoint.create(1),
            base_value=ValueScore.create(1.0),
            completion_logic=CompletionLogic.ALL,
            dependencies=set(),
            planning_level=PlanningLevel.ATOMIC,
            status=TaskStatus.READY if i % 2 == 0 else TaskStatus.PENDING
        )
        repository.save(task)
    
    # When
    tasks, total = repository.find_paged(
        status=TaskStatus.READY,
        project_id="test-project",
        planning_level=PlanningLevel.ATOMIC,
        search="Task",
        page=1,
        page_size=5
    )
    
    # Then
    assert total == 8 # 0, 2, 4, 6, 8, 10, 12, 14
    assert len(tasks) == 5

def test_task_dependencies(repository):
    # Given
    task_a = Task.create(
        project_id="test-project",
        name="Task A",
        description="...",
        effort=StoryPoint.create(1),
        base_value=ValueScore.create(1.0),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        planning_level=PlanningLevel.ATOMIC
    )
    repository.save(task_a)
    
    task_b = Task.create(
        project_id="test-project",
        name="Task B",
        description="...",
        effort=StoryPoint.create(1),
        base_value=ValueScore.create(1.0),
        completion_logic=CompletionLogic.ALL,
        dependencies={task_a.id},
        planning_level=PlanningLevel.ATOMIC
    )
    repository.save(task_b)
    
    # When
    retrieved_b = repository.get(task_b.id)
    dependents_of_a = repository.find_dependents(task_a.id)
    
    # Then
    assert task_a.id in retrieved_b.dependencies
    assert len(dependents_of_a) == 1
    assert dependents_of_a[0].id == task_b.id

def test_optimistic_locking(repository, session_factory):
    # Given
    task = Task.create(
        project_id="test-project",
        name="Lock Task",
        description="...",
        effort=StoryPoint.create(1),
        base_value=ValueScore.create(1.0),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        planning_level=PlanningLevel.ATOMIC
    )
    repository.save(task)
    
    # Simulate two sessions
    session1 = session_factory()
    session2 = session_factory()
    
    # In real implementation, the domain object might not have version_id, 
    # but the mapper handles it. We just need to check if save fails on conflict.
    # However, since save() usually fetches and merges, we need to be careful.
    
    # For now, this test identifies if we handle concurrent updates.
    # We might need to implement this later when Logic Filling is done.
    pass
