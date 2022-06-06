from os import listdir, getcwd, chdir
from os.path import isfile, join

import subprocess
import json
import urllib
import re
import pandas as pd

from src import file_torrenting
from src import file_analysis
from src import file_description

with open(join('data', 'APIkeys.json')) as f:
    keys = json.load(f)
    omdbapi = keys['OMDBapi']


with open(join('data', 'trackers.txt'), 'r') as f:
    trackers = f.read().replace('\n', ',')

# change to correct working directory
chdir('movies-tvshows')

# get correct list of files to analyze
mypath = getcwd()
movies = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.lower().endswith(('mkv', 'mp4'))]

# data = []

for movie_name in movies:

    # title = movie_name.split('-')[1].split('(')[0].strip() # il secondo titolo
    title = movie_name.split('(')[0].strip()
    # title = movie_name
    year = re.search('\(([0-9]{4})\)', movie_name).group(1)

    # begin file analysis
    print('Generating report...')
    report = file_analysis.get_report(movie_name)
    print('Extracting screenshots...')
    file_analysis.extract_screenshots(movie_name)

    # begin retrieving file information
    print('Obtaining metadata...')
    description = file_description.get_description_omdb(omdbapi, title, year, movie_name)

    FILENAME_WITHOUT_EXTENSION = movie_name.split('.')[-2]
    FILENAME_WITHOUT_DETAILS = movie_name.split('[')[0].strip()

    print('Generating .torrent file...')
    output_torrent_name = FILENAME_WITHOUT_EXTENSION+'.torrent'
    subprocess.run(['mktorrent', '-a', trackers, movie_name, '-o', output_torrent_name])

    HASH = file_torrenting.torrent_to_hash(output_torrent_name)

    MAGNET = file_torrenting.hash_to_magnet(HASH, FILENAME_WITHOUT_EXTENSION, trackers)

    plot_search = 'http://google.com/search?' + urllib.parse.urlencode({'q': FILENAME_WITHOUT_DETAILS+' sinossi'})

    text_forum = f"""
[url=https://postimages.org/][img]https://i.postimg.cc/d18LXq68/RS.jpg[/img][/url]

[size=200][b]{FILENAME_WITHOUT_DETAILS}[/b][/size]

>>>>>> IMMAGINE <<<<<<

[b]INFORMAZIONI[/b]

{description}

[b]TRAMA[/b]

{plot_search}

[b]SCREENSHOTS[/b]

[spoiler]
>>>>>> SCREENSHOTS <<<<<<
[/spoiler]

[b]BITRATE[/b]

[spoiler]
>>>>>> BITRATE <<<<<<
[/spoiler]

[b]REPORT[/b]

[spoiler][code]
{report}
[/code][/spoiler]

[magnet]
{MAGNET}
[/magnet]
"""

    # data.append([movie_name, text_forum])
    print('Generating bitrate graph...')
    subprocess.check_call(['python', '../_bitrate-viewer/main.py', '-i', movie_name])

    with open(f'{movie_name}_TEXT.txt', 'a') as the_file:
        the_file.write(text_forum)

# remove all .XML
subprocess.check_call(['rm', '-f', '*.xml'])

# df = pd.DataFrame(data, columns=['name', 'text_forum'])
# chdir('..')
# df.to_csv('__OUTPUT.csv', index=False)
