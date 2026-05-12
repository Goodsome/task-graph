from datetime import datetime
from pydantic import BaseModel


class TaskLinkDTO(BaseModel):
    task_id: str
    linked_at: datetime
