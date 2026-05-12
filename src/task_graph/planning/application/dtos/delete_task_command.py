from pydantic import BaseModel


class DeleteTaskCommand(BaseModel):
    task_id: str
