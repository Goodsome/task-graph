import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.suggest_next_action import (
    SuggestNextAction,
    SuggestNextActionQuery
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.services import PriorityAnalysisService
from task_graph.planning.domain.enums import TaskStatus

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def mock_priority_service():
    return Mock(spec=PriorityAnalysisService)

@pytest.fixture
def use_case(mock_uow, mock_priority_service):
    return SuggestNextAction(
        uow=mock_uow,
        priority_service=mock_priority_service
    )

def test_suggest_next_action_filtering(use_case, mock_repo, mock_priority_service):
    # Setup tasks with different statii
    task_ready = Mock(status=TaskStatus.READY)
    task_ready.is_claimable.return_value = True
    task_progress = Mock(status=TaskStatus.IN_PROGRESS)
    task_progress.is_claimable.return_value = True
    task_blocked = Mock(status=TaskStatus.BLOCKED)
    task_blocked.is_claimable.return_value = False
    task_done = Mock(status=TaskStatus.DONE)
    task_done.is_claimable.return_value = False
    
    # Service returns them in some order
    mock_priority_service.calculate_priorities.return_value = [
        task_progress, 
        task_ready, 
        task_blocked, 
        task_done
    ]
    
    query = SuggestNextActionQuery(top_n=5)
    result = use_case.execute(query)
    
    # Should only return READY and IN_PROGRESS
    assert len(result.tasks) == 2
    assert task_progress in result.tasks
    assert task_ready in result.tasks
    assert task_blocked not in result.tasks
    assert task_done not in result.tasks

def test_suggest_next_action_top_n(use_case, mock_repo, mock_priority_service):
    tasks = [Mock(status=TaskStatus.READY) for _ in range(10)]
    mock_priority_service.calculate_priorities.return_value = tasks
    
    query = SuggestNextActionQuery(top_n=3)
    result = use_case.execute(query)
    
    assert len(result.tasks) == 3
