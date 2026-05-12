from pydantic import BaseModel


class UnlockTaskCommand(BaseModel):
    task_id: str
