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

            tags["a"].append((f"{lang.upper()}", f"{t.format.replace('-', '')} {channels}"))
        elif t.track_type == "Text":
            # Enhanced subtitle handling, including NU (non-hearing) subtitles
            subtitle_lang = None
            
            # Try t.other_language first
            if t.other_language and len(t.other_language) > 3:
                subtitle_lang = t.other_language[3].upper()
            elif t.other_language:
                # Look for 3-character language codes in other_language
                filtered_strings = filter(lambda x: len(x) == 3, t.other_language)
                tag_s = next(filtered_strings, None)
                if tag_s:
                    subtitle_lang = tag_s.upper()
            
            # If other_language doesn't work, use t.language directly
            if not subtitle_lang and t.language:
                # Handle codes like "nu-eng", "nu-ita", "nu-fra", etc.
                lang_code = t.language.upper()
                if lang_code.startswith('NU'):
                    # Extract the part after NU- (e.g., "NU-ENG" -> "ENG")
                    if '-' in lang_code:
                        subtitle_lang = lang_code.split('-')[1]
                    else:
                        # Case "NUENG", "NUITA", "NUFRA" without hyphen
                        if len(lang_code) > 2:
                            subtitle_lang = lang_code[2:]
                else:
                    # Normal language code (ITA, ENG, FRA, etc.)
                    subtitle_lang = lang_code
            
            # If still no language found, use t.language directly  
            if not subtitle_lang and t.language:
                # ISO 639-2/T language code mapping (most common languages)
                language_map = {
                    "italian": "ITA", "english": "ENG", "french": "FRA", "spanish": "SPA",
                    "german": "GER", "portuguese": "POR", "russian": "RUS", "chinese": "CHI",
                    "japanese": "JPN", "korean": "KOR", "arabic": "ARA", "dutch": "DUT",
                    "swedish": "SWE", "norwegian": "NOR", "danish": "DAN", "finnish": "FIN",
                    "polish": "POL", "czech": "CZE", "hungarian": "HUN", "turkish": "TUR",
                    "greek": "GRE", "hebrew": "HEB", "thai": "THA", "hindi": "HIN"
                }
                
                lang_lower = t.language.lower()
                if lang_lower in language_map:
                    subtitle_lang = language_map[lang_lower]
                elif len(t.language) <= 3:
                    # Already a short code
                    subtitle_lang = t.language.upper()
                # If language not in map and not a short code, skip it
            
            # Check if this is a non-hearing subtitle (SDH, CC, etc.)
            # Note: "Forced" subtitles are NOT for non-hearing, they're for foreign language dialogue
            is_non_hearing = False
            if hasattr(t, 'title') and t.title:
                title_upper = t.title.upper()
                if any(keyword in title_upper for keyword in ['SDH', 'CC']):
                    is_non_hearing = True
            
            # Add language code with NU prefix if it's a non-hearing subtitle
            if subtitle_lang:
                if is_non_hearing:
                    tags["s"].append(f"NU{subtitle_lang}")
                else:
                    tags["s"].append(subtitle_lang)

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

    final_name = f"{title} ({year}) {tag}"
    
    # Remove quotes around language codes (ITA, ENG, etc.)
    import re
    final_name = re.sub(r"'([A-Z]{2,3})'", r'\1', final_name)
    
    return final_name


# https://discord.com/channels/507666522756349963/519567517069344768/971753081115136021
def get_channels(channels: str) -> str:
    lfe = int("LFE" in channels)
    return f'{len(channels.split(" ")) - lfe}.{lfe}'
