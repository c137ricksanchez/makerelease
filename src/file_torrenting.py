import urllib
import bencoding
import hashlib


def hash_to_magnet(HASH, NAME, trackers):
    #NAME = "Dieci piccoli indiani - And Then There Were None (1945) [1080p BluRay H264 ITA AC3 ENG AAC Sub Eng]"
    NAME = urllib.parse.quote(NAME)
    magnet = f'magnet:?xt=urn:btih:{HASH}&dn={NAME}'
    for tracker in trackers.split(','):
        magnet += '&tr=' + urllib.parse.quote(tracker, safe='')  # safe di default è '/'
    return magnet


def torrent_to_hash(FILENAME):
    with open(FILENAME, "rb") as f:
        data = bencoding.bdecode(f.read())
    info = data[b'info']
    hashed_info = hashlib.sha1(bencoding.bencode(info)).hexdigest()
    return hashed_info
