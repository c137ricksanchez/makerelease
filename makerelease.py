import argparse
import os
import re
from pathlib import Path

import src.bitrateviewer as bv
from src import constants, images, metadata, post, tag, torrent, utils

# Instantiate the parser
parser = argparse.ArgumentParser()

parser.add_argument(
    "-c",
    "--crew",
    type=str,
    help="Release crew",
)

parser.add_argument(
    "-r",
    "--rename",
    default=False,
    action="store_true",
    help="Rinomina il file",
)

args = parser.parse_args()

for movie in utils.get_movies(constants.movies):
    file = Path(movie).name
    filename = Path(movie).stem
    ext = Path(movie).suffix

    print("File:", file)

    title, year = utils.parse_title(filename)

    filesize = os.path.getsize(movie)

    print("\n1. Ricezione dei metadati da TheMovieDB...")
    movie_id = metadata.search(title, year)
    data = metadata.get(movie_id)

    outputdir = os.path.join(constants.movies, data["title"] + "_files")
    if os.path.exists(outputdir):
        print("ERRORE: Esiste già una cartella chiamata", outputdir)
        continue
    else:
        os.mkdir(outputdir)

    title = tag.parse(movie, data["title"], data["year"], args.crew)

    if args.rename:
        old_movie = movie

        filename = re.sub(r'[\\/*?:"<>|]', "", title)
        movie = os.path.join(constants.movies, filename + ext)

        os.rename(old_movie, movie)

    print("2. Generazione del report con MediaInfo...")
    report = post.generate_report(movie, outputdir)

    print("3. Generazione del file torrent...")
    magnet = torrent.generate(movie, outputdir, filename)

    print("4. Estrazione degli screenshot...")
    screenshots = images.extract_screenshots(movie, outputdir)

    print("5. Generazione del grafico del bitrate...")
    bitrate = bv.BitrateViewer(movie)
    bitrate.analyze()

    results = bitrate.parse()
    bitrate.plot(results, outputdir)
    os.remove(os.path.join(constants.movies, filename + ".xml"))

    print("\n6. Caricamento delle immagini su Imgur...")
    uploaded_imgs = [images.upload_to_imgur(img) for img in screenshots]
    bitrate_img = images.upload_to_imgur(os.path.join(outputdir, "bitrate.png"))

    print("7. Generazione del post...")
    post.generate_text(
        data, filesize, report, uploaded_imgs, bitrate_img, magnet, outputdir
    )

    print("8. Fine!")

    print("\nIl file è stato rinominato con successo.")
    print("\nTITOLO\n->", title + "\n")
