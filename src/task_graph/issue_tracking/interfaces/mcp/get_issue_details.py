from task_graph.issue_tracking.application.use_cases.get_issue_details import (
    GetIssueDetails,
)
from dependency_injector.wiring import Provide, inject
from task_graph.issue_tracking.application.dtos.get_issue_details_result import (
    GetIssueDetailsResult,
)
from task_graph.issue_tracking.application.dtos.get_issue_details_query import (
    GetIssueDetailsQuery,
)


@inject
def _get_issue_details(
    query: GetIssueDetailsQuery,
    use_case: GetIssueDetails = Provide["issue_tracking.get_issue_details"],
) -> GetIssueDetailsResult:
    return use_case.execute(query)


def get_issue_details(query: GetIssueDetailsQuery) -> GetIssueDetailsResult:
    """Get full issue details including comments and labels"""
    return _get_issue_details(query)
