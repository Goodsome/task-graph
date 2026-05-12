from pydantic import BaseModel, Field


class UnlinkIssueFromTaskResult(BaseModel):
    success: bool
    error: str = Field(default="")
