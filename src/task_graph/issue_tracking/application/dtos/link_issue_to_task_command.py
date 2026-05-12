from pydantic import BaseModel


class LinkIssueToTaskCommand(BaseModel):
    issue_id: str
    task_id: str
