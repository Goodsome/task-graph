# tests/planning/domain/test_cycles.py
import pytest
from task_graph.planning.domain.services import CycleDetectionService

class TestCycleDetection:

    def test_self_loop(self, create_task, mock_repo):
        """Scenario: Self Loop"""
        a = create_task(name="A")
        service = CycleDetectionService()

        # A -> A
        assert service.detect_cycle(target_task_id=a.id, new_dependency_id=a.id, repository=mock_repo) is True

    def test_simple_cycle(self, create_task, mock_repo):
        """Scenario: Simple Cycle (A -> B -> A)"""
        a = create_task(name="A")
        b = create_task(name="B", deps={a.id}) # B depends on A

        service = CycleDetectionService()

        # Try making A depend on B
        assert service.detect_cycle(target_task_id=a.id, new_dependency_id=b.id, repository=mock_repo) is True

    def test_complex_cycle(self, create_task, mock_repo):
        """Scenario: Complex Cycle"""
        # A -> B -> C -> D
        a = create_task(name="A")
        b = create_task(name="B", deps={a.id})
        c = create_task(name="C", deps={b.id})
        d = create_task(name="D", deps={c.id})

        service = CycleDetectionService()

        # Try A -> D (Create cycle D -> ... -> A)
        # 注意: detect_cycle(target=A, new_dep=D) 意味着 A 依赖 D
        assert service.detect_cycle(target_task_id=a.id, new_dependency_id=d.id, repository=mock_repo) is True

    def test_diamond_valid_dag(self, create_task, fixture_diamond_graph, mock_repo):
        """Scenario: False Positive (Diamond)"""
        # Diamond graph is valid, should not detect cycle
        # Top -> Left, Top -> Right, Left -> Bottom, Right -> Bottom
        top, left, right, bottom = fixture_diamond_graph

        service = CycleDetectionService()

        # 检查现有连接不应报错（虽然 detect_cycle 通常用于新增边之前的检查）
        # 这里我们可以测试一个不构成环的新连接，例如 Bottom -> External
        external = create_task(name="External")

        assert service.detect_cycle(bottom.id, external.id, mock_repo) is False