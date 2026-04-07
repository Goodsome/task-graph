import pytest
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus, CompletionLogic, PlanningLevel
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.exceptions import TaskNotClaimableError
from task_graph.planning.domain.events import TaskInProgressEvent

class TestTaskClaimBehaviors:
    
    @pytest.fixture
    def ready_task(self):
        return Task.create(
            project_id="test-project",
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
        ready_task.status = TaskStatus.READY
        
        ready_task.claim()
        
        assert ready_task.status == TaskStatus.IN_PROGRESS

    def test_claim_changes_requested_task_success(self, ready_task):
        """Scenario: Successfully claim a CHANGES_REQUESTED task"""
        ready_task.status = TaskStatus.CHANGES_REQUESTED
        
        ready_task.claim()
        
        assert ready_task.status == TaskStatus.IN_PROGRESS

    def test_claim_emits_in_progress_event(self, ready_task):
        """Scenario: claim() publishes TaskInProgressEvent"""
        ready_task.status = TaskStatus.READY
        
        ready_task.claim()
        
        events = ready_task.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskInProgressEvent)
        assert events[0].task_id == str(ready_task.id)
        assert events[0].project_id == ready_task.project_id
        assert events[0].planning_level == ready_task.planning_level

    def test_claim_pending_task_fails(self, ready_task):
        """Scenario: Claiming a PENDING task raises error"""
        ready_task.status = TaskStatus.PENDING
        
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()
        assert ready_task.status == TaskStatus.PENDING

    def test_claim_blocked_task_fails(self, ready_task):
        """Scenario: Claiming a BLOCKED task raises error"""
        ready_task.status = TaskStatus.BLOCKED
        
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()
        assert ready_task.status == TaskStatus.BLOCKED

    def test_claim_already_in_progress_fails(self, ready_task):
        """Scenario: Claiming an IN_PROGRESS task raises error"""
        ready_task.status = TaskStatus.IN_PROGRESS
        
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()

    def test_claim_done_task_fails(self, ready_task):
        """Scenario: Claiming a DONE task raises error"""
        ready_task.status = TaskStatus.DONE
        
        with pytest.raises(TaskNotClaimableError):
            ready_task.claim()
