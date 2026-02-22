import os
import tempfile
import pytest

from unittest import mock

# Need to patch the env var for DB before any module level initialization
# For E2E tests, it's safer to use a temporary Yaml repository file
# to avoid messing up the user's database or actual files.

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    # Setup temporary file for Yaml repository
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        yaml_path = tmp.name
        
    with mock.patch("task_graph.planning.infrastructure.repositories.yaml_task_repository.YamlTaskRepository.file_path", yaml_path):
        yield yaml_path
        
    # Cleanup
    if os.path.exists(yaml_path):
        os.remove(yaml_path)

def test_delete_task_e2e():
    """
    E2E test evaluating the real execution of MCP tools:
    1. Create a task via `create_task`.
    2. Check the task exists using `get_task_details`.
    3. Delete the task via `delete_task`.
    4. Assert task no longer exists.
    """
    
    # Needs to be imported inside the test so the mock takes effect correctly 
    # if there are any module-level dependencies
    from task_graph.planning.interfaces.mcp_server import (
        create_task,
        get_task_details,
        delete_task,
        _get_container
    )
    
    # 1. Create task
    create_result = create_task(
        project_id="E2E_Test",
        name="Task to be deleted",
        description="This task will be deleted shortly.",
        effort=2,
        base_value=5.0,
        planning_level="atomic"
    )
    
    assert create_result["success"] is True
    task_id = create_result["task_id"]
    assert task_id != ""
    
    # 2. Check task exists
    get_result = get_task_details(task_id=task_id)
    assert get_result["success"] is True
    assert get_result["task"] is not None
    assert get_result["task"]["name"] == "Task to be deleted"
    
    # 3. Delete the task
    delete_result = delete_task(task_id=task_id)
    assert delete_result["success"] is True
    assert delete_result["error"] == ""
    
    # 4. Verify the task doesn't exist
    get_result_after = get_task_details(task_id=task_id)
    assert get_result_after["success"] is False
    assert get_result_after["task"] is None
