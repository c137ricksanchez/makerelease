import json
import os
import re
from typing import List, Tuple

from src import constants


def get_api_key(key: str) -> str:
    with open(constants.keys) as f:
        keys = json.load(f)
    return keys[key] if key in keys else ""


def get_movies(path: str) -> List[str]:
    return [
        os.path.join(path, f)
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
        and f.lower().endswith(("avi", "mkv", "mp4"))
    ]


def read_file(file: str) -> str:
    if not os.path.exists(file):
        raise Exception(f"File {file} non trovato")

    with open(file) as f:
        return f.read()


def parse_title(filename: str) -> Tuple[str, str]:
    title = filename.replace(".", " ").split("(")[0].strip()
    title_year: List[str] = re.findall(r"\b\d{4}\b", filename)
    year = ""

    if len(title_year) == 1:
        year = title_year[0]
    elif len(title_year) == 2:
        year = title_year[1]
        title = title.split(year, 1)[0]

    return title, year
