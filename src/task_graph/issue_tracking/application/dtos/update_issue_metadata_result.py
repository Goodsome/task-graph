from pydantic import BaseModel, Field


class UpdateIssueMetadataResult(BaseModel):
    success: bool
    error: str = Field(default="")
