import pytest
from unittest.mock import Mock, ANY
from task_graph.planning.application.use_cases.create_task import CreateTask, CreateTaskCommand
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.enums import ScopeLevel, CompletionLogic
from task_graph.planning.domain.value_objects import TaskId

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def use_case(mock_uow):
    return CreateTask(uow=mock_uow)

def test_create_task_success(use_case, mock_repo):
    cmd = CreateTaskCommand(
        project_id="test-project",
        name="Test Task",
        description="Description",
        effort=5,
        base_value=10.0,
        scope_level=ScopeLevel.CONTEXT,
        completion_logic=CompletionLogic.ALL,
        dependencies=[]
    )
    
    mock_repo.find_by_ids.return_value = []
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    assert result.task_id != ""
    assert result.error == ""
    mock_repo.save.assert_called_once()

def test_create_task_with_dependencies_success(use_case, mock_repo):
    dep_id = TaskId.create()
    cmd = CreateTaskCommand(
        project_id="test-project",
        name="Dependent Task",
        description="Desc",
        effort=3,
        base_value=5.0,
        scope_level=ScopeLevel.ATOMIC,
        completion_logic=CompletionLogic.ANY,
        dependencies=[str(dep_id)]
    )
    
    mock_task = Mock()
    mock_task.id = TaskId.reconstitute(str(dep_id))
    mock_repo.find_by_ids.return_value = [mock_task]
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    mock_repo.save.assert_called_once()

def test_create_task_missing_dependency(use_case, mock_repo):
    missing_id = "00000000-0000-0000-0000-000000000000"
    cmd = CreateTaskCommand(
        project_id="test-project",
        name="Broken Task",
        description="Desc",
        effort=1,
        base_value=1.0,
        scope_level=ScopeLevel.ATOMIC,
        completion_logic=CompletionLogic.ALL,
        dependencies=[missing_id]
    )
    
    mock_repo.find_by_ids.return_value = [] # No tasks found
    
    result = use_case.execute(cmd)
    
    assert result.success is False
    assert "Dependencies not found" in result.error
    mock_repo.save.assert_not_called()
