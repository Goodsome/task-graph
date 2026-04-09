from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use
from uuid import uuid4

from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.scope_context import ScopeContext
from task_graph.planning.domain.enums import CompletionLogic, ScopeLevel, TaskStatus, ArchitectureLayer


# ==========================================
# Value Object Factories
# ==========================================
class TaskIdFactory(ModelFactory[TaskId]):
    __model__ = TaskId

    @classmethod
    def value(cls) -> str:
        return str(uuid4())


class StoryPointFactory(ModelFactory[StoryPoint]):
    __model__ = StoryPoint

    @classmethod
    def value(cls) -> int:
        return cls.__random__.choice([1, 2, 3, 5, 8, 13, 21, 34, 55, 89])


class ValueScoreFactory(ModelFactory[ValueScore]):
    __model__ = ValueScore

    @classmethod
    def value(cls) -> float:
        return cls.__random__.uniform(1.0, 10.0)


class ScopeContextFactory(ModelFactory[ScopeContext]):
    __model__ = ScopeContext

    @classmethod
    def bounded_context(cls) -> str:
        return cls.__random__.choice(["planning", "user_management", "billing", "notification"])

    @classmethod
    def architecture_layer(cls) -> ArchitectureLayer:
        return cls.__random__.choice(list(ArchitectureLayer))


class TaskOutputFactory(ModelFactory[TaskOutput]):
    __model__ = TaskOutput

    summary = Use(lambda: "Test task output summary")
    artifacts = Use(lambda: ["file1.py", "file2.py"])
    error = None


# ==========================================
# Aggregate Root Factory
# ==========================================
class TaskFactory(ModelFactory[Task]):
    __model__ = Task

    # 定制化生成逻辑
    project_id = Use(lambda: f"test-project-{TaskFactory.__random__.randint(1, 100)}")
    name = Use(lambda: f"Task {TaskFactory.__random__.word()}")
    description = Use(lambda: f"Description for task {TaskFactory.__random__.sentence()}")
    scope_level = Use(lambda: TaskFactory.__random__.choice(list(ScopeLevel)))

    # 显式指定值对象生成器，确保符合业务规则
    effort = Use(StoryPointFactory.build)
    base_value = Use(ValueScoreFactory.build)

    # 合理的默认业务状态
    status = TaskStatus.PENDING
    completion_logic = CompletionLogic.ALL
    dependencies = set()
    parent_id = None
    output = None
    review_feedback = None
    recurrence = None
    scope_context = None
