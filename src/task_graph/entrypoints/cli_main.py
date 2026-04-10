import typer
from task_graph.bootstrap import create_container
from task_graph.planning.interfaces.cli.create_task import create_task
from task_graph.planning.interfaces.cli.list_tasks import list_tasks
from task_graph.planning.interfaces.cli.get_task import get_task
from task_graph.planning.interfaces.cli.delete_task import delete_task

_ = create_container()

app = typer.Typer(name="TaskGraph")
app.command("create_task")(create_task)
app.command("list_tasks")(list_tasks)
app.command("get_task")(get_task)
app.command("delete_task")(delete_task)

if __name__ == "__main__":
    app()