from pydantic import BaseModel


class GetIssueDetailsQuery(BaseModel):
    issue_id: str
