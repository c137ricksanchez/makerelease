import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

from . import constants
from .api import themoviedb as tmdb


def get_keys(type: str) -> Tuple[str, str]:
    if type == "movie":
        title_key = "title"
        release_date_key = "release_date"
    elif type == "tv":
        title_key = "name"
        release_date_key = "first_air_date"
    else:
        raise ValueError("Invalid type")
    return title_key, release_date_key


class SearchCancelled(Exception):
    """Sollevata quando l'utente annulla la selezione del titolo TMDB (es. dalla GUI)."""


def search(title: str, year: str, type: str, chooser=None) -> str:
    results = tmdb.search_movie(title, year, type)

    title_key, release_date_key = get_keys(type)

    # Alcuni releaser dopo il titolo in italiano mettono anche quello originale
    # Se la ricerca fallisce, provo a cercare solo il primo
    if results["total_results"] == 0 and "-" in title:
        results = tmdb.search_movie(title.split("-")[0], year, type)

    # Normalizza i risultati in una lista semplice, indipendente dal frontend
    candidates: List[Dict[str, str]] = []
    for result in results["results"]:
        release_date = result[release_date_key] if result.get(release_date_key) else ""
        candidates.append(
            {
                "id": str(result["id"]),
                "title": result[title_key],
                "year": release_date[:4] if release_date else "n.d.",
            }
        )

    # Il chooser decide quale id usare; di default si usa la console (comportamento CLI)
    chooser = chooser or _console_chooser
    selected = chooser(candidates)

    if not selected:
        raise SearchCancelled()

    return selected


def _console_chooser(candidates: List[Dict[str, str]]) -> str:
    """Selezione del titolo TMDB da terminale (default per la CLI)."""
    total = len(candidates)

    if total == 0:
        print("\nNessun risultato.")
        id = input("Inserisci manualmente un ID di TMDB (lascia vuoto per terminare lo script): ")
        return id if is_tmdb_id(id) else exit(0)

    if total == 1:
        print("Risultato:", candidates[0]["title"], f"({candidates[0]['year']})")

        choice = input("\nSe il risultato è sbagliato, inserisci un ID di TMDB [lascia vuoto per confermare]: ")
        if is_tmdb_id(choice):
            return choice

        return candidates[0]["id"]

    print("\nHo trovato", total, "risultati:\n")

    for index, candidate in enumerate(candidates, start=1):
        print(f"[{index}] {candidate['title']} ({candidate['year']})")

    choice = input(
        "\nSeleziona un film inserendo il numero della scelta (1, 2, ...) o un ID di TMDB con prefisso id: (es. id:123) [default: 1]: "
    )
    if choice.startswith("id:") and is_tmdb_id(choice[3:], True):
        return choice[3:]

    value = check_input(choice, total + 1)
    print("Film selezionato:", candidates[value - 1]["title"] + "\n")

    return candidates[value - 1]["id"]


def get(id: str, type: str) -> Dict:
    title_key, release_date_key = get_keys(type)

    try:
        data = tmdb.get_movie(id, type)
    except Exception:
        print("Non esiste nessun film con questo ID.")
        exit(-1)

    with open(os.path.join(constants.root, "src/makerelease/countries_ISO_3166-1_alpha2.json")) as file:
        country_codes = json.load(file)

        countries: List[str] = []
        for country in data["production_countries"]:
            countries.append(country_codes[country["iso_3166_1"]])

    genres: List[str] = []
    for genre in data["genres"]:
        genres.append(genre["name"])

    cast: List[Dict[str, str]] = []
    for actor in data["credits"]["cast"][:10]:
        cast.append(actor)  # each actor is a dict with keys 'name' and 'character'

    director: List[str] = []
    for crew in data["credits"]["crew"]:
        if crew["job"] == "Director":
            director.append(crew["name"])

    trailer = ""
    for video in data["videos"]["results"]:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer = "https://www.youtube.com/watch?v=" + video["key"]
            break

    poster = ""
    if data["poster_path"]:
        poster = "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    else:
        poster = "https://i.imgur.com/iDhevbK.jpg"

    return {
        "tmdb_url": f"https://www.themoviedb.org/{type}/" + str(data["id"]),
        "title": data[title_key],
        "year": str(datetime.strptime(data[release_date_key], "%Y-%m-%d").year),
        "poster_url": poster,
        "original_title": data["original_" + title_key],
        "director": ", ".join(director),
        "country": ", ".join(countries),
        "genre": ", ".join(genres),
        "cast": cast,
        "plot": data["overview"],
        "trailer": trailer,
    }


def check_input(choice: str, max: int, default: int = 1) -> int:
    values = range(1, max)

    if choice == "":
        choice = "1"

    response = int(choice)

    if response in values:
        return response
    else:
        print(f"Scelta non valida. Seleziono {default}")
        return default


def is_tmdb_id(string: str, silent: bool = False) -> bool:
    if string.isdigit():
        return True
    else:
        if not silent and string:
            print("ERRORE: Non è un ID di TMDB valido.")

        return False
