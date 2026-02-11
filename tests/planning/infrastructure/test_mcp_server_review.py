
import pytest
from unittest.mock import MagicMock, patch
from task_graph.planning.interfaces.mcp_server import review_task
from task_graph.planning.application.use_cases.review_task import ReviewTaskResult

@patch('task_graph.planning.interfaces.mcp_server._get_container')
def test_mcp_review_task_success(mock_get_container):
    # Mock container and use case
    mock_container = MagicMock()
    mock_use_case = MagicMock()
    mock_get_container.return_value = mock_container
    mock_container.review_task.return_value = mock_use_case

    # Mock success result
    mock_use_case.execute.return_value = ReviewTaskResult(
        success=True,
        task_id="task-123",
        affected_tasks=["task-456"]
    )

    # Call the tool function
    result = review_task(
        task_id="task-123",
        approved=True,
        feedback="Looks good"
    )

    # Verify result
    assert result["success"] is True
    assert result["affected_tasks"] == ["task-456"]
    assert result["error"] == ""

    # Verify correct call to use case
    args = mock_use_case.execute.call_args[0][0]
    assert args.task_id == "task-123"
    assert args.approved is True
    assert args.feedback == "Looks good"


@patch('task_graph.planning.interfaces.mcp_server._get_container')
def test_mcp_review_task_failure(mock_get_container):
    # Mock container and use case
    mock_container = MagicMock()
    mock_use_case = MagicMock()
    mock_get_container.return_value = mock_container
    mock_container.review_task.return_value = mock_use_case

    # Mock failure result
    mock_use_case.execute.return_value = ReviewTaskResult(
        success=False,
        task_id="task-123",
        error="Task not in REVIEW state"
    )

    # Call the tool
    result = review_task(
        task_id="task-123",
        approved=True,
        feedback="Should fail"
    )

    # Verify result
    assert result["success"] is False
    assert result["error"] == "Task not in REVIEW state"
