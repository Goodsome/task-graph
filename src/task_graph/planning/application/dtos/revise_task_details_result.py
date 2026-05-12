from pydantic import BaseModel, Field


class ReviseTaskDetailsResult(BaseModel):
    success: bool
    error: str = Field(default="")
