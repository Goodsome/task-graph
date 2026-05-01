from unittest.mock import MagicMock
import pytest
from task_graph.planning.application.use_cases.decompose_task import (
    DecomposeTask, DecomposeTaskCommand
)
from task_graph.planning.application.use_cases.complete_delegated_task import (
    CompleteDelegatedTask, CompleteDelegatedTaskCommand
)
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus, ScopeLevel, CompletionLogic
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.sub_task_info import SubTaskInfo


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.tasks = MagicMock()
    # Mock context manager
    uow.__enter__.return_value = uow
    return uow


def test_decompose_task_success(mock_uow):
    # Setup
    task_id = TaskId.create()
    task = Task.create(
        project_id="p1",
        name="Task 1",
        description="Desc",
        effort=StoryPoint.create(5),
        base_value=ValueScore.create(10),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        scope_level=ScopeLevel.PROJECT
    )
    # Ensure task ID is consistent
    task.id = task_id
    task.status = TaskStatus.IN_PROGRESS
    
    sub_info = SubTaskInfo(
        name="Sub1",
        description="SubDesc",
        effort=StoryPoint.create(2),
        base_value=ValueScore.create(5),
        acceptance_criteria=[]
    )
    task.set_output(TaskOutput(summary="Done", artifacts=[], sub_tasks=[sub_info]))
    task.review(approved=True, feedback="OK")
    
    # Verify pre-condition: status should be DECOMPOSING after review with sub_tasks
    assert task.status == TaskStatus.DECOMPOSING

    mock_uow.tasks.get.return_value = task
    
    use_case = DecomposeTask(uow=mock_uow)
    cmd = DecomposeTaskCommand(task_id=str(task_id))
    
    # Execute
    result = use_case.execute(cmd)
    
    # Assert
    assert result.success
    assert len(result.sub_task_ids) == 1
    assert task.status == TaskStatus.DELEGATED
    mock_uow.tasks.add.assert_called()
    mock_uow.tasks.save.assert_called_with(task)
    mock_uow.commit.assert_called_once()


def test_complete_decomposition_with_delegated_task(mock_uow):
    # Setup
    task_id = TaskId.create()
    task = Task.create(
        project_id="p1",
        name="Task 1",
        description="Desc",
        effort=StoryPoint.create(5),
        base_value=ValueScore.create(10),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        scope_level=ScopeLevel.PROJECT
    )
    task.id = task_id
    task.status = TaskStatus.DELEGATED
    
    mock_uow.tasks.get.return_value = task
    mock_uow.tasks.find_by_parent_id.return_value = [] # All subtasks done
    
    use_case = CompleteDelegatedTask(uow=mock_uow)
    cmd = CompleteDelegatedTaskCommand(task_id=str(task_id))
    
    # Execute
    result = use_case.execute(cmd)
    
    # Assert
    assert result.status == "success"
    assert task.status == TaskStatus.DONE
    mock_uow.commit.assert_called_once()
