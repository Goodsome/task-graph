import typer
from task_graph.bootstrap import create_container, setup_cli_logging
from task_graph.planning.interfaces.cli.app import planning_app


def create_app() -> typer.Typer:
    """初始化并配置 CLI 应用实例"""
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
    container = None
    try:
        container = create_container()
        app = create_app()
        app()
    except SystemExit:
        # Normal exit from --help or other Click/Typer signals
        pass
    except Exception as e:
        logger.error(f"CLI application failed: {str(e)}", exc_info=True)
        raise
    finally:
        if container:
            logger.info("Shutting down container...")
            container.shutdown_resources()

if __name__ == "__main__":
    main()