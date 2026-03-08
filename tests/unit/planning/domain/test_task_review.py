import pytest
from task_graph.planning.domain.enums import TaskStatus, CompletionLogic
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.exceptions import IllegalStateTransitionError
from task_graph.planning.domain.events import (
    TaskCompletedEvent,
    TaskChangesRequestedEvent,
)

class TestTaskReview:

    @pytest.fixture
    def reviewable_task(self):
        return Task.create(
            project_id="test-project",
            name="Reviewable Task",
            description="Testing review logic",
            effort=StoryPoint.create(3),
            base_value=ValueScore.create(5.0),
            completion_logic=CompletionLogic.ALL,
            dependencies=set(),
            planning_level="atomic"
        )

    def test_review_approved(self, reviewable_task):
        reviewable_task.status = TaskStatus.REVIEW
        
        reviewable_task.review(approved=True, feedback="Good job")
        
        assert reviewable_task.status == TaskStatus.DONE
        assert reviewable_task.review_feedback is not None
        assert reviewable_task.review_feedback.decision == "approved"
        assert reviewable_task.review_feedback.comment == "Good job"

    def test_review_approved_emits_completed_event(self, reviewable_task):
        """Scenario: review(approved=True) publishes TaskCompletedEvent"""
        reviewable_task.status = TaskStatus.REVIEW
        
        reviewable_task.review(approved=True, feedback="LGTM")
        
        events = reviewable_task.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCompletedEvent)
        assert events[0].task_id == str(reviewable_task.id)
        assert events[0].planning_level == reviewable_task.planning_level

    def test_review_changes_requested(self, reviewable_task):
        reviewable_task.status = TaskStatus.REVIEW
        
        reviewable_task.review(approved=False, feedback="Fix lint errors")
        
        assert reviewable_task.status == TaskStatus.CHANGES_REQUESTED
        assert reviewable_task.review_feedback is not None
        assert reviewable_task.review_feedback.decision == "changes_requested"
        assert reviewable_task.review_feedback.comment == "Fix lint errors"

    def test_review_changes_requested_emits_event(self, reviewable_task):
        """Scenario: review(approved=False) publishes TaskChangesRequestedEvent"""
        reviewable_task.status = TaskStatus.REVIEW
        
        reviewable_task.review(approved=False, feedback="Fix formatting")
        
        events = reviewable_task.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskChangesRequestedEvent)
        assert events[0].task_id == str(reviewable_task.id)
        assert events[0].feedback == "Fix formatting"
        assert events[0].planning_level == reviewable_task.planning_level

    def test_review_invalid_state(self, reviewable_task):
        reviewable_task.status = TaskStatus.IN_PROGRESS
        
        with pytest.raises(IllegalStateTransitionError):
            reviewable_task.review(approved=True, feedback="Should fail")
