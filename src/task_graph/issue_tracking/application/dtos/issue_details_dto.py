from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from pydantic import BaseModel
from task_graph.issue_tracking.application.dtos.submitter_dto import SubmitterDTO
from task_graph.issue_tracking.application.dtos.label_dto import LabelDTO
from datetime import datetime
from task_graph.issue_tracking.application.dtos.task_link_dto import TaskLinkDTO
from task_graph.issue_tracking.application.dtos.comment_dto import CommentDTO


class IssueDetailsDTO(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    type: IssueType
    severity: Severity
    status: IssueStatus
    submitter: SubmitterDTO
    labels: list[LabelDTO]
    comments: list[CommentDTO]
    task_links: list[TaskLinkDTO]
    created_at: datetime
    updated_at: datetime
