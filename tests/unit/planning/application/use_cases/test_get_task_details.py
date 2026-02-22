import pytest
from unittest.mock import Mock, MagicMock
from task_graph.planning.application.use_cases.get_task_details import GetTaskDetails, GetTaskDetailsQuery
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from uuid import uuid4

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def use_case(mock_repo):
    return GetTaskDetails(repository=mock_repo)

def test_get_existing_task(use_case, mock_repo):
    task_id_str = str(uuid4())
    mock_task = MagicMock()
    mock_task.to_dict.return_value = {"id": task_id_str, "name": "Existing Task"}
    
    mock_repo.find_by_id.return_value = mock_task
    
    query = GetTaskDetailsQuery(task_id=task_id_str)
    result = use_case.execute(query)
    
    assert result.success is True
    assert result.task == {"id": task_id_str, "name": "Existing Task"}
    assert result.error is None
    
    # Verify repo called correctly
    # Since TaskId is a value object, we might need to check if called with equivalent TaskId
    args, _ = mock_repo.find_by_id.call_args
    assert str(args[0]) == task_id_str

def test_get_non_existing_task(use_case, mock_repo):
    mock_repo.find_by_id.return_value = None
    
    task_id_str = str(uuid4())
    query = GetTaskDetailsQuery(task_id=task_id_str)
    result = use_case.execute(query)
    
    assert result.success is False
    assert result.task is None
    assert f"Task with ID {task_id_str} not found" in result.error

def test_repository_exception(use_case, mock_repo):
    mock_repo.find_by_id.side_effect = Exception("Database error")
    
    task_id_str = str(uuid4())
    query = GetTaskDetailsQuery(task_id=task_id_str)
    result = use_case.execute(query)
    
    assert result.success is False
    assert result.task is None
    assert "Database error" in result.error
