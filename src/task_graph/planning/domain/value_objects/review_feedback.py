from task_graph.shared.models import ValueObject


class ReviewFeedback(ValueObject):
    """任务规划者的验收意见"""

    comment: str
    decision: str
