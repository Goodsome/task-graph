import typer
from task_graph.bootstrap import create_container
from task_graph.planning.interfaces.cli.app import planning_app

_ = create_container()

app = typer.Typer(name="TaskGraph")

app.add_typer(planning_app)

if __name__ == "__main__":
    app()