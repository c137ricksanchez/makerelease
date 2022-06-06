from pymediainfo import MediaInfo
import argparse
from os import rename
from os.path import dirname, join, splitext, basename

# Instantiate the parser
parser = argparse.ArgumentParser(description='')

parser.add_argument('-p', '--path',
                    type=str,
                    help='Required path of the file to be analyzed',
                    required=True)

# Switch
parser.add_argument('-m', '--mircrew',
                    default=False,
                    action='store_true',
                    help='If passed, in the title it will be specified MIRCrew')

# Switch
parser.add_argument('-r', '--rename',
                    default=False,
                    action='store_true',
                    help='If passed, it also renames the original file')

# Switch
parser.add_argument('-nov', '--noverbose',
                    default=False,
                    action='store_true',
                    help='If passed, no output will be given')

args = parser.parse_args()


media_info = MediaInfo.parse(args.path)
# https://mircrew-releases.org/viewtopic.php?t=18626
# debug media_info.tracks[1].to_data()

tags = {
    'v': '',  # video
    'a': '',  # audio
    's': '',  # subtitles
}

for t in media_info.tracks:

    if t.track_type == "Video":

        # may not be the height, but the correspondent 16:9 version
        fake_height = int(t.width/(16/9))

        # it may be a bit off so round it with 10 pixel tolerance
        resolutions = [576, 720, 1080, 2160]
        for res in resolutions:
            if abs(res-fake_height) < 10:
                fake_height = res

        if fake_height <= 576:
            tags['v'] += "SD"
        else:
            scanType = 'p' if t.scan_type == 'Progressive' else 'i'
            tags['v'] += f"{t.codec_id} {t.encoded_library_name} {fake_height}{scanType}"

    elif t.track_type == "Audio":
        tags['a'] += f" {t.other_language[3].upper()} {t.codec_id}"

    elif t.track_type == "Text":
        tags['s'] += f" {t.other_language[3].title()}"

if tags['s'] != '':
    tags['s'] = ' Sub'+tags['s']

TAG = tags['v'] + tags['a'] + tags['s']

parent = dirname(args.path)
filename, file_extension = splitext(basename(args.path))

TITLE = f"{filename} [{TAG}]"

if args.mircrew:
    TITLE += ' MIRCrew'

# make sure no '/' in title
TITLE = TITLE.replace('/', '-')

if not args.noverbose:
    print(TITLE)

if args.rename:
    rename(args.path,
           join(parent, TITLE)+file_extension)


def yes_no_input(choice, default=False):
    # usage mychoide = yes_no_input(input("BlaBlaBla"))
    # raw_input returns the empty string for "enter"
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = choice.lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        print(f'No valid choice, we assume {default}')
        return default
