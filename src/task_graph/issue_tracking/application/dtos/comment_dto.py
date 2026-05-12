from datetime import datetime
from pydantic import BaseModel


class CommentDTO(BaseModel):
    id: str
    content: str
    author: str
    created_at: datetime
