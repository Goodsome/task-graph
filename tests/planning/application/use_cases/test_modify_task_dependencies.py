import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.modify_task_dependencies import (
    ModifyTaskDependencies, 
    ModifyTaskDependenciesCommand
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.services import CycleDetectionService
from task_graph.planning.domain.value_objects import TaskId

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def mock_cycle_service():
    return Mock(spec=CycleDetectionService)

@pytest.fixture
def use_case(mock_repo, mock_cycle_service):
    return ModifyTaskDependencies(
        repository=mock_repo,
        cycle_detector=mock_cycle_service
    )

def test_add_dependency_success(use_case, mock_repo, mock_cycle_service):
    task_id_str = str(TaskId.create().value)
    dep_id_str = str(TaskId.create().value)
    
    # Mock existing task
    mock_task = Mock()
    mock_task.dependencies = set()
    mock_repo.get.side_effect = lambda id: mock_task if str(id.value) == task_id_str else (Mock() if str(id.value) == dep_id_str else None)
    
    # Mock cycle detection (no cycle)
    mock_cycle_service.detect_cycle.return_value = False
    
    cmd = ModifyTaskDependenciesCommand(
        task_id=task_id_str,
        added_dependencies=[dep_id_str]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    assert len(mock_task.dependencies) == 1
    mock_repo.save.assert_called_once()

def test_add_dependency_cycle_detected(use_case, mock_repo, mock_cycle_service):
    task_id_str = str(TaskId.create().value)
    dep_id_str = str(TaskId.create().value)
    
    mock_task = Mock()
    mock_repo.get.side_effect = lambda id: mock_task if str(id.value) == task_id_str else Mock()
    
    # Simulate cycle
    mock_cycle_service.detect_cycle.return_value = True
    
    cmd = ModifyTaskDependenciesCommand(
        task_id=task_id_str,
        added_dependencies=[dep_id_str]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is False
    assert "Cycle detected" in result.error
    mock_repo.save.assert_not_called()

def test_remove_dependency(use_case, mock_repo):
    task_id_str = str(TaskId.create().value)
    dep_id = TaskId.create()
    dep_id_str = str(dep_id.value)
    
    mock_task = Mock()
    mock_task.dependencies = {dep_id}
    mock_repo.get.return_value = mock_task
    
    cmd = ModifyTaskDependenciesCommand(
        task_id=task_id_str,
        removed_dependencies=[dep_id_str]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    assert len(mock_task.dependencies) == 0
    mock_repo.save.assert_called_once()
