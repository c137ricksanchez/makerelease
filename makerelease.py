import argparse
import update_check


from src.app import MakeRelease, ReleaseType

def main():

    # Controlla gli aggiornamenti
    update_check.check_for_update()

if __name__ == "__main__":
    # Instantiate the parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Indirizzo della cartella o del file",
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[t.value for t in ReleaseType],
        help="Tipo di release",
    )

    parser.add_argument(
        "-r",
        "--rename",
        default=False,
        action="store_true",
        help="Rinomina in automatico il file seguendo il formato consigliato da MIRCrew",
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
