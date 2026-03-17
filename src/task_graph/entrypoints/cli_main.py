import typer
from task_graph.planning.interfaces.cli import app as planning_app

app = typer.Typer(name="TaskGraph")
app.add_typer(planning_app, name="p")

if __name__ == "__main__":
    app()