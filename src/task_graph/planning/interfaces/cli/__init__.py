import typer
from task_graph.planning.interfaces.cli.create_task import create_task
from task_graph.planning.interfaces.cli.list_tasks import list_tasks
from task_graph.planning.interfaces.cli.get_task import get_task
from task_graph.planning.interfaces.cli.suggest_next import suggest_next
from task_graph.planning.interfaces.cli.claim_task import claim_task
from task_graph.planning.interfaces.cli.submit_result import submit_result
from task_graph.planning.interfaces.cli.review_task import review_task
from task_graph.planning.interfaces.cli.modify_deps import modify_deps
from task_graph.planning.interfaces.cli.revise_task import revise_task
from task_graph.planning.interfaces.cli.delete_task import delete_task

app = typer.Typer(help="Planning CLI")
app.command("create_task")(create_task)
app.command("list_tasks")(list_tasks)
app.command("get_task")(get_task)
app.command("suggest_next")(suggest_next)
app.command("claim_task")(claim_task)
app.command("submit_result")(submit_result)
app.command("review_task")(review_task)
app.command("modify_deps")(modify_deps)
app.command("revise_task")(revise_task)
app.command("delete_task")(delete_task)
