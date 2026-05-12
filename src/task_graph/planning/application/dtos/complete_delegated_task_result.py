from pydantic import BaseModel


class CompleteDelegatedTaskResult(BaseModel):
    status: str
    task_id: str
    message: str
