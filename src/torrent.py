import os

from torf import Torrent

from src import constants, utils


def generate(filename: str, outputdir: str, outputfile: str) -> str:
    trackers = utils.read_file(constants.trackers).splitlines()

    filesize = os.path.getsize(filename)
    piece_size = calculate_piece_size(filesize)

    t = Torrent(path=filename, trackers=trackers, piece_size=piece_size)
    t.generate()
    t.write(os.path.join(outputdir, outputfile + ".torrent"))

    return t.magnet()


# https://cdn.discordapp.com/attachments/667734286543093760/915388777160142930/Torrent_Dimension.PNG
def calculate_piece_size(filesize: int) -> int:
    if filesize <= 50 * 1024 * 1024:
        # 0 - 50MB = 32KB
        piece = 32 * 1024
    elif filesize <= 150 * 1024 * 1024:
        # 50 - 150MB = 64KB
        piece = 64 * 1024
    elif filesize <= 350 * 1024 * 1024:
        # 150 - 350MB = 128KB
        piece = 128 * 1024
    elif filesize <= 512 * 1024 * 1024:
        # 350 - 512MB = 256KB
        piece = 256 * 1024
    elif filesize <= 1024 * 1024 * 1024:
        # 512MB - 1GB = 512KB
        piece = 512 * 1024
    elif filesize <= 2048 * 1024 * 1024:
        # 1 - 2GB = 1MB
        piece = 1024 * 1024
    elif filesize <= 4096 * 1024 * 1024:
        # 2 - 4GB = 2MB
        piece = 2048 * 1024
    elif filesize <= 8192 * 1024 * 1024:
        # 4 - 8GB = 4MB
        piece = 4096 * 1024
    elif filesize <= 16384 * 1024 * 1024:
        # 8 - 16GB = 8MB
        piece = 8192 * 1024
    else:
        # 16GB+ = 16MB
        piece = 16384 * 1024

    return piece
