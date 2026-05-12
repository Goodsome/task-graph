from pydantic import BaseModel


class ReviewTaskCommand(BaseModel):
    task_id: str
    approved: bool
    feedback: str
