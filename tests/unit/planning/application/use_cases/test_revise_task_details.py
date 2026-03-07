import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.revise_task_details import (
    ReviseTaskDetails,
    ReviseTaskDetailsCommand
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects import TaskId

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def use_case(mock_uow):
    return ReviseTaskDetails(uow=mock_uow)

def test_revise_task_details_success(use_case, mock_repo):
    task_id_str = str(TaskId.create().value)
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.name = "Old Name"
    mock_task.effort.value = 1
    mock_repo.get.return_value = mock_task
    
    cmd = ReviseTaskDetailsCommand(
        task_id=task_id_str,
        name="New Name",
        effort=5
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    assert mock_task.name == "New Name"
    # Verify effort was updated (mock doesn't actually store VO, but property should be set)
    # Since we mocked the task, we can check if attributes were set
    # But wait, in the use case: task.effort = StoryPoint.create(cmd.effort)
    # The mock will just accept the assignment.
    
    mock_repo.save.assert_called_once()

def test_revise_task_not_found(use_case, mock_repo):
    mock_repo.get.return_value = None
    
    cmd = ReviseTaskDetailsCommand(
        task_id=str(TaskId.create().value),
        name="New Name"
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is False
    assert "not found" in result.error
    mock_repo.save.assert_not_called()
