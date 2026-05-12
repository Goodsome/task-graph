from pydantic import BaseModel, Field


class LinkIssueToTaskResult(BaseModel):
    success: bool
    error: str = Field(default="")
