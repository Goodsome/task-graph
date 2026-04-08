import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.list_tasks import ListTasks, ListTasksQuery
from task_graph.planning.domain.ports.task_repository import TaskRepository

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def use_case(mock_uow):
    return ListTasks(uow=mock_uow)

def test_list_tasks_pagination(use_case, mock_repo):
    # Setup 25 mock tasks
    mock_tasks = [Mock() for _ in range(25)]
    for i, t in enumerate(mock_tasks):
        t.to_summary_dict.return_value = {"id": i}
    
    # Mock find_paged to handle pagination
    def mock_find_paged(status=None, project_id=None, scope_level=None, search=None, page=1, page_size=10):
        start = (page - 1) * page_size
        end = start + page_size
        return mock_tasks[start:end], len(mock_tasks)
        
    mock_repo.find_paged.side_effect = mock_find_paged
    
    # Request page 2, size 10 -> items 10-19
    query = ListTasksQuery(page=2, page_size=10)
    result = use_case.execute(query)
    
    assert result.total_count == 25
    assert result.total_pages == 3
    assert result.current_page == 2
    assert len(result.tasks) == 10
    assert result.tasks[0]["id"] == 10
    assert result.tasks[-1]["id"] == 19

def test_list_tasks_empty(use_case, mock_repo):
    mock_repo.find_paged.return_value = ([], 0)
    
    query = ListTasksQuery(page=1, page_size=10)
    result = use_case.execute(query)
    
    assert result.total_count == 0
    assert result.total_pages == 1
    assert len(result.tasks) == 0

def test_list_tasks_out_of_bounds(use_case, mock_repo):
    mock_tasks = [Mock()] * 5
    mock_repo.find_paged.return_value = ([], 5)
    
    query = ListTasksQuery(page=2, page_size=10)
    result = use_case.execute(query)
    
    # Depending on implementation, this returns empty list
    assert len(result.tasks) == 0
    assert result.total_pages == 1
