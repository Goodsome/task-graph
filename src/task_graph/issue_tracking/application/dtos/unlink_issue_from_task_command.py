from pydantic import BaseModel


class UnlinkIssueFromTaskCommand(BaseModel):
    issue_id: str
    task_id: str
