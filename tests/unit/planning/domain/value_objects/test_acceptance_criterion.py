import pytest
from pydantic import ValidationError
from task_graph.planning.domain.value_objects.acceptance_criterion import AcceptanceCriterion


class TestAcceptanceCriterionCreation:
    def test_create_valid_acceptance_criterion(self) -> None:
        """正常场景：提供所有必填字段应成功创建实例"""
        ac = AcceptanceCriterion(
            title="User Login",
            given="User is on login page",
            when="User enters credentials",
            then="User should be redirected to dashboard",
        )

        assert ac.title == "User Login"
        assert ac.given == "User is on login page"
        assert ac.when == "User enters credentials"
        assert ac.then == "User should be redirected to dashboard"


class TestAcceptanceCriterionSerialization:
    def test_to_dict_preserves_data(self) -> None:
        """序列化：转换为字典时应保留所有字段"""
        ac = AcceptanceCriterion(
            title="AC1",
            given="G1",
            when="W1",
            then="T1",
        )

        data = ac.model_dump()

        assert data == {
            "title": "AC1",
            "given": "G1",
            "when": "W1",
            "then": "T1",
        }

    def test_from_json_serialization(self) -> None:
        """反序列化：从 JSON 数据（字典）恢复对象"""
        original = AcceptanceCriterion(
            title="AC2",
            given="G2",
            when="W2",
            then="T2",
        )

        restored = AcceptanceCriterion.model_validate(original.model_dump(mode="json"))

        assert restored == original
        assert restored.title == "AC2"


class TestAcceptanceCriterionValidation:
    def test_missing_required_fields_raises_validation_error(self) -> None:
        """必填校验：缺少任一 Given/When/Then 应抛出 ValidationError"""
        fields = {
            "title": "Missing Info",
            "given": "Given something",
            "when": "When something",
            "then": "Then something",
        }

        # 逐个移除必填项
        for field in fields:
            test_data = fields.copy()
            del test_data[field]
            with pytest.raises(ValidationError):
                AcceptanceCriterion(**test_data)
