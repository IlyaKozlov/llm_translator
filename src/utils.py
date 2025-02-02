import logging
from pathlib import Path

resources_path = Path(__file__).parent / "resources"
assert resources_path.is_dir()


def help_message() -> str:
    path = resources_path / "help_message.txt"
    with open(path, "r") as f:
        message = f.read()
    return message


def init_logger() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)
