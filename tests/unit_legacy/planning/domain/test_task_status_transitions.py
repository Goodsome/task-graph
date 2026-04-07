"""Tests for Task aggregate status transition behaviors: mark_ready, mark_completed, set_output."""
import pytest
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus, CompletionLogic, PlanningLevel
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.exceptions import IllegalStateTransitionError
from task_graph.planning.domain.events import (
    TaskReadyEvent,
    TaskCompletedEvent,
    TaskReviewRequestedEvent,
    TaskBlockedEvent,
)


@pytest.fixture
def task():
    return Task.create(
        project_id="test-project",
        name="Test Task",
        description="Status transition test",
        effort=StoryPoint.create(2),
        base_value=ValueScore.create(5.0),
        completion_logic=CompletionLogic.ALL,
        dependencies=set(),
        planning_level=PlanningLevel.ATOMIC,
    )


class TestMarkReady:

    @pytest.mark.parametrize("initial_status", [TaskStatus.PENDING, TaskStatus.BLOCKED])
    def test_mark_ready_from_valid_status(self, task, initial_status):
        task.status = initial_status
        task.mark_ready()

        assert task.status == TaskStatus.READY
        events = task.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskReadyEvent)
        assert events[0].task_id == str(task.id)
        assert events[0].planning_level == task.planning_level

    @pytest.mark.parametrize(
        "initial_status",
        [TaskStatus.READY, TaskStatus.IN_PROGRESS, TaskStatus.DONE, TaskStatus.REVIEW],
    )
    def test_mark_ready_from_invalid_status_raises(self, task, initial_status):
        task.status = initial_status
        with pytest.raises(IllegalStateTransitionError):
            task.mark_ready()


class TestMarkCompleted:

    @pytest.mark.parametrize(
        "initial_status",
        [TaskStatus.REVIEW, TaskStatus.IN_PROGRESS, TaskStatus.READY],
    )
    def test_mark_completed_from_valid_status(self, task, initial_status):
        task.status = initial_status
        task.mark_completed()

        assert task.status == TaskStatus.DONE
        events = task.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCompletedEvent)
        assert events[0].planning_level == task.planning_level

    @pytest.mark.parametrize(
        "initial_status",
        [TaskStatus.PENDING, TaskStatus.BLOCKED, TaskStatus.DONE],
    )
    def test_mark_completed_from_invalid_status_raises(self, task, initial_status):
        task.status = initial_status
        with pytest.raises(IllegalStateTransitionError):
            task.mark_completed()


class TestSetOutput:

    def test_set_output_success_transitions_to_review(self, task):
        task.status = TaskStatus.IN_PROGRESS
        output = TaskOutput(summary="Done", artifacts=["file.txt"])

        task.set_output(output)

        assert task.status == TaskStatus.REVIEW
        assert task.output == output
        events = task.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskReviewRequestedEvent)
        assert events[0].planning_level == task.planning_level

    def test_set_output_with_error_transitions_to_blocked(self, task):
        task.status = TaskStatus.IN_PROGRESS
        output = TaskOutput(summary="Failed", artifacts=[], error="Runtime crash")

        task.set_output(output)

        assert task.status == TaskStatus.BLOCKED
        assert task.output == output
        events = task.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskBlockedEvent)
        assert events[0].reason == "Runtime crash"
        assert events[0].planning_level == task.planning_level

    def test_set_output_from_invalid_status_raises(self, task):
        task.status = TaskStatus.READY
        output = TaskOutput(summary="Done", artifacts=[])

        with pytest.raises(IllegalStateTransitionError):
            task.set_output(output)
