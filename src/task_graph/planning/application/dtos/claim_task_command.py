from pydantic import BaseModel, Field


class ClaimTaskCommand(BaseModel):
    task_id: str
    executor_id: str = Field(default_factory=str)
