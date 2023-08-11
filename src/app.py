import os
import re
import shutil
from enum import Enum
from pathlib import Path

import src.bitrateviewer as bv
from src import constants, images, metadata, post, tag, torrent, utils


class ReleaseType(Enum):
    MOVIE_FILE = "movie"
    MOVIE_FOLDER = "movie_folder"
    TV_SINGLE = "tv_single"
    TV_MULTI = "tv_multi"


def parse_release_type(type_str: str) -> ReleaseType:
    try:
        return ReleaseType(type_str)
    except ValueError:
        raise ValueError(
            f"Invalid release type: {type_str}. Must be one of:\
                {', '.join([t.value for t in ReleaseType])}"
        )


class MakeRelease:
    def __init__(self, crew: str, rename: bool, type: str, path: str, id: str):
        self.crew = crew
        self.rename = rename
        self.type = parse_release_type(type)
        self.id = id

        if (
            self.type == ReleaseType.MOVIE_FOLDER
            or self.type == ReleaseType.TV_SINGLE
            or self.type == ReleaseType.TV_MULTI
        ):
            self.folder_release = True
        else:
            self.folder_release = False

        if self.type == ReleaseType.MOVIE_FILE or self.type == ReleaseType.MOVIE_FOLDER:
            self.type_id = "movie"
        else:
            self.type_id = "tv"

        # Check if the path exists and is a file or directory
        if not os.path.exists(path):
            raise ValueError(f"Invalid path: {path}. Path does not exist.")
        if not os.path.isfile(path) and not os.path.isdir(path):
            raise ValueError(f"Invalid path: {path}. Path is not a file or directory.")

        self.path = path

    def get_file(self) -> str:
        # Switch between the cases of type
        if self.type == ReleaseType.MOVIE_FILE:
            return self.path
        elif self.type == ReleaseType.MOVIE_FOLDER:
            return utils.get_movies(self.path)[0]
        elif self.type == ReleaseType.TV_SINGLE:
            return utils.get_movies(self.path)[0]
        elif self.type == ReleaseType.TV_MULTI:
            # self.path should contain a directory with multiple seasons
            # return the first episode of the first season
            return utils.get_movies(utils.get_folders(self.path)[0])[0]
        else:
            raise ValueError(f"Invalid release type: {self.type}")

    def remove_temporary_files(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if (
                    file.startswith("._")
                    or file.startswith(".DS_Store")
                    or file.endswith(".tmp")
                ):
                    os.remove(os.path.join(root, file))

    def make_release(self):
        if not self.type == ReleaseType.MOVIE_FILE:
            self.remove_temporary_files()

        # file = Path(movie).name
        filename = Path(self.path).stem
        ext = Path(self.path).suffix

        movie = self.get_file()

        print("Name:", filename)

        title, year = utils.parse_title(filename)
        duration = utils.get_duration(movie)

        # Get the size of a directory
        releasesize = utils.get_size(self.path)

        print("\n1. Ricezione dei metadati da TheMovieDB...")

        if self.id and metadata.is_tmdb_id(self.id):
            movie_id = self.id
        else:
            movie_id = metadata.search(title, year, self.type_id)

        data = metadata.get(movie_id, self.type_id)

        outputdir = os.path.join(Path(self.path).parent, filename + "_files")
        if os.path.exists(outputdir):
            print("ERRORE: Esiste già una cartella chiamata", outputdir)
            return
        else:
            os.mkdir(outputdir)

        title = tag.parse(movie, data["title"], data["year"], self.crew)

        # Only rename the file if it is a movie file
        if self.rename and (
            self.type == ReleaseType.MOVIE_FILE or self.type == ReleaseType.MOVIE_FOLDER
        ):
            old_movie = movie

            filename = re.sub(r'[\\/*?:"<>|]', "", title)
            movie = str(os.path.join(constants.movies, filename + ext))

            os.rename(old_movie, movie)

        report = ""
        if "$REPORT_MEDIAINFO" in utils.read_file(constants.template):
            print("2. Generazione del report con MediaInfo...")
            report = post.generate_report(movie, outputdir)

        report_avinaptic = ""
        if (
            "$REPORT_AVINAPTIC" in utils.read_file(constants.template)
            and os.name == "nt"
        ):
            print("2. Generazione del report con AVInaptic...")
            if shutil.which("avinaptic2-cli"):
                report_avinaptic = post.generate_avinaptic_report(movie, outputdir)
            else:
                print("Errore: avinaptic2-cli.exe non è stato trovato.")

        print("3. Generazione del file torrent...")
        magnet = torrent.generate(self.path, outputdir, filename)

        print("4. Estrazione degli screenshot...")
        screenshots = images.extract_screenshots(movie, outputdir)

        # Salta la generazione del grafico del bitrate se non è presente
        # la variabile $BITRATE_GRAPH nel file template.txt
        skip_chart = "$BITRATE_GRAPH" not in utils.read_file(constants.template)

        print("5. Generazione del grafico del bitrate...")
        if skip_chart:
            print("Operazione saltata.")
        else:
            bitrate = bv.BitrateViewer(movie)
            bitrate.analyze()
            bitrate.plot(outputdir)

        bitrate_img = {}

        if utils.get_api_key("imgbb") != "":
            print("\n6. Caricamento delle immagini su ImgBB...")
            uploaded_imgs = [images.upload_to_imgbb(img) for img in screenshots]
            if not skip_chart:
                bitrate_img = images.upload_to_imgbb(
                    os.path.join(outputdir, "bitrate.png")
                )
        else:
            print("\n6. Caricamento delle immagini su Imgur...")
            uploaded_imgs = [images.upload_to_imgur(img) for img in screenshots]
            if not skip_chart:
                bitrate_img = images.upload_to_imgur(
                    os.path.join(outputdir, "bitrate.png")
                )

        ep_count = 0

        if self.folder_release:
            tree = utils.get_tree(self.path)
            if self.type == ReleaseType.TV_SINGLE:
                ep_count = utils.get_ep_count(self.path)
        else:
            tree = ""

        print("7. Generazione del post...")
        post.generate_text(
            data,
            releasesize,
            duration,
            report,
            report_avinaptic,
            uploaded_imgs,
            bitrate_img,
            magnet,
            outputdir,
            tree,
            ep_count,
        )

        print("8. Fine!")

        if self.rename:
            print("\nIl file è stato rinominato con successo.")

        print("\nTITOLO\n->", title + "\n")
