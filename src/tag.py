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

            if t.format == "MPEG Video":
                t.format = "MPEG2"
            elif t.format == "MPEG-4 Visual":
                t.format = "XviD"
            elif t.format == "AVC":
                t.format = "H264"
            elif t.format == "HEVC":
                t.format = "H265"
            elif t.format == "VP08":
                t.format = "VP8"
            elif t.format == "VP09":
                t.format = "VP9"

            if fake_height <= 576:
                tags["v"] += f"SD {t.format}"
            else:
                scan_type = "i" if t.scan_type == "Interlaced" else "p"
                tags["v"] += f"{fake_height}{scan_type} {t.format}"
        elif t.track_type == "Audio":
            lang = (
                t.other_language[3].upper()
                if t.other_language and len(t.other_language) >= 4
                else (t.language if t.language else "UND")
            )

            channels = get_channels(t.channel_layout) if t.channel_layout else f"{t.channel_s}.0"

            if t.format == "MPEG Audio" and t.format_profile == "Layer 3":
                t.format = "MP3"

            tags["a"].append((f"{lang}", f"{t.format.replace('-', '')} {channels}"))
        elif t.track_type == "Text":
            if len(t.other_language) > 3:
                tags["s"].append(f"{t.other_language[3].title()}")
            else:
                filtered_strings = filter(lambda x: len(x) == 3, t.other_language)
                tag_s = next(filtered_strings, None)
                tags["s"].append(tag_s)

    # Replace "ITA AC3 5.1 ENG AC3 5.1" with "ITA ENG AC3 5.1"
    channel_lang_map = {}
    for lang, channel in tags["a"]:
        if channel in channel_lang_map:
            channel_lang_map[channel].append(lang)
        else:
            channel_lang_map[channel] = [lang]

    # Forming the final list of strings
    tags["a"] = [" ".join([*langs, channel]) for channel, langs in channel_lang_map.items()]
    tags["a"] = list(dict.fromkeys(tags["a"]))
    tags["s"] = list(dict.fromkeys(tags["s"]))

    if len(tags["s"]) > 3:
        tags["s"] = "MultiSub"
    else:
        tags["s"] = "Sub " + " ".join(tags["s"]) if tags["s"] else ""

    tag = tags["v"] + " " + " ".join(tags["a"]) + " " + tags["s"]

    if crew:
        tag += f" [{crew}]"

    return f"{title} ({year}) {tag}"


# https://discord.com/channels/507666522756349963/519567517069344768/971753081115136021
def get_channels(channels: str) -> str:
    lfe = int("LFE" in channels)
    return f'{len(channels.split(" ")) - lfe}.{lfe}'
