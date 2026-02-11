import pytest
from unittest.mock import MagicMock, patch
from task_graph.planning.interfaces.mcp_server import get_task_details, _get_container
from task_graph.planning.application.use_cases.get_task_details import GetTaskDetailsResult

@patch('task_graph.planning.interfaces.mcp_server.PlanningContainer')
def test_get_task_details_tool(mock_container_cls):
    # Setup mock container and use case
    mock_container = mock_container_cls.return_value
    mock_use_case = MagicMock()
    mock_container.get_task_details.return_value = mock_use_case
    
    # Setup global container
    with patch('task_graph.planning.interfaces.mcp_server._container', mock_container):
        
        # Test success case
        mock_use_case.execute.return_value = GetTaskDetailsResult(
            success=True,
            task={"id": "123", "name": "Test Task"},
            error=None
        )
        
        result = get_task_details(task_id="123")
        
        assert result["success"] is True
        assert result["task"] == {"id": "123", "name": "Test Task"}
        assert result["error"] is None
        
        # Test failure case
        mock_use_case.execute.return_value = GetTaskDetailsResult(
            success=False,
            task=None,
            error="Not found"
        )
        
        result = get_task_details(task_id="999")
        
        assert result["success"] is False
        assert result["task"] is None
        assert result["error"] == "Not found"
