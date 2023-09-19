import os
import sys
from datetime import datetime
from typing import Dict, List

import ffmpeg
from pymediainfo import MediaInfo

from src import constants
from src.api import imgbb, imgur, imgbly


def extract_screenshots(path: str, outputdir: str) -> List[str]:
    images: List[str] = []

    movie_ms = MediaInfo.parse(path).tracks[0].duration  # type: ignore

    with open(constants.screenshots, "r") as f:
        timecodes = f.read().splitlines()

        for time in timecodes:
            if not time:
                continue

            try:
                t = datetime.strptime(time, "%H:%M:%S")
            except ValueError:
                print(f"Il timestamp '{time}' non è nel formato valido HH:MM:SS")
                continue

            timecode_ms = (t.hour * 60 * 60 + t.minute * 60 + t.second) * 1000

            # check if timecode is shorter than film duration
            if timecode_ms > movie_ms:
                break

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
    args = {}
    if is_anamorphic(filename):
        args = {"vf": "scale=iw*sar:ih"}

    try:
        (
            ffmpeg.input(filename, ss=time)
            .output(os.path.join(outputdir, outputfile), vframes=1, **args)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        exit(-1)


def is_anamorphic(path: str) -> bool:
    data = MediaInfo.parse(path)
    if not isinstance(data, MediaInfo):
        exit(-1)

    return float(data.tracks[1].pixel_aspect_ratio) != 1


def upload_to_imgbb(path: str) -> Dict[str, str]:
    return imgbb.upload_image(path)


def upload_to_imgur(path: str) -> Dict[str, str]:
    return imgur.upload_image(path)


def upload_to_imgbly(path: str) -> Dict[str,str]: 
    return imgbly.imgbly_upload(path)