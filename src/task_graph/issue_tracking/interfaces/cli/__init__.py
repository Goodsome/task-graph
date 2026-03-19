import typer
from task_graph.issue_tracking.interfaces.cli.issue_create import issue_create
from task_graph.issue_tracking.interfaces.cli.issue_list import issue_list
from task_graph.issue_tracking.interfaces.cli.issue_show import issue_show
from task_graph.issue_tracking.interfaces.cli.issue_status import issue_status
from task_graph.issue_tracking.interfaces.cli.issue_metadata import issue_metadata
from task_graph.issue_tracking.interfaces.cli.issue_comment import issue_comment
from task_graph.issue_tracking.interfaces.cli.issue_close import issue_close
from task_graph.issue_tracking.interfaces.cli.issue_link import issue_link
from task_graph.issue_tracking.interfaces.cli.issue_unlink import issue_unlink

app = typer.Typer(help="IssueTracking CLI")
app.command("issue_create")(issue_create)
app.command("issue_list")(issue_list)
app.command("issue_show")(issue_show)
app.command("issue_status")(issue_status)
app.command("issue_metadata")(issue_metadata)
app.command("issue_comment")(issue_comment)
app.command("issue_close")(issue_close)
app.command("issue_link")(issue_link)
app.command("issue_unlink")(issue_unlink)