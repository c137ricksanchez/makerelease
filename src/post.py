import os
from pathlib import Path
from string import Template

import pymediainfo

from src import constants, utils


def generate_text(
    metadata: dict,
    filesize: int,
    report: str,
    screenshots: dict,
    bitrate_img: str,
    magnet: str,
    outputdir: str,
) -> None:
    screenshots = "\n".join(["[img]" + img + "[/img]" for img in screenshots])

    values = {
        "IMDB_URL": metadata["imdb_url"],
        "TITLE": metadata["title"],
        "YEAR": metadata["year"],
        "SIZE": sizeof_fmt(filesize),
        "POSTER_URL": metadata["poster_url"],
        "ORIGINAL_TITLE": metadata["original_title"],
        "DIRECTOR": metadata["director"],
        "RUNTIME": metadata["runtime"],
        "COUNTRY": metadata["country"],
        "GENRE": metadata["genre"],
        "CAST": metadata["cast"],
        "PLOT": metadata["plot"],
        "TRAILER": metadata["trailer"],
        "SCREENSHOTS": screenshots,
        "BITRATE_GRAPH": bitrate_img,
        "REPORT": report,
        "MAGNET": magnet,
    }

    template_text = utils.read_file(constants.template)
    template = Template(template_text).substitute(**values)

    with open(os.path.join(outputdir, "post.txt"), "wb") as t:
        t.write(str.encode(template))


def generate_report(path: str, outputdir: str) -> str:
    report = pymediainfo.MediaInfo.parse(path, full=False, output="Text")
    report = report.replace(path, Path(path).name)

    with open(os.path.join(outputdir, "report.txt"), "wb") as file:
        file.write(str.encode(report))

    return report


# https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"
