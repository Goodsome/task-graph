import pytest
from unittest.mock import MagicMock, patch
from task_graph.planning.interfaces.mcp_server import delete_task, _get_container
from task_graph.planning.application.use_cases.delete_task import DeleteTaskResult

@patch('task_graph.planning.interfaces.mcp_server.PlanningContainer')
def test_delete_task_tool(mock_container_cls):
    # Setup mock container and use case
    mock_container = mock_container_cls.return_value
    mock_use_case = MagicMock()
    mock_container.delete_task.return_value = mock_use_case
    
    # Setup global container
    with patch('task_graph.planning.interfaces.mcp_server._container', mock_container):
        
        # Test success case
        mock_use_case.execute.return_value = DeleteTaskResult(
            success=True,
            error=""
        )
        
        result = delete_task(task_id="123")
        
        assert result["success"] is True
        assert result["error"] == ""
        
        # Test failure case
        mock_use_case.execute.return_value = DeleteTaskResult(
            success=False,
            error="Task not found"
        )
        
        result = delete_task(task_id="999")
        
        assert result["success"] is False
        assert result["error"] == "Task not found"
