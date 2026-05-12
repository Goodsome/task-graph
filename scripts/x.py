from task_graph.bootstrap.setup import create_container
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.infrastructure.adapters.sql_alchemy_task_query_service import SqlAlchemyTaskQueryService
from task_graph.shared.infrastructure.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork

def main():
    container = create_container()

    qs: SqlAlchemyTaskQueryService = container.planning.task_query_service()
    uow: SqlAlchemyUnitOfWork[TaskRepository] = container.planning.unit_of_work()

    task_id = TaskId.reconstitute(value="3616f533-6746-4e97-b49a-ed27c838afe4")

    data = qs.find_dependents(task_id=task_id)
    print(data)

    with uow:
        tid = "1fe0399a-aff4-4504-be6d-5fb01f7dfa5e"
        task_id = TaskId.reconstitute(tid)
        task = uow.repository.get(task_id)
        print(task.dependencies)


if __name__ == "__main__":
    main()