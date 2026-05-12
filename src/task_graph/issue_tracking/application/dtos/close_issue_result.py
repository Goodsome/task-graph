from pydantic import BaseModel, Field


class CloseIssueResult(BaseModel):
    success: bool
    error: str = Field(default="")
