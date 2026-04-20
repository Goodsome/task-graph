"""
单元测试：AcceptanceCriterion 值对象

验收标准：
  - Given: 所有必填字段均已提供
    When: 构造 AcceptanceCriterion 实例
    Then: 实例创建成功，各字段值与输入一致

  - Given: test_type 未提供
    When: 构造 AcceptanceCriterion 实例
    Then: test_type 默认值为 "unit"

  - Given: 一个有效的 AcceptanceCriterion 实例
    When: 调用 model_dump(mode="json")
    Then: 返回包含所有 BDD 字段的字典，可无损反序列化

  - Given: test_type 为不支持的字符串
    When: 构造 AcceptanceCriterion 实例
    Then: 抛出 ValidationError
"""

import pytest
from pydantic import ValidationError

from task_graph.planning.domain.value_objects.acceptance_criterion import AcceptanceCriterion


# ─────────────────────────── 正常路径 ─────────────────────────────


class TestAcceptanceCriterionCreation:
    def test_creates_with_all_required_fields(self) -> None:
        """正常构建：提供全部必填字段时实例创建成功"""
        ac = AcceptanceCriterion(
            title="用户登录后可以查看任务列表",
            given="用户已通过身份验证",
            when="用户访问任务列表页面",
            then="系统返回属于该用户的任务列表",
        )
        assert ac.title == "用户登录后可以查看任务列表"
        assert ac.given == "用户已通过身份验证"
        assert ac.when == "用户访问任务列表页面"
        assert ac.then == "系统返回属于该用户的任务列表"

    def test_default_test_type_is_unit(self) -> None:
        """默认值：未指定 test_type 时应默认为 'unit'"""
        ac = AcceptanceCriterion(
            title="任务标题",
            given="前置条件",
            when="触发动作",
            then="预期结果",
        )
        assert ac.test_type == "unit"

    def test_explicit_test_type_subcutaneous(self) -> None:
        """显式指定 test_type 为 subcutaneous"""
        ac = AcceptanceCriterion(
            title="API 集成验证",
            given="服务已启动",
            when="发送 POST /tasks 请求",
            then="任务被创建并返回 201",
            test_type="subcutaneous",
        )
        assert ac.test_type == "subcutaneous"

    @pytest.mark.parametrize("test_type", ["unit", "integration", "subcutaneous", "e2e"])
    def test_all_valid_test_types_accepted(self, test_type: str) -> None:
        """所有合法的 test_type 枚举值均应被接受"""
        ac = AcceptanceCriterion(
            title="标题",
            given="给定",
            when="当",
            then="则",
            test_type=test_type,
        )
        assert ac.test_type == test_type


# ─────────────────────────── 序列化 ─────────────────────────────


class TestAcceptanceCriterionSerialization:
    def test_model_dump_returns_all_fields(self) -> None:
        """序列化：model_dump 应包含所有 BDD 字段"""
        ac = AcceptanceCriterion(
            title="创建任务成功",
            given="项目已存在",
            when="调用 create_task 用例",
            then="新任务被持久化并返回任务 ID",
            test_type="integration",
        )
        data = ac.model_dump(mode="json")
        assert data == {
            "title": "创建任务成功",
            "given": "项目已存在",
            "when": "调用 create_task 用例",
            "then": "新任务被持久化并返回任务 ID",
            "test_type": "integration",
        }

    def test_round_trip_serialization(self) -> None:
        """无损往返：序列化再反序列化后值完全相同"""
        original = AcceptanceCriterion(
            title="幂等测试",
            given="任务已存在",
            when="重复调用 save",
            then="数据库中只有一条记录",
            test_type="e2e",
        )
        restored = AcceptanceCriterion.model_validate(original.model_dump(mode="json"))
        assert restored == original


# ─────────────────────────── 异常路径 ─────────────────────────────


class TestAcceptanceCriterionValidation:
    def test_invalid_test_type_raises_validation_error(self) -> None:
        """非法 test_type 应抛出 ValidationError"""
        with pytest.raises(ValidationError):
            AcceptanceCriterion(
                title="标题",
                given="给定",
                when="当",
                then="则",
                test_type="manual",  # 不在 Literal 枚举中
            )

    @pytest.mark.parametrize("missing_field", ["title", "given", "when", "then"])
    def test_missing_required_field_raises_validation_error(self, missing_field: str) -> None:
        """缺少任意必填字段均应抛出 ValidationError"""
        fields = {
            "title": "标题",
            "given": "给定",
            "when": "当",
            "then": "则",
        }
        del fields[missing_field]
        with pytest.raises(ValidationError):
            AcceptanceCriterion(**fields)
