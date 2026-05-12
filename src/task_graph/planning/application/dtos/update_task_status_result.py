from pydantic import BaseModel, Field


class UpdateTaskStatusResult(BaseModel):
    success: bool
    error: str = Field(default="")
