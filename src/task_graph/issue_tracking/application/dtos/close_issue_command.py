from pydantic import BaseModel, Field


class CloseIssueCommand(BaseModel):
    issue_id: str
    resolution: str | None = Field(default=None)
