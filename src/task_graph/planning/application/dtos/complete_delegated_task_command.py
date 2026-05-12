from pydantic import BaseModel


class CompleteDelegatedTaskCommand(BaseModel):
    task_id: str
