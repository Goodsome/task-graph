from pydantic import BaseModel, Field


class ClaimTaskResult(BaseModel):
    success: bool
    task_id: str
    error: str = Field(default_factory=str)
    error_code: str = Field(default_factory=str)
