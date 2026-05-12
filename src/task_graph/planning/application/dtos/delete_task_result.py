from pydantic import BaseModel, Field


class DeleteTaskResult(BaseModel):
    success: bool
    error: str | None = Field(default="")
