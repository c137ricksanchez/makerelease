import json
import os

from src import constants


def get_api_key(key: str) -> str:
    with open(constants.keys) as f:
        keys = json.load(f)
    return keys[key] if key in keys else ""


def get_movies(path: str) -> list:
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
