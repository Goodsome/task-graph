from pydantic import BaseModel


class AddCommentCommand(BaseModel):
    issue_id: str
    content: str
    author: str
