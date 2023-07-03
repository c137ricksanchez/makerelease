import argparse
import os
import re
from enum import Enum
from pathlib import Path

import src.bitrateviewer as bv
from src import constants, images, metadata, post, tag, torrent, utils


class ReleaseType(Enum):
    MOVIE_FILE = "Movie (File)"
    MOVIE_FOLDER = "Movie (Folder)"
    TV_SINGLE = "TV Series (Single Season)"
    TV_MULTI = "TV Series (Multiple Seasons)"


def parse_release_type(type_str: str) -> ReleaseType:
    try:
        return ReleaseType(type_str.lower())
    except ValueError:
        raise ValueError(
            f"Invalid release type: {type_str}. Must be one of: {', '.join([t.value for t in ReleaseType])}"
        )


#type_str = input("Enter release type (movie/tv): ")
#release_type = parse_release_type(type_str)
#release = MakeRelease("crew", True, release_type, "path/to/file")


class MakeRelease:
    def __init__(self, crew: str, rename: bool, type: ReleaseType, path: str):
        self.crew = crew
        self.rename = rename
        self.type = type

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
            raise ValueError(
                f"Invalid release type: {self.type}. Must be one of: {', '.join([t.value for t in ReleaseType])}"
            )

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
        # ext = Path(movie).suffix

        movie = self.get_file()

        print("Name:", filename)

        title, year = utils.parse_title(filename)
        duration = utils.get_duration(movie)
        filesize = os.path.getsize(movie)

        print("\n1. Ricezione dei metadati da TheMovieDB...")
        movie_id = metadata.search(title, year)
        data = metadata.get(movie_id)

        outputdir = os.path.join(Path(self.path), Path(movie).name + "_files")
        if os.path.exists(outputdir):
            print("ERRORE: Esiste già una cartella chiamata", outputdir)
            return
        else:
            os.mkdir(outputdir)

        title = tag.parse(movie, data["title"], data["year"], self.crew)

        if self.rename:
            old_movie = movie

            filename = re.sub(r'[\\/*?:"<>|]', "", title)
            movie = str(os.path.join(constants.movies, filename + ext))

            os.rename(old_movie, movie)

        print("2. Generazione del report con MediaInfo...")
        report = post.generate_report(movie, outputdir)

        print("3. Generazione del file torrent...")
        magnet = torrent.generate(movie, outputdir, filename)

        print("4. Estrazione degli screenshot...")
        screenshots = images.extract_screenshots(movie, outputdir)

        # Salta la generazione del grafico del bitrate se non è presente la variabile $BITRATE_GRAPH nel file template.txt
        skip_chart = "$BITRATE_GRAPH" not in utils.read_file(constants.template)

        print("5. Generazione del grafico del bitrate...")
        if skip_chart:
            print("Operazione saltata.")
        else:
            bitrate = bv.BitrateViewer(movie)
            bitrate.analyze()

            results = bitrate.parse()
            bitrate.plot(results, outputdir)
            os.remove(os.path.join(constants.movies, filename + ".xml"))

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

        print("7. Generazione del post...")
        post.generate_text(
            data,
            filesize,
            duration,
            report,
            uploaded_imgs,
            bitrate_img,
            magnet,
            outputdir,
        )

        if self.type == ReleaseType.MOVIE_FOLDER \
            or self.type == ReleaseType.TV_SINGLE \
            or self.type == ReleaseType.TV_MULTI:

            # Get the tree of the directory
            utils.get_tree(self.path)

            # TODO add tree to the report if it's a folder release
        

        print("8. Fine!")

        if self.rename:
            print("\nIl file è stato rinominato con successo.")

        print("\nTITOLO\n->", title + "\n")


if __name__ == "__main__":
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

    parser.add_argument(
        "path",
        type=str,
        help="Path to the movie or folder",
    )

    parser.add_argument(
        "type",
        type=str,
        choices=[t.value for t in ReleaseType],
        help="Release type",
    )

    args = parser.parse_args()

    # Instantiate the class
    release_maker = MakeRelease(args.crew, args.rename, args.type, args.path)

    # Call the make_release method with the movie argument
    release_maker.make_release()
