import os
import sys

import ffmpeg

from src import constants
from src.api import imgur


def extract_screenshots(path: str, outputdir: str) -> dict:
    images = []

    with open(constants.screenshots, "r") as f:
        timecodes = f.read().splitlines()

        for time in timecodes:
            name = time.replace(":", ".") + ".png"
            generate_thumbnail(path, outputdir, name, time)
            images.append(os.path.join(outputdir, name))

    return images


def generate_thumbnail(
    filename: str,
    outputdir: str,
    outputfile: str,
    time: str,
) -> None:
    try:
        (
            ffmpeg.input(filename, ss=time)
            .output(os.path.join(outputdir, outputfile), vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)


def upload_to_imgur(path: str) -> str:
    return imgur.upload_image(path)
