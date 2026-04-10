import logging
from task_graph.bootstrap import create_container

from task_graph.planning.config import PROJECT_ROOT

LOG_FILE_PATH = PROJECT_ROOT / "logs/main.log"

logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logging.info("Starting MCP Server")



def main():
    container = create_container()
    


if __name__ == "__main__":
    main()