from pydantic import BaseModel, Field


class ReviewTaskResult(BaseModel):
    success: bool
    task_id: str
    affected_tasks: list[str] = Field(default_factory=list)
    error: str = Field(default="")
