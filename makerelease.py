import os
import re
import sys
from pathlib import Path

from src import constants, images, metadata, post, torrent, utils

sys.path.append(constants.bitrateviewer)
from bitrateviewer._bitrate_analyzer import analyze_bitrate
from bitrateviewer._plotter import plot_results

for movie in utils.get_movies(constants.movies):
    file = Path(movie).name
    filename = Path(movie).stem

    print("File:", file)

    title = filename.split("(")[0].strip()
    year = re.search("\(([0-9]{4})\)", filename).group(1)
    filesize = os.path.getsize(movie)

    outputdir = os.path.join(constants.movies, title + "_files")
    if os.path.exists(outputdir):
        print("ERRORE: Esiste già una cartella chiamata", outputdir)
        continue
    else:
        os.mkdir(outputdir)

    print("\n1. Generazione del report con MediaInfo...")
    report = post.generate_report(movie, outputdir)

    print("2. Generazione del file torrent...")
    magnet = torrent.generate(movie, outputdir, filename)

    print("3. Ricezione dei metadati da TheMovieDB...")
    movie_id = metadata.search(title, year)
    data = metadata.get(movie_id)

    print("4. Estrazione degli screenshot...")
    screenshots = images.extract_screenshots(movie, outputdir)

    print("5. Generazione del grafico del bitrate...")
    results = analyze_bitrate(movie)
    plot_results(results, filename, os.path.join(outputdir, "bitrate"))
    os.remove(os.path.join(constants.root, filename + ".xml"))

    print("6. Caricamento delle immagini su Imgur...")
    uploaded_imgs = [images.upload_to_imgur(img) for img in screenshots]
    bitrate_img = images.upload_to_imgur(os.path.join(outputdir, "bitrate.png"))

    print("7. Generazione del post...")
    post.generate_text(
        data, filesize, report, uploaded_imgs, bitrate_img, magnet, outputdir
    )

    print("8. Fine!")
