from pydantic import BaseModel


class GetTaskDetailsQuery(BaseModel):
    task_id: str
