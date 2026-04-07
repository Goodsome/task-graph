# tests/planning/domain/test_task_entity.py
import pytest
from pydantic import ValidationError
from task_graph.planning.domain.enums import TaskStatus, CompletionLogic
from task_graph.planning.domain.services import DependencyResolutionService

class TestTaskEntity:

    def test_immutability_and_validation(self, create_task):
        """Scenario: Immutability & Validation"""
        # 验证负数 Effort 抛出异常 (依赖 Pydantic 校验)
        with pytest.raises(ValidationError):
            create_task(name="Invalid", effort=-1)

    def test_blocking_logic_and(self, create_task, mock_repo):
        """Scenario: Blocking Logic (AND) - Default"""
        dep1 = create_task(status=TaskStatus.DONE)
        dep2 = create_task(status=TaskStatus.PENDING)

        parent = create_task(logic=CompletionLogic.ALL, deps={dep1.id, dep2.id})

        service = DependencyResolutionService()
        is_blocked = service.evaluate_blocking_status(parent, mock_repo)

        assert is_blocked is True, "AND 逻辑下，只要有一个依赖未完成，应被阻塞"

    def test_blocking_logic_and_unblocked(self, create_task, mock_repo):
        dep1 = create_task(status=TaskStatus.DONE)
        dep2 = create_task(status=TaskStatus.DONE)

        parent = create_task(logic=CompletionLogic.ALL, deps={dep1.id, dep2.id})

        service = DependencyResolutionService()
        is_blocked = service.evaluate_blocking_status(parent, mock_repo)

        assert is_blocked is False, "AND 逻辑下，所有依赖完成则不阻塞"
