from pymediainfo import MediaInfo


def parse(filename: str, title: str, year: str, crew: str) -> str:
    data = MediaInfo.parse(filename)
    if not isinstance(data, MediaInfo):
        exit(-1)

    tags = {
        "v": "",  # video
        "a": [],  # audio
        "s": [],  # subtitles
    }

    for t in data.tracks:
        if t.track_type == "Video":
            # may not be the height, but the correspondent 16:9 version
            fake_height = int(t.width / (16 / 9))

            # it may be a bit off so round it with 10 pixel tolerance
            resolutions = [576, 720, 1080, 2160]
            for res in resolutions:
                if abs(res - fake_height) < 10:
                    fake_height = res

            if fake_height <= 576:
                if "MP4V-ES" in t.internet_media_type:
                    t.internet_media_type = "XviD"

                tags["v"] += f"SD {t.internet_media_type.replace('video/', '')}"
            else:
                scan_type = "i" if t.scan_type == "Interlaced" else "p"
                tags[
                    "v"
                ] += f"{fake_height}{scan_type} {t.internet_media_type.replace('video/', '')}"
        elif t.track_type == "Audio":
            lang = (
                t.other_language[3].upper()
                if t.other_language and len(t.other_language) >= 4
                else (t.language if t.language else "UND")
            )

            channels = (
                get_channels(t.channel_layout)
                if t.channel_layout
                else f"{t.channel_s}.0"
            )

            if t.format == "MPEG Audio" and t.format_profile == "Layer 3":
                t.format = "MP3"

            tags["a"].append(f"{lang} {t.format.replace('-', '')} {channels}")
        elif t.track_type == "Text":
            tags["s"].append(f"{t.other_language[3].title()}")

    tags["a"] = list(dict.fromkeys(tags["a"]))
    tags["s"] = list(dict.fromkeys(tags["s"]))

    tags["s"] = "Sub " + " ".join(tags["s"]) if tags["s"] else ""

    tag = tags["v"] + " " + " ".join(tags["a"]) + " " + tags["s"]

    if crew:
        tag += f" [{crew}]"

    return f"{title} ({year}) {tag}"


# https://discord.com/channels/507666522756349963/519567517069344768/971753081115136021
def get_channels(channels: str) -> str:
    lfe = int("LFE" in channels)
    return f'{len(channels.split(" ")) - lfe}.{lfe}'
