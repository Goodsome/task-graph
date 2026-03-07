import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.update_task_status import (
    UpdateTaskStatus,
    UpdateTaskStatusCommand
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.services import DependencyResolutionService
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.value_objects import TaskId

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def mock_resolution_service():
    return Mock(spec=DependencyResolutionService)

@pytest.fixture
def use_case(mock_uow, mock_resolution_service):
    return UpdateTaskStatus(
        uow=mock_uow,
        resolution_service=mock_resolution_service
    )

def test_update_status_simple(use_case, mock_repo):
    task_id_str = str(TaskId.create().value)
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.id.value = task_id_str
    mock_task.status = TaskStatus.READY
    def side_effect_status(status):
        mock_task.status = status
    mock_task._update_status.side_effect = side_effect_status
    mock_task.is_done.return_value = False
    
    mock_repo.get.return_value = mock_task
    
    cmd = UpdateTaskStatusCommand(
        task_id=task_id_str,
        new_status="in_progress"
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    assert mock_task.status == TaskStatus.IN_PROGRESS
    mock_repo.save.assert_called_once()

def test_update_status_unlocking_dependents(use_case, mock_repo, mock_resolution_service):
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.id = task_id
    mock_task.status = TaskStatus.IN_PROGRESS
    def side_effect_status(status):
        mock_task.status = status
    mock_task._update_status.side_effect = side_effect_status
    # Simulate completion
    mock_task.is_done.return_value = True
    
    mock_repo.get.return_value = mock_task
    
    # Dependent task that is currently blocked
    dep_task = Mock()
    dep_task.collect_events.return_value = []
    dep_task.id = TaskId.create()
    dep_task.status = TaskStatus.BLOCKED
    def dep_side_effect_status(status):
        dep_task.status = status
    dep_task._update_status.side_effect = dep_side_effect_status
    
    mock_repo.find_dependents.return_value = [dep_task]
    
    # Resolution service says it's no longer blocked
    mock_resolution_service.evaluate_blocking_status.return_value = False
    
    cmd = UpdateTaskStatusCommand(
        task_id=task_id_str,
        new_status="done"
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    assert mock_task.status == TaskStatus.DONE
    # Verify dependent was updated to READY
    assert dep_task.status == TaskStatus.READY
    assert str(dep_task.id.value) in result.affected_tasks
    
    # Should save both
    assert mock_repo.save.call_count == 2
