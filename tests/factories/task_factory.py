from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use
from typing import Any

from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.story_point import StoryPoint
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.value_score import ValueScore
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.enums import CompletionLogic, ScopeLevel, TaskStatus


class TaskIdFactory(ModelFactory[TaskId]):
    __model__ = TaskId

    @classmethod
    def build(cls, **kwargs: Any) -> TaskId:
        return TaskId.create()


class StoryPointFactory(ModelFactory[StoryPoint]):
    __model__ = StoryPoint

    @classmethod
    def build(cls, **kwargs: Any) -> StoryPoint:
        return StoryPoint.create(cls.__random__.choice([1, 2, 3, 5, 8, 13]))


class ValueScoreFactory(ModelFactory[ValueScore]):
    __model__ = ValueScore

    @classmethod
    def build(cls, **kwargs: Any) -> ValueScore:
        return ValueScore.create(cls.__random__.uniform(1.0, 10.0))


class TaskOutputFactory(ModelFactory[TaskOutput]):
    __model__ = TaskOutput

    summary = Use(lambda: "Test task output summary")
    artifacts = Use(lambda: ["file1.py", "file2.py"])
    error = None


class TaskFactory(ModelFactory[Task]):
    __model__ = Task

    id = Use(TaskIdFactory.build)
    project_id = Use(lambda: f"test-project-{TaskFactory.__random__.randint(1, 100)}")
    name = Use(lambda: f"Task {TaskFactory.__random__.word()}")
    description = Use(lambda: f"Description for task {TaskFactory.__random__.sentence()}")
    effort = Use(StoryPointFactory.build)
    base_value = Use(ValueScoreFactory.build)
    scope_level = Use(lambda: TaskFactory.__random__.choice(list(ScopeLevel)))
    completion_logic = CompletionLogic.ALL
    dependencies = set()
    status = TaskStatus.PENDING
    output = None
    parent_id = None

    @classmethod
    def build(cls, **kwargs: Any) -> Task:
        # First let polyfactory resolve all the Use fields
        model_data = super().build(**kwargs)
        # Use Task.create factory method instead of direct model instantiation
        task = Task.create(
            project_id=model_data.project_id,
            name=model_data.name,
            description=model_data.description,
            effort=model_data.effort,
            base_value=model_data.base_value,
            scope_level=model_data.scope_level,
            completion_logic=model_data.completion_logic,
            dependencies=model_data.dependencies,
            parent_id=model_data.parent_id,
        )
        # Copy over any additional fields that were set
        if model_data.status != TaskStatus.PENDING:
            task.status = model_data.status
        if model_data.output is not None:
            task.output = model_data.output
        return task
