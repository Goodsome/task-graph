# task_graph/planning/interfaces/cli/app.py
import typer

# 创建 planning 领域的专属子应用
planning_app = typer.Typer(
    name="planning", 
    help="任务计划相关命令"
)