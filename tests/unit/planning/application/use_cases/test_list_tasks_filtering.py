import pytest
from unittest.mock import Mock
from task_graph.planning.application.use_cases.list_tasks import ListTasks, ListTasksQuery
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.enums import TaskStatus, PlanningLevel

@pytest.fixture
def mock_repo():
    return Mock(spec=TaskRepository)

@pytest.fixture
def use_case(mock_uow):
    return ListTasks(uow=mock_uow)

def test_list_tasks_filtering_params_passed(use_case, mock_repo):
    """验证 Use Case 正确地将筛选参数传递给 Repository 的 find_paged 方法。"""
    # 虽然目前 execute 可能还没更新到调用 find_paged，
    # 但我们按照设计编写测试。
    
    mock_tasks = []
    mock_repo.find_paged.return_value = (mock_tasks, 0)
    
    query = ListTasksQuery(
        project_id="test-project",
        status=TaskStatus.READY,
        planning_level=PlanningLevel.ATOMIC,
        search="test keyword",
        page=1,
        page_size=10
    )
    
    # 运行 execute。如果逻辑还没改，它可能还在调 find_all()，导致这个测试失败。
    use_case.execute(query)
    
    # 验证是否调用了 find_paged 且参数正确
    mock_repo.find_paged.assert_called_once_with(
        status=TaskStatus.READY,
        project_id="test-project",
        planning_level=PlanningLevel.ATOMIC,
        search="test keyword",
        page=1,
        page_size=10
    )

def test_list_tasks_filtering_defaults(use_case, mock_repo):
    """验证默认参数。"""
    mock_repo.find_paged.return_value = ([], 0)
    
    query = ListTasksQuery() # 此时取默认值
    use_case.execute(query)
    
    # 验证默认值被正确传递
    # 注意：ListTasksQuery 的默认值可能在代码中被定义
    mock_repo.find_paged.assert_called_once()
    args, kwargs = mock_repo.find_paged.call_args
    assert kwargs.get('page') == 1 or args[3] == 1 # 根据位置或关键字
