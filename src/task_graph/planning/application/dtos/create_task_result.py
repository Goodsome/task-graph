from pydantic import BaseModel


class CreateTaskResult(BaseModel):
    success: bool
    task_id: str
    error: str
