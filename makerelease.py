import argparse

from src.app import MakeRelease, ReleaseType

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
        "-p",
        "--path",
        type=str,
        help="Path to the movie or folder",
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[t.value for t in ReleaseType],
        help="Release type",
    )

    args = parser.parse_args()

    # Instantiate the class
    release_maker = MakeRelease(args.crew, args.rename, args.type, args.path)

    # Call the make_release method with the movie argument
    release_maker.make_release()
