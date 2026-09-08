import json
from pathlib import Path


def parse_json(file_path: Path) -> str:
    """
    Load JSON and convert it into readable text.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )