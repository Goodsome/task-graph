import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.claim_task import (
    ClaimTask,
    ClaimTaskCommand,
    ClaimTaskResult
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.services.dependency_resolution_service import DependencyResolutionService
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.exceptions import TaskNotClaimableError

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def mock_dependency_service():
    return Mock(spec=DependencyResolutionService)

@pytest.fixture
def use_case(mock_uow, mock_dependency_service):
    return ClaimTask(
        uow=mock_uow,
        dependency_service=mock_dependency_service
    )

def test_claim_task_success(use_case, mock_repo, mock_dependency_service):
    # Given
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.id = task_id
    mock_task.status = TaskStatus.READY
    mock_task.is_claimable.return_value = True
    
    mock_repo.get.return_value = mock_task
    mock_dependency_service.evaluate_blocking_status.return_value = False
    
    cmd = ClaimTaskCommand(task_id=task_id_str)
    
    # When
    result = use_case.execute(cmd)
    
    # Then
    assert result.success is True
    assert result.task_id == task_id_str
    mock_task.claim.assert_called_once()
    mock_repo.save.assert_called_once_with(mock_task)

def test_claim_task_not_found(use_case, mock_repo):
    # Given
    task_id_str = "non-existent-id"
    mock_repo.get.return_value = None
    
    cmd = ClaimTaskCommand(task_id=task_id_str)
    
    # When
    result = use_case.execute(cmd)
    
    # Then
    assert result.success is False
    assert result.error_code == "TASK_NOT_FOUND"
    assert "not found" in result.error.lower()

def test_claim_task_not_ready(use_case, mock_repo):
    # Given
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.id = task_id
    mock_task.status = TaskStatus.PENDING
    mock_task.is_claimable.return_value = False
    
    mock_repo.get.return_value = mock_task
    
    cmd = ClaimTaskCommand(task_id=task_id_str)
    
    # When
    result = use_case.execute(cmd)
    
    # Then
    assert result.success is False
    assert result.error_code == "TASK_NOT_READY"

def test_claim_task_already_claimed(use_case, mock_repo):
    # Given
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.id = task_id
    mock_task.status = TaskStatus.IN_PROGRESS
    mock_task.is_claimable.return_value = False
    
    mock_repo.get.return_value = mock_task
    
    cmd = ClaimTaskCommand(task_id=task_id_str)
    
    # When
    result = use_case.execute(cmd)
    
    # Then
    assert result.success is False
    assert result.error_code == "ALREADY_CLAIMED"

def test_claim_task_blocked_by_dependencies(use_case, mock_repo, mock_dependency_service):
    # Given
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.id = task_id
    mock_task.status = TaskStatus.READY
    mock_task.is_claimable.return_value = True
    
    mock_repo.get.return_value = mock_task
    # Even if status is READY, double check says it's blocked
    mock_dependency_service.evaluate_blocking_status.return_value = True
    
    cmd = ClaimTaskCommand(task_id=task_id_str)
    
    # When
    result = use_case.execute(cmd)
    
    # Then
    assert result.success is False
    assert result.error_code == "TASK_BLOCKED"

def test_claim_task_domain_exception(use_case, mock_repo, mock_dependency_service):
    # Given
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.collect_events.return_value = []
    mock_task.id = task_id
    mock_task.status = TaskStatus.READY
    mock_task.is_claimable.return_value = True
    mock_task.claim.side_effect = TaskNotClaimableError("Domain error")
    
    mock_repo.get.return_value = mock_task
    mock_dependency_service.evaluate_blocking_status.return_value = False
    
    cmd = ClaimTaskCommand(task_id=task_id_str)
    
    # When
    result = use_case.execute(cmd)
    
    # Then
    assert result.success is False
    assert result.error_code == "TASK_NOT_READY"
    assert "Domain error" in result.error
