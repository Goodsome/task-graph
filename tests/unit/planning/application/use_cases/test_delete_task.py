import pytest
from unittest.mock import Mock

from task_graph.planning.application.use_cases.delete_task import DeleteTask, DeleteTaskCommand
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects import TaskId

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def use_case(mock_uow):
    return DeleteTask(uow=mock_uow)

def test_delete_task_success(use_case, mock_repo):
    task_id_str = str(TaskId.create().value)
    cmd = DeleteTaskCommand(task_id=task_id_str)
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    assert result.error == ""
    mock_repo.delete.assert_called_once()
    
    called_task_id = mock_repo.delete.call_args[0][0]
    assert str(called_task_id.value) == task_id_str

def test_delete_task_failure_exception(use_case, mock_repo):
    task_id_str = str(TaskId.create().value)
    cmd = DeleteTaskCommand(task_id=task_id_str)
    
    mock_repo.delete.side_effect = Exception("Database connection error")
    
    result = use_case.execute(cmd)
    
    assert result.success is False
    assert "Database connection error" in result.error
    mock_repo.delete.assert_called_once()
