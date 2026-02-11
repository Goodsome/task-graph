import pytest
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus, CompletionLogic, PlanningLevel
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.exceptions import TaskNotClaimableError

class TestTaskClaimBehaviors:
    
    @pytest.fixture
    def ready_task(self):
        return Task.create(
            name="Ready Task",
            description="A task that is ready to be claimed",
            effort=StoryPoint.create(1),
            base_value=ValueScore.create(10),
            completion_logic=CompletionLogic.ALL,
            dependencies=set(),
            planning_level=PlanningLevel.ATOMIC
        )

    def test_claim_ready_task_success(self, ready_task):
        """Scenario: Successfully claim a READY task"""
        # Given a READY task (created with PENDING by default in factory, but Task.create sets status)
        # Actually Task.create() sets status to PENDING
        ready_task.status = TaskStatus.READY
        
        # When
        ready_task.claim()
        
        # Then
        assert ready_task.status == TaskStatus.IN_PROGRESS

    def test_claim_pending_task_fails(self, ready_task):
        """Scenario: Claiming a PENDING task raises error"""
        # Given
        ready_task.status = TaskStatus.PENDING
        
        # When / Then
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()
        assert ready_task.status == TaskStatus.PENDING

    def test_claim_blocked_task_fails(self, ready_task):
        """Scenario: Claiming a BLOCKED task raises error"""
        # Given
        ready_task.status = TaskStatus.BLOCKED
        
        # When / Then
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()
        assert ready_task.status == TaskStatus.BLOCKED

    def test_claim_already_in_progress_fails(self, ready_task):
        """Scenario: Claiming an IN_PROGRESS task raises error"""
        # Given
        ready_task.status = TaskStatus.IN_PROGRESS
        
        # When / Then
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()

    def test_claim_done_task_fails(self, ready_task):
        """Scenario: Claiming a DONE task raises error"""
        # Given
        ready_task.status = TaskStatus.DONE
        
        # When / Then
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()
