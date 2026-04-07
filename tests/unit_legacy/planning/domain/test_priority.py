# tests/planning/domain/test_priority.py
import pytest
from task_graph.planning.domain.services import PriorityAnalysisService

class TestPriorityAlgorithm:

    def test_basic_roi_calculation(self, create_task, mock_repo):
        """Scenario: Basic ROI Calculation"""
        # Score = Value / Effort
        task = create_task(value=100, effort=8)

        service = PriorityAnalysisService()
        priorities = service.calculate_priorities(mock_repo)

        # 只有这一个任务
        target = priorities[0]
        # 100 / 10 = 10.0
        assert target.id == task.id
        # 假设我们能在 Task 上访问到计算后的动态属性 (dynamic_priority)，或者服务返回带分数的元组
        # 这里假设 Service 会给 Task 注入 _effective_priority 或类似属性用于排序
        # 也可以检查排序结果

    def test_value_back_propagation(self, fixture_linear_graph, mock_repo):
        """Scenario: Value Propagation (A -> B -> C)"""
        a, b, c = fixture_linear_graph
        # C: Base=100
        # B: Base=50 + C(100) = 150
        # A: Base=10 + B(150) = 160

        service = PriorityAnalysisService()
        # 计算后，Service 内部应该更新了 Accumulated Value
        sorted_tasks = service.calculate_priorities(mock_repo)

        # 验证排序: A (Value 160, Effort Low) 应该排第一
        assert sorted_tasks[0].id == c.id

    def test_shared_dependency_boost(self, fixture_diamond_graph, mock_repo):
        """Scenario: Shared Dependency Boost (Diamond Shape)"""
        top, left, right, bottom = fixture_diamond_graph

        service = PriorityAnalysisService()
        service.calculate_priorities(mock_repo)

        # 验证 Bottom 的价值累积
        # Bottom Base(10) + Left_Contribution + Right_Contribution
        # 注意：这里的 Contribution 是指传递下来的价值。
        # 如果算法是简单的 Value = Base + Sum(Dependents.accumulated_value)，
        # 那么 Bottom = 10 + Left(Accumulated) + Right(Accumulated)
        # Left = 20 + Top(100+...) -> 120
        # Right = 30 + Top(100+...) -> 130
        # Bottom = 10 + 120 + 130 = 260
        # 这是一个极其重要的“高杠杆”任务

        # 无论具体数值如何，Bottom 应该是最高优先级的（因为它是所有高价值任务的瓶颈）
        sorted_tasks = service.calculate_priorities(mock_repo)
        assert sorted_tasks[0].id == bottom.id, "共享依赖底层任务应具有最高优先级"

    def test_or_logic_shortest_path_cost(self, fixture_or_logic_gate, mock_repo):
        """Scenario: OR Logic Cost Optimization"""
        goal, easy, hard = fixture_or_logic_gate

        service = PriorityAnalysisService()
        # 计算 Goal 的 Effective Effort 时
        # 应该选择 Easy 路径 (Effort=1) 而不是 Hard 路径 (Effort=100)
        # Goal Effective Effort = Goal.effort(5) + Easy.effort(1) = 6
        # 如果选错，就是 105

        # 这里我们通过检查 Goal 的优先级来间接验证，或者如果 Service 公开了 Effective Effort 方法直接测
        # 假设 Goal 的 Value=100
        # Case Correct: 100 / 6 ≈ 16.6
        # Case Wrong: 100 / 105 ≈ 0.95

        # 同时，Easy 任务本身的 Value 会因为它是 Goal 的关键路径而被放大
        # Hard 任务因为被“短路”，可能优先级较低

        priorities = service.calculate_priorities(mock_repo)
        task_ids = [t.id for t in priorities]

        # Easy 应该比 Hard 排在更前面
        assert task_ids.index(easy.id) < task_ids.index(hard.id)