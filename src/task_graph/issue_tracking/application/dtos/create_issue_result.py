from pydantic import BaseModel, Field


class CreateIssueResult(BaseModel):
    success: bool
    issue_id: str
    error: str = Field(default="")
