from pydantic import BaseModel, Field


class SubmitTaskResultResult(BaseModel):
    success: bool
    error: str | None = Field(default=None)
