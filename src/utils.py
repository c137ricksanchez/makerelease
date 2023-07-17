import json
import os
import re
from typing import List, Tuple

from pymediainfo import MediaInfo

from src import constants, post


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


def get_folders(path: str) -> List[str]:
    return [
        os.path.join(path, f)
        for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f))
    ]


def get_size(path: str) -> int:
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        total = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                total += os.path.getsize(fp)
        return total
    else:
        raise Exception(f"Path {path} non trovato")


def get_tree(path: str) -> str:
    # get all files and folders recursively
    # and output them in a tree structure
    tree = []
    for root, dirs, files in os.walk(path):
        level = root.replace(path, "").count(os.sep)
        indent = " " * 4 * level
        tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)

            size = get_size(file_path)
            pretty_size = post.sizeof_fmt(size)

            if f.lower().endswith(("avi", "mkv", "mp4")):
                duration = get_duration(file_path)
                runtime = post.parse_runtime(duration)

                file_info = f"{runtime}, {pretty_size}"
            else:
                file_info = pretty_size

            tree.append(f"{subindent}{f} ({file_info})")

    return "\n".join(tree)

def get_ep_count(path: str) -> int:
    ep_count = 0
    rel_files = os.listdir(path)
    for file in rel_files:
        if(file.endswith(("avi", "mkv", "mp4"))):
            ep_count += 1
    return ep_count


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


def get_duration(path: str) -> int:
    return MediaInfo.parse(path).tracks[0].duration // 60000  # type: ignore
