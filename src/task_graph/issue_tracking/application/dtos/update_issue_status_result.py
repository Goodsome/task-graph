from pydantic import BaseModel, Field


class UpdateIssueStatusResult(BaseModel):
    success: bool
    error: str = Field(default="")
