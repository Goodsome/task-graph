import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.create_task import CreateTask, CreateTaskCommand
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.enums import ScopeLevel, CompletionLogic, TaskStatus
from task_graph.planning.domain.value_objects import TaskId

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def use_case(mock_uow):
    return CreateTask(uow=mock_uow)

def test_create_task_all_logic_satisfied(use_case, mock_repo):
    # Setup: 2 dependencies, both DONE
    dep1 = Mock()
    dep1.id = TaskId.create()
    dep1.status = TaskStatus.DONE
    
    dep2 = Mock()
    dep2.id = TaskId.create()
    dep2.status = TaskStatus.DONE
    
    mock_repo.find_by_ids.return_value = [dep1, dep2]
    
    cmd = CreateTaskCommand(
        project_id="test-project",
        name="Task ALL Satisfied",
        description="Desc",
        effort=3,
        base_value=5.0,
        scope_level=ScopeLevel.ATOMIC,
        completion_logic=CompletionLogic.ALL,
        dependencies=[str(dep1.id), str(dep2.id)]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    # Verify the task saved has status READY
    saved_task = mock_repo.save.call_args[0][0]
    assert saved_task.status == TaskStatus.READY

def test_create_task_all_logic_partially_satisfied(use_case, mock_repo):
    # Setup: 2 dependencies, one DONE, one PENDING
    dep1 = Mock()
    dep1.id = TaskId.create()
    dep1.status = TaskStatus.DONE
    
    dep2 = Mock()
    dep2.id = TaskId.create()
    dep2.status = TaskStatus.PENDING
    
    mock_repo.find_by_ids.return_value = [dep1, dep2]
    
    cmd = CreateTaskCommand(
        project_id="test-project",
        name="Task ALL Partially Satisfied",
        description="Desc",
        effort=3,
        base_value=5.0,
        scope_level=ScopeLevel.ATOMIC,
        completion_logic=CompletionLogic.ALL,
        dependencies=[str(dep1.id), str(dep2.id)]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    saved_task = mock_repo.save.call_args[0][0]
    assert saved_task.status == TaskStatus.PENDING

def test_create_task_any_logic_not_satisfied(use_case, mock_repo):
    # Setup: 2 dependencies, none DONE
    dep1 = Mock()
    dep1.id = TaskId.create()
    dep1.status = TaskStatus.PENDING
    
    dep2 = Mock()
    dep2.id = TaskId.create()
    dep2.status = TaskStatus.READY
    
    mock_repo.find_by_ids.return_value = [dep1, dep2]
    
    cmd = CreateTaskCommand(
        project_id="test-project",
        name="Task ANY Not Satisfied",
        description="Desc",
        effort=3,
        base_value=5.0,
        scope_level=ScopeLevel.ATOMIC,
        completion_logic=CompletionLogic.ANY,
        dependencies=[str(dep1.id), str(dep2.id)]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    saved_task = mock_repo.save.call_args[0][0]
    assert saved_task.status == TaskStatus.PENDING
