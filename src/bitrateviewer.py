import io
import math
import multiprocessing
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import timedelta
from pathlib import Path

import ffmpeg
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from tqdm import tqdm


# https://github.com/InB4DevOps/bitrate-viewer
class BitrateViewer:
    def __init__(self, video_path: str):
        video_path = os.path.abspath(video_path)

        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"File not found. {video_path}")

        self.video_path = video_path
        self.dir = os.path.dirname(video_path)
        self.filename = Path(video_path).stem

    def analyze(self):
        duration = round(self.get_duration(), 2)
        fps = self.get_framerate_float()
        self.fps_rounded = round(fps)

        total_frames = math.trunc(duration * fps) + 1

        cpu_count = multiprocessing.cpu_count()

        with open(
            os.path.join(self.dir, self.filename + ".xml"), "w", encoding="utf-8"
        ) as f:
            print(f"Now analyzing ~{total_frames} frames...")

            with tqdm(total_frames, unit=" frames", ncols=80) as progress:
                proc = subprocess.Popen(
                    [
                        "ffprobe",
                        "-hide_banner",
                        "-show_frames",
                        "-show_streams",
                        "-threads",
                        str(cpu_count),
                        "-loglevel",
                        "quiet",
                        "-show_entries",
                        "frame=key_frame,pkt_size",
                        "-print_format",
                        "xml",
                        "-select_streams",
                        "v:0",
                        self.video_path,
                    ],
                    stdout=subprocess.PIPE,
                )

                for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                    f.write(line)

                    if "pkt_size" in line:
                        progress.update()

                proc.poll()

        self.analyzed_file = os.path.join(self.dir, self.filename + ".xml")

    def get_duration(self) -> float:
        duration = ffmpeg.probe(self.video_path)["format"]["duration"]
        return float(duration)

    def get_framerate_float(self) -> float:
        numerator, denominator = self.get_framerate_fraction().split("/")
        return round((int(numerator) / int(denominator)), 3)

    def get_framerate_fraction(self) -> str:
        return [
            stream
            for stream in ffmpeg.probe(self.video_path)["streams"]
            if stream["codec_type"] == "video"
        ][0]["r_frame_rate"]

    def parse(self):
        bitrates = []
        keyframes = []
        encoder = str()

        bitrates, keyframes, encoder = self.load_xml()
        seconds, bitrates_per_sec = self.calculate_bitrate_per_sec(bitrates)

        return tuple([seconds, bitrates_per_sec, keyframes, encoder])

    def calculate_bitrate_per_sec(self, bitrates):
        seconds = []
        bitrates_per_sec = []
        current_second = 0
        current_bitrate = 0
        frame_count = 0

        for bitrate in bitrates:
            current_bitrate += bitrate
            frame_count += 1

            if frame_count == self.fps_rounded:
                seconds.append(current_second)
                bitrates_per_sec.append(current_bitrate / 1_000)  # kilobit
                current_bitrate = 0
                frame_count = 0
                current_second += 1

        return seconds, bitrates_per_sec

    def read_key_frame_time(self, frame) -> float:
        frame_time = frame.get("pkt_pts_time")
        if not frame_time:
            frame_time = frame.get("pkt_dts_time")

        return float(frame_time) if frame_time else None

    def load_xml(self):
        bitrates = []
        keyframes = []
        root = ET.parse(self.analyzed_file).getroot()

        for frame in root.findall("frames/frame"):
            value = int(frame.get("pkt_size"))
            bitrates.append(value * 8)  # pkt_size is in byte

            if int(frame.get("key_frame")) == 1:
                keyframe_time = self.read_key_frame_time(frame)
                if keyframe_time:
                    keyframes.append(keyframe_time)

        streams = root.findall("streams/stream")
        encoder = streams[0].get("codec_name")
        return bitrates, keyframes, encoder

    def plot(self, results, outputdir):
        seconds, bitrates, keyframes, encoder = results

        avg_bitrate = self.get_mbit_str(round(np.mean(bitrates) / 1_000, 2))
        max_bitrate = self.get_mbit_str(round(max(bitrates) / 1_000, 2))

        # set seaborn style
        plt.style.use("seaborn-dark")

        # init the plot
        fig, ax = plt.subplots(figsize=[16, 9])
        ax.set_title(self.filename)
        ax.set_xlabel("Time")
        ax.set_ylabel("Bitrate (Kbps)")

        ax.grid(True)

        # actually plot the data
        ax.fill_between(seconds, bitrates, color="#4c72b0")

        ax.axhline(
            np.mean(bitrates),
            lw=2,
            color="#c44e52",
            label=f"Average bitrate = {avg_bitrate}",
        )

        ax.axhline(
            max(bitrates),
            color="#1a1a1a",
            label=f"Peak bitrate = {max_bitrate}",
        )

        # setup plot legend
        ax.legend(loc="upper right", facecolor="#fff", frameon=True, framealpha=1)

        ax.margins(x=0.01)
        ax.set_ylim(0)

        ax.set_xticks(range(0, seconds[-1] + 1, max(seconds[-1] // 10, 1)))

        # format axes values
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, loc: timedelta(seconds=int(x)))
        )
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, loc: "{:,}".format(int(x)))
        )

        output = os.path.join(outputdir, "bitrate.png")

        # save the plot
        fig.savefig(output, bbox_inches="tight")

    def get_mbit_str(self, megabits):
        return f"{megabits} Mbps"
