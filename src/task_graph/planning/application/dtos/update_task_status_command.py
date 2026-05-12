from pydantic import BaseModel


class UpdateTaskStatusCommand(BaseModel):
    task_id: str
    new_status: str
