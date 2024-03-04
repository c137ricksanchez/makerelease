import argparse

from src.makerelease import MakeRelease, ReleaseType

if __name__ == "__main__":
    # Instantiate the parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path",
        metavar="PATH",
        type=str,
        help="Percorso del file o della cartella",
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[t.value for t in ReleaseType],
        default=ReleaseType.MOVIE_FILE,
        help="Tipo di release (default: movie)",
    )

    parser.add_argument(
        "-r",
        "--rename",
        default=False,
        action="store_true",
        help="Rinomina in automatico il file seguendo il formato consigliato",
    )

    parser.add_argument(
        "-c",
        "--crew",
        type=str,
        help="Nome della crew da inserire alla fine del nome del file",
    )

    parser.add_argument(
        "-i",
        "--id",
        type=str,
        help="ID del titolo su TheMovieDB",
    )

    args = parser.parse_args()

    # Instantiate the class
    release_maker = MakeRelease(args.crew, args.rename, args.type, args.path, args.id)

    # Call the make_release method with the movie argument
    release_maker.make_release()
