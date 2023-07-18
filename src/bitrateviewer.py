import io
import math
import multiprocessing
import os
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import List

import ffmpeg
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.ndimage import gaussian_filter1d
from tqdm import tqdm


# https://github.com/InB4DevOps/bitrate-viewer
class BitrateViewer:
    _path: str
    _filename: str

    _seconds: List[int] = []
    _bitrates_per_sec: List[float] = []
    _avg_bitrate: List[float] = []

    def __init__(self, path: str):
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found. {path}")

        self._path = path
        self._filename = Path(path).stem

    def analyze(self):
        duration = self.get_duration()
        fps = self.get_framerate()
        self._fps_rounded = round(fps)

        total_frames = math.trunc(duration * fps) + 1

        cpu_count = multiprocessing.cpu_count()

        bitrates: List[int] = []

        with tqdm(range(total_frames), unit=" frames", ncols=80) as progress:
            proc = subprocess.Popen(
                [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-threads",
                    str(cpu_count),
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "frame=pkt_size",
                    "-print_format",
                    "csv",
                    self._path,
                ],
                stdout=subprocess.PIPE,
            )

            if proc.stdout:
                for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                    if line.strip() and "," in line:
                        frame = line.split(",")[1]
                        if frame.rstrip().isdigit():
                            bitrates.append(int(frame) * 8)  # pkt_size is in byte
                            progress.update()

            proc.poll()

        self.calculate_bitrates_per_sec(bitrates)

    def get_duration(self) -> float:
        duration: float = ffmpeg.probe(self._path)["format"]["duration"]
        return float(duration)

    def get_framerate(self) -> float:
        r_frame_rate: str = [
            stream
            for stream in ffmpeg.probe(self._path)["streams"]
            if stream["codec_type"] == "video"
        ][0]["r_frame_rate"]

        numerator, denominator = r_frame_rate.split("/")
        return round(int(numerator) / int(denominator), 3)

    def calculate_bitrates_per_sec(self, bitrates: List[int]):
        current_second = 0
        current_bitrate = 0
        frame_count = 0

        for bitrate in bitrates:
            current_bitrate += bitrate
            frame_count += 1

            if frame_count == self._fps_rounded:
                self._seconds.append(current_second)
                self._bitrates_per_sec.append(current_bitrate / 1_000)  # kilobit
                # self._avg_bitrate.append(float(np.mean(self._bitrates_per_sec)))

                current_bitrate = 0
                frame_count = 0
                current_second += 1

    def plot(self, outputdir: str):
        fig, ax = plt.subplots(figsize=[16, 9])
        ax.set_title(self._filename)

        ax.plot(self._seconds, self._bitrates_per_sec, label="Bitrate", color="#9e9e9e")

        ax.plot(
            self._seconds,
            gaussian_filter1d(input=self._bitrates_per_sec, sigma=64),
            label="Bitrate (smoothed)",
            color="red",
            lw=2,
        )

        ax.legend(loc="upper right")

        ax.grid(axis="y", c="#e0e0e0")
        ax.set_axisbelow(True)

        ax.margins(x=0.02)
        ax.set_ylim(0)

        ax.set_xlabel("Time")
        # mette 10 ticks sull'asse x
        ax.set_xticks(range(0, self._seconds[-1] + 1, max(self._seconds[-1] // 9, 1)))
        # converte i secondi nel human-readable 0:01:44
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: timedelta(seconds=int(x)))
        )

        ax.set_ylabel("Bitrate (Kbps)")
        # mettere il separatore delle migliaia
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: "{:,}".format(int(x)).replace(",", "."))
        )

        output = os.path.join(outputdir, "bitrate.png")
        fig.savefig(output, bbox_inches="tight")
