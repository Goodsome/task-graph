from pydantic import BaseModel


class DecomposeTaskCommand(BaseModel):
    """Command to decompose a task into sub-tasks."""

    task_id: str
