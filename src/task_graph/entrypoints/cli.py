import sys

import typer
from task_graph.bootstrap import create_container, setup_cli_logging
from task_graph.planning.interfaces.cli.app import planning_app


def create_app() -> typer.Typer:
    """初始化并配置 CLI 应用实例"""
    _ = create_container()
    app = typer.Typer(
        name="TaskGraph",
        invoke_without_command=True,
    )

    @app.callback()
    def default_callback(ctx: typer.Context) -> None:
        """当没有子命令时，默认启动交互式终端界面。"""
        if ctx.invoked_subcommand is None:
            from task_graph.planning.interfaces.tui.app import run_tui
            run_tui()

    app.add_typer(planning_app)
    return app

def main():
    logger = setup_cli_logging()
    try:
        app = create_app()
        app()
    except Exception as e:
        logger.error(f"CLI application failed: {str(e)}", exc_info=True)
        raise
    finally:
        pass

if __name__ == "__main__":
    main()