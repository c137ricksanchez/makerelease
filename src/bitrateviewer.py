import json
import math
import os
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import Literal, TypedDict

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.ndimage import gaussian_filter1d


class FrameEntry(TypedDict):
    n: int
    frame_type: Literal["I", "Non-I"]
    pts: float | Literal["NaN"]
    size: int
    duration: float | Literal["NaN"]


# https://github.com/slhck/ffmpeg-bitrate-stats
class BitrateViewer:
    _path: str
    _filename: str

    def __init__(self, path: str):
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found. {path}")

        self._path = path
        self._filename = Path(path).stem

        self._chunk_size = 1
        self._frames: list[FrameEntry] = []
        self._chunks: list[float] = []

    def analyze(self):
        proc = subprocess.Popen(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-fflags",
                "+genpts",
                "-select_streams",
                "v:0",
                "-show_packets",
                "-show_entries",
                "packet=pts_time,dts_time,duration_time,size,flags",
                "-of",
                "json",
                self._path,
            ],
            stdout=subprocess.PIPE,
        )

        stdout, _ = proc.communicate()
        data = stdout.decode("utf-8")

        info = json.loads(data)["packets"]

        ret: list[FrameEntry] = []
        idx = 1

        default_duration = next((x["duration_time"] for x in info if "duration_time" in x.keys()), "NaN")

        for packet_info in info:
            frame_type: Literal["I", "Non-I"] = (
                # key frames are marked with a capital K (K_ or K__) in packet flags
                "I" if "K" in packet_info["flags"] else "Non-I"
            )

            pts: float | Literal["NaN"] = float(packet_info["pts_time"]) if "pts_time" in packet_info.keys() else "NaN"

            duration: float | Literal["NaN"] = (
                float(packet_info["duration_time"])
                if "duration_time" in packet_info.keys()
                else float(default_duration)
                if default_duration != "NaN"
                else "NaN"
            )

            ret.append(
                {
                    "n": idx,
                    "frame_type": frame_type,
                    "pts": pts,
                    "size": int(packet_info["size"]),
                    "duration": duration,
                }
            )
            idx += 1

        # fix for missing durations, estimate it via PTS
        if default_duration == "NaN":
            ret = self._fix_durations(ret)

        # fix missing data in first packet (occurs occassionally when reading streams)
        if ret[0]["duration"] == "NaN" and isinstance(ret[1]["duration"], float):
            ret[0]["duration"] = ret[1]["duration"]

        if ret[0]["pts"] == "NaN" and isinstance(ret[1]["pts"], float) and isinstance(ret[0]["duration"], float):
            ret[0]["pts"] = ret[1]["pts"] - ret[0]["duration"]

        self._frames = ret

    def _fix_durations(self, ret: list[FrameEntry]) -> list[FrameEntry]:
        last_duration = None
        for i in range(len(ret) - 1):
            curr_pts = ret[i]["pts"]
            next_pts = ret[i + 1]["pts"]
            if curr_pts == "NaN" or next_pts == "NaN":
                continue
            last_duration = next_pts - curr_pts
            ret[i]["duration"] = last_duration
        if last_duration is not None:
            ret[-1]["duration"] = last_duration
        return ret

    def _collect_chunks(self) -> list[float]:
        # this is where we will store the stats in buckets
        aggregation_chunks: list[list[FrameEntry]] = []
        curr_list: list[FrameEntry] = []

        agg_time: float = 0
        for frame in self._frames:
            if agg_time < self._chunk_size:
                curr_list.append(frame)
                agg_time += float(frame["duration"])
            else:
                if curr_list:
                    aggregation_chunks.append(curr_list)
                curr_list = [frame]
                agg_time = float(frame["duration"])
        aggregation_chunks.append(curr_list)

        # calculate BR per group
        self._chunks = [BitrateViewer._bitrate_for_frame_list(x) for x in aggregation_chunks]

        return self._chunks

    @staticmethod
    def _bitrate_for_frame_list(frame_list: list[FrameEntry]) -> float:
        if len(frame_list) < 2:
            return math.nan

        # sort frames by PTS in case they are unordered
        frame_list.sort(key=lambda x: x["pts"])

        duration = float(frame_list[-1]["pts"]) - float(frame_list[0]["pts"])
        size = sum(f["size"] for f in frame_list)
        bitrate = ((size * 8) / 1000) / duration

        return bitrate

    def plot(self, outputdir: str):
        chunks = self._collect_chunks()
        x_values = [i * self._chunk_size for i in range(len(chunks))]

        fig, ax = plt.subplots(figsize=[16, 9])
        ax.set_title(self._filename)

        ax.plot(x_values, chunks, label="Bitrate", color="#9e9e9e")

        ax.plot(
            x_values,
            gaussian_filter1d(input=chunks, sigma=64),
            label="Bitrate (smoothed)",
            color="#f44336",
            lw=2,
        )

        ax.legend(loc="upper right")

        ax.grid(axis="y", c="#e0e0e0")
        ax.set_axisbelow(True)

        ax.margins(x=0.02)
        ax.set_ylim(0)

        ax.set_xlabel("Time")
        # mette 10 ticks sull'asse x
        ax.set_xticks(range(0, x_values[-1] + 1, max(x_values[-1] // 9, 1)))
        # converte i secondi nel human-readable 0:01:44
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: timedelta(seconds=int(x))))

        ax.set_ylabel("Bitrate (Kbps)")
        # mettere il separatore delle migliaia
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "{:,}".format(int(x)).replace(",", ".")))

        output = os.path.join(outputdir, "bitrate.png")
        fig.savefig(output, bbox_inches="tight")
