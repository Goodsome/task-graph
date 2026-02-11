import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.review_task import (
    ReviewTask,
    ReviewTaskCommand
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.services.dependency_resolution_service import DependencyResolutionService
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.exceptions import IllegalStateTransitionError

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def mock_resolution_service():
    return Mock(spec=DependencyResolutionService)

@pytest.fixture
def use_case(mock_repo, mock_resolution_service):
    return ReviewTask(
        repository=mock_repo,
        resolution_service=mock_resolution_service
    )

def test_review_task_approved(use_case, mock_repo, mock_resolution_service):
    # Setup
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.id = task_id
    mock_task.status = TaskStatus.REVIEW
    
    mock_repo.get.return_value = mock_task
    
    # Mock review behavior - in real implementation this updates status
    def side_effect_review(approved, feedback):
        if approved:
            mock_task.status = TaskStatus.DONE
    mock_task.review.side_effect = side_effect_review
    mock_task.is_done.side_effect = lambda: mock_task.status == TaskStatus.DONE

    # No dependents for simplicity here
    mock_repo.find_dependents.return_value = []

    # Execute
    cmd = ReviewTaskCommand(
        task_id=task_id_str,
        approved=True,
        feedback="Great job!"
    )
    result = use_case.execute(cmd)

    # Assert
    assert result.success is True
    assert result.task_id == task_id_str
    mock_task.review.assert_called_once_with(approved=True, feedback="Great job!")
    assert mock_task.status == TaskStatus.DONE
    mock_repo.save.assert_called_with(mock_task)

def test_review_task_rejected(use_case, mock_repo):
    # Setup
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.id = task_id
    mock_task.status = TaskStatus.REVIEW
    
    mock_repo.get.return_value = mock_task
    
    def side_effect_review(approved, feedback):
        if not approved:
            mock_task.status = TaskStatus.REJECTED
    mock_task.review.side_effect = side_effect_review
    mock_task.is_done.return_value = False

    # Execute
    cmd = ReviewTaskCommand(
        task_id=task_id_str,
        approved=False,
        feedback="Formatting is off."
    )
    result = use_case.execute(cmd)

    # Assert
    assert result.success is True
    assert mock_task.status == TaskStatus.REJECTED
    mock_task.review.assert_called_once_with(approved=False, feedback="Formatting is off.")
    mock_repo.save.assert_called_with(mock_task)

def test_review_task_invalid_state(use_case, mock_repo):
    # Setup
    task_id = TaskId.create()
    task_id_str = str(task_id.value)
    
    mock_task = Mock()
    mock_task.status = TaskStatus.IN_PROGRESS
    mock_repo.get.return_value = mock_task

    # review() should raise error if not in REVIEW state
    mock_task.review.side_effect = IllegalStateTransitionError("Invalid state")

    # Execute
    cmd = ReviewTaskCommand(
        task_id=task_id_str,
        approved=True,
        feedback="Ignore state"
    )
    result = use_case.execute(cmd)

    # Assert
    assert result.success is False
    assert "Invalid state" in result.error
