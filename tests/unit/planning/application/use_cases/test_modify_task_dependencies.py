import pytest
from unittest.mock import Mock, MagicMock
from task_graph.planning.application.use_cases.modify_task_dependencies import (
    ModifyTaskDependencies, 
    ModifyTaskDependenciesCommand
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.services.cycle_detection_service import CycleDetectionService
from task_graph.planning.domain.services.dependency_resolution_service import DependencyResolutionService
from task_graph.planning.domain.value_objects import TaskId
from task_graph.planning.domain.enums import TaskStatus

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def mock_cycle_service():
    return Mock(spec=CycleDetectionService)

@pytest.fixture
def mock_dependency_resolver():
    return Mock(spec=DependencyResolutionService)

@pytest.fixture
def use_case(mock_uow, mock_cycle_service, mock_dependency_resolver):
    return ModifyTaskDependencies(
        uow=mock_uow,
        cycle_detector=mock_cycle_service,
        dependency_resolver=mock_dependency_resolver
    )

def test_add_dependency_success(use_case, mock_repo, mock_cycle_service):
    task_id_str = str(TaskId.create().value)
    dep_id_str = str(TaskId.create().value)
    
    # Mock existing task
    mock_task = Mock()
    mock_task.collect_events.return_value = []
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
    mock_task.collect_events.return_value = []
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
    mock_task.collect_events.return_value = []
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


def test_add_dependency_updates_status_to_pending(use_case, mock_repo, mock_cycle_service, mock_dependency_resolver):
    task_id_str = str(TaskId.create().value)
    dep_id_str = str(TaskId.create().value)
    
    # Mock existing task is READY
    mock_task = MagicMock()
    mock_task.collect_events.return_value = []
    mock_task.id = TaskId.reconstitute(task_id_str)
    mock_task.dependencies = set()
    mock_task.status = TaskStatus.READY
    
    def side_effect_status(status):
        mock_task.status = status
    mock_task._update_status.side_effect = side_effect_status
    
    # Dep task
    mock_dep = MagicMock()
    
    mock_repo.get.side_effect = lambda id: mock_task if str(id.value) == task_id_str else (mock_dep if str(id.value) == dep_id_str else None)
    mock_cycle_service.detect_cycle.return_value = False
    
    # Resolver says BLOCKED after adding dependency
    mock_dependency_resolver.evaluate_blocking_status.return_value = True
    
    cmd = ModifyTaskDependenciesCommand(
        task_id=task_id_str,
        added_dependencies=[dep_id_str]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    # Verify status changed to PENDING (because it is now blocked)
    assert mock_task.status == TaskStatus.PENDING
    mock_dependency_resolver.evaluate_blocking_status.assert_called_once_with(mock_task, mock_repo)


def test_remove_dependency_updates_status_to_ready(use_case, mock_repo, mock_dependency_resolver):
    task_id_str = str(TaskId.create().value)
    dep_id = TaskId.create()
    dep_id_str = str(dep_id.value)
    
    # Mock task is currently PENDING
    mock_task = MagicMock()
    mock_task.collect_events.return_value = []
    mock_task.id = TaskId.reconstitute(task_id_str)
    mock_task.dependencies = {dep_id}
    mock_task.status = TaskStatus.PENDING
    
    def side_effect_status(status):
        mock_task.status = status
    mock_task._update_status.side_effect = side_effect_status
    mock_repo.get.return_value = mock_task
    
    # Resolver says UNBLOCKED after removing dependency
    mock_dependency_resolver.evaluate_blocking_status.return_value = False
    
    cmd = ModifyTaskDependenciesCommand(
        task_id=task_id_str,
        removed_dependencies=[dep_id_str]
    )
    
    result = use_case.execute(cmd)
    
    assert result.success is True
    # Verify status changed to READY
    assert mock_task.status == TaskStatus.READY
    mock_dependency_resolver.evaluate_blocking_status.assert_called_once_with(mock_task, mock_repo)
