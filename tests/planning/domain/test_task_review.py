import pytest
from task_graph.planning.domain.enums import TaskStatus, CompletionLogic
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.exceptions import IllegalStateTransitionError

class TestTaskReview:

    @pytest.fixture
    def reviewable_task(self):
        return Task.create(
            name="Reviewable Task",
            description="Testing review logic",
            effort=StoryPoint.create(3),
            base_value=ValueScore.create(5.0),
            completion_logic=CompletionLogic.ALL,
            dependencies=set(),
            planning_level="atomic"
        )

    def test_review_approved(self, reviewable_task):
        # Transition to REVIEW first
        reviewable_task.status = TaskStatus.REVIEW
        
        reviewable_task.review(approved=True, feedback="Good job")
        
        assert reviewable_task.status == TaskStatus.DONE
        assert reviewable_task.review_feedback is not None
        assert reviewable_task.review_feedback.decision == "approved"
        assert reviewable_task.review_feedback.comment == "Good job"

    def test_review_rejected(self, reviewable_task):
        # Transition to REVIEW first
        reviewable_task.status = TaskStatus.REVIEW
        
        reviewable_task.review(approved=False, feedback="Fix lint errors")
        
        assert reviewable_task.status == TaskStatus.REJECTED
        assert reviewable_task.review_feedback is not None
        assert reviewable_task.review_feedback.decision == "rejected"
        assert reviewable_task.review_feedback.comment == "Fix lint errors"

    def test_review_invalid_state(self, reviewable_task):
        reviewable_task.status = TaskStatus.IN_PROGRESS
        
        with pytest.raises(IllegalStateTransitionError):
            reviewable_task.review(approved=True, feedback="Should fail")
