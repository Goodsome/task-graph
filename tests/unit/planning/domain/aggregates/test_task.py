import pytest
from task_graph.planning.domain.enums import CompletionLogic, ScopeLevel, TaskStatus
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.sub_task_info import SubTaskInfo


@pytest.fixture
def sample_task():
    return Task.create(
        project_id="proj-123",
        name="Parent Task",
        description="A task to be decomposed.",
        effort=StoryPoint.create(5),
        base_value=ValueScore.create(100.0),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        scope_level=ScopeLevel.PROJECT,
    )


def test_task_review_without_sub_tasks(sample_task: Task):
    # Setup
    sample_task.status = TaskStatus.IN_PROGRESS
    sample_task.set_output(TaskOutput(summary="Done", artifacts=[]))
    
    # Execute
    sample_task.review(approved=True, feedback="Good job")
    
    # Assert
    assert sample_task.status == TaskStatus.DONE


def test_task_review_with_sub_tasks(sample_task: Task):
    # Setup
    sample_task.status = TaskStatus.IN_PROGRESS
    sub1 = SubTaskInfo(
        name="Backend",
        description="Backend implementation",
        effort=StoryPoint.create(3),
        base_value=ValueScore.create(50.0),
        acceptance_criteria=[]
    )
    sub2 = SubTaskInfo(
        name="Frontend",
        description="Frontend implementation",
        effort=StoryPoint.create(2),
        base_value=ValueScore.create(50.0),
        acceptance_criteria=[]
    )
    sample_task.set_output(TaskOutput(
        summary="Done but needs split",
        artifacts=[],
        sub_tasks=[sub1, sub2]
    ))
    
    # Execute
    sample_task.review(approved=True, feedback="Please decompose")
    
    # Assert
    assert sample_task.status == TaskStatus.DECOMPOSING
    
    # Now generate subtasks
    sub_tasks = sample_task.generate_sub_tasks()
    
    assert len(sub_tasks) == 2
    
    # Verify child 1 properties
    assert sub_tasks[0].name == "Parent Task[Backend]"
    assert sub_tasks[0].description == "Backend implementation"
    assert sub_tasks[0].effort.value == 3
    assert sub_tasks[0].base_value.value == 50.0
    assert sub_tasks[0].scope_level == ScopeLevel.CONTEXT
    assert sub_tasks[0].scope_context.bounded_context == "Backend"
    assert sub_tasks[0].parent_id == sample_task.id

    # Verify child 2 properties
    assert sub_tasks[1].name == "Parent Task[Frontend]"
    assert sub_tasks[1].scope_context.bounded_context == "Frontend"
    assert sub_tasks[1].parent_id == sample_task.id
