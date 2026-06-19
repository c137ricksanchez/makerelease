import os
import re
import shutil
from enum import Enum
from pathlib import Path

from . import constants, images, metadata, post, tag, torrent, utils
from .bitrateviewer import BitrateViewer


class ReleaseType(Enum):
    MOVIE_FILE = "movie"
    MOVIE_FOLDER = "movie_folder"
    TV_EPISODE = "tv_episode"
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
    def __init__(self, crew: str, rename: bool, type: str, path: str, id: str, template: str = None, chooser=None):
        self.crew = crew
        self.rename = rename
        self.type = parse_release_type(type)
        self.id = id
        # Callback per la selezione del titolo TMDB; None = selezione da console (CLI)
        self.chooser = chooser

        # template=None -> usa tutti i template presenti in config/ (comportamento storico)
        if template is not None and template not in constants.templates:
            raise ValueError(
                f"Invalid template: {template}. Must be one of: {', '.join(constants.templates)}"
            )
        self.templates = [template] if template else constants.templates

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

        # Controllo esistenza e coerenza del percorso con il tipo di release
        if not os.path.exists(path):
            raise ValueError(
                f"Percorso non trovato: {path}\n"
                "Verifica che esista e sia raggiungibile. Per i percorsi di rete (\\\\server\\...): "
                "controlla connessione e credenziali e assicurati che il terminale NON sia avviato come "
                "Amministratore (le connessioni di rete dell'utente non sono visibili al processo elevato)."
            )

        # I tipi 'movie_folder', 'tv_single' e 'tv_multi' lavorano su una cartella; 'movie' su un file
        if self.folder_release and not os.path.isdir(path):
            raise ValueError(
                f"Il tipo '{type}' richiede una CARTELLA, ma il percorso indicato è un file:\n{path}\n"
                "Indica la cartella (es. quella della stagione) oppure usa '-t movie' per un singolo file."
            )
        if not self.folder_release and not os.path.isfile(path):
            raise ValueError(
                f"Il tipo '{type}' richiede un FILE, ma il percorso indicato è una cartella:\n{path}\n"
                "Indica il file video oppure usa '-t movie_folder' / '-t tv_single' per una cartella."
            )

        self.path = path

    def get_file(self) -> str:
        # Switch between the cases of type
        if self.type == ReleaseType.MOVIE_FILE or self.type == ReleaseType.TV_EPISODE:
            return self.path
        elif self.type == ReleaseType.MOVIE_FOLDER or self.type == ReleaseType.TV_SINGLE:
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
                if file.startswith("._") or file.startswith(".DS_Store") or file.endswith(".tmp"):
                    os.remove(os.path.join(root, file))

    def make_release(self):
        if self.folder_release:
            self.remove_temporary_files()

        if os.path.isdir(self.path):
            name = Path(self.path).name
        elif os.path.isfile(self.path):
            name = Path(self.path).stem
            ext = Path(self.path).suffix

        # Get the file to analyze
        file = self.get_file()

        print("Name:", name)

        title, year = utils.parse_title(name)
        duration = utils.get_duration(file)
        releasesize = utils.get_size(self.path)

        # name = original name of the file
        # file = path of the file to analyze
        # title = parsed title of the movie

        print("\n1. Ricezione dei metadati da TheMovieDB...")

        if self.id and metadata.is_tmdb_id(self.id):
            movie_id = self.id
        else:
            movie_id = metadata.search(title, year, self.type_id, self.chooser)

        data = metadata.get(movie_id, self.type_id)

        new_name = tag.parse(file, data["title"], data["year"], self.crew)
        new_name = re.sub(r'[\\/*?:"<>|]', "", new_name)

        # Rinomina solo per i tipi a file singolo o per il film in cartella
        if self.rename and (
            self.type == ReleaseType.MOVIE_FILE
            or self.type == ReleaseType.MOVIE_FOLDER
            or self.type == ReleaseType.TV_EPISODE
        ):
            os.rename(
                src=file,
                dst=os.path.join(Path(self.path).parent, f"{new_name}{ext}" if ext else new_name),
            )
            name = new_name

            # Per i tipi a file singolo abbiamo appena rinominato il file da analizzare, aggiorniamolo
            if self.type == ReleaseType.MOVIE_FILE or self.type == ReleaseType.TV_EPISODE:
                self.path = os.path.join(Path(self.path).parent, f"{new_name}{ext}")
                file = self.get_file()

        outputdir = os.path.join(Path(self.path).parent, f"{name}_files")
        if os.path.exists(outputdir):
            print("La cartella", outputdir, "esiste già: riprendo riutilizzando i file già presenti.")
        else:
            os.mkdir(outputdir)

        report = ""
        report_avinaptic = ""
        # Salta la generazione del grafico del bitrate se non è presente
        # la variabile {{ BITRATE_GRAPH }} nel file template.jinja
        # controllo in anticipo skip_chart per evitare cicli sui template successivi
        skip_chart = True
        for t in self.templates:
            template = utils.read_file(os.path.join(constants.config, t))

            if "{{ BITRATE_GRAPH }}" in template:
                skip_chart = False

            if "{{ REPORT_MEDIAINFO }}" in template and report == "":
                print("\n2. Generazione del report con MediaInfo...")
                if os.path.exists(os.path.join(outputdir, "report_mediainfo.txt")):
                    print("  |---> File Mediainfo già presente, skip step")
                    report = utils.read_file(os.path.join(outputdir, "report_mediainfo.txt"))
                else:
                    report = post.generate_report(file, outputdir)

            if "{{ REPORT_AVINAPTIC }}" in template and os.name == "nt" and report_avinaptic == "":
                print("2. Generazione del report con AVInaptic...")
                if shutil.which("avinaptic2-cli"):
                    if os.path.exists(os.path.join(outputdir, "report_avinaptic.txt")):
                        print("  |---> File AVInaptic già presente, skip step")
                        report_avinaptic = utils.read_file(os.path.join(outputdir, "report_avinaptic.txt"))
                    else:
                        report_avinaptic = post.generate_avinaptic_report(file, outputdir)
                else:
                    print("Errore: avinaptic2-cli.exe non è stato trovato.")

        print("\n3. Generazione del file torrent...")
        if os.path.exists(os.path.join(outputdir, f"{name}.torrent")):
            print("  |---> File Torrent già presente, skip step")
            magnet = torrent.get_magnet(outputdir, name)
        else:
            magnet = torrent.generate(self.path, outputdir, name)

        print("\n4. Estrazione degli screenshot...")
        screenshots = images.extract_screenshots(file, outputdir)

        # Salta la generazione del grafico del bitrate se non è presente
        # la variabile {{ BITRATE_GRAPH }} nel file template.jinja
        print("\n5. Generazione del grafico del bitrate...")
        if skip_chart:
            print("Operazione saltata.")
        else:
            if os.path.exists(os.path.join(outputdir, "bitrate.png")):
                print("  |---> Grafico già generato, skip step")
            else:
                bitrate = BitrateViewer(file)
                bitrate.analyze()
                bitrate.plot(outputdir)

        bitrate_img = {}

        if utils.get_api_key("imgbly"):
            print("\n6. Caricamento delle immagini su ImgBly...")
            uploaded_imgs = [images.upload_to_imgbly(img) for img in screenshots]
            if not skip_chart:
                bitrate_img = images.upload_to_imgbly(os.path.join(outputdir, "bitrate.png"))
        elif utils.get_api_key("imgbb") != "":
            print("\n6. Caricamento delle immagini su ImgBB...")
            uploaded_imgs = [images.upload_to_imgbb(img) for img in screenshots]
            if not skip_chart:
                bitrate_img = images.upload_to_imgbb(os.path.join(outputdir, "bitrate.png"))
        else:
            print("\n6. Caricamento delle immagini su Imgur...")
            uploaded_imgs = [images.upload_to_imgur(img) for img in screenshots]
            if not skip_chart:
                bitrate_img = images.upload_to_imgur(os.path.join(outputdir, "bitrate.png"))

        ep_count = 0
        tree = ""

        if self.folder_release:
            tree = utils.get_tree(self.path)
            if self.type == ReleaseType.TV_SINGLE or self.type == ReleaseType.TV_MULTI:
                ep_count = utils.get_ep_count(self.path)

        print("\n7. Generazione del post...")
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
            templates=self.templates,
        )

        print("\n8. Fine!")

        if self.rename:
            print("\nIl file è stato rinominato con successo.")

        print("\nTITOLO\n->", new_name + "\n")
        return
