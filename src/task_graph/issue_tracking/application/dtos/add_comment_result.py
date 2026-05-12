from pydantic import BaseModel, Field


class AddCommentResult(BaseModel):
    success: bool
    comment_id: str
    error: str = Field(default="")
