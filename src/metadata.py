import json
from datetime import datetime
from typing import Dict, List

from src.api import themoviedb as tmdb


def search(title: str, year: str, type: str) -> str:
    results = tmdb.search_movie(title, year, type)

    # Alcuni releaser dopo il titolo in italiano mettono anche quello originale
    # Se la ricerca fallisce, provo a cercare solo il primo
    if results["total_results"] == 0 and "-" in title:
        results = tmdb.search_movie(title.split("-")[0], year, type)

    if results["total_results"] == 0:
        print("\nNessun risultato.")

        id = input(
            "Inserisci manualmente un ID di TMDB (lascia vuoto per terminare lo script): "
        )
        return id if is_tmdb_id(id) else exit(0)

    if results["total_results"] == 1:
        print(
            "Risultato:",
            results["results"][0]["title"],
            f"({results['results'][0]['release_date'][:4]})",
        )

        choice = input(
            "\nSe il risultato è sbagliato, inserisci un ID di TMDB [lascia vuoto per confermare]: "
        )
        if is_tmdb_id(choice):
            return choice

        return results["results"][0]["id"]

    print("\nHo trovato", results["total_results"], "risultati:\n")

    id = 1
    for result in results["results"]:
        release_date = result["release_date"] if result.get("release_date") else "n.d."
        print(f"[{id}] {result['title']} ({release_date[:4]})")
        id += 1

    choice = input("\nSeleziona un film o inserisci un ID di TMDB [default: 1]: ")
    if is_tmdb_id(choice, True):
        return choice

    value = check_input(choice, id)
    print("Film selezionato:", results["results"][value - 1]["title"] + "\n")

    return results["results"][value - 1]["id"]


def get(id: str, type: str) -> Dict[str, str]:
    try:
        data = tmdb.get_movie(id, type)
    except Exception:
        print("Non esiste nessun film con questo ID.")
        exit(-1)

    credits = tmdb.get_movie_credits(id, type)
    videos = tmdb.get_movie_videos(id, type)

    with open("src/countries_ISO_3166-1_alpha2.json") as file:
        country_codes = json.load(file)

        countries: List[str] = []
        for country in data["production_countries"]:
            countries.append(country_codes[country["iso_3166_1"]])

    genres: List[str] = []
    for genre in data["genres"]:
        genres.append(genre["name"])

    cast: List[str] = []
    for actor in credits["cast"][:10]:
        cast.append(f"[*]{actor['name']}: {actor['character']}")

    director: List[str] = []
    for crew in credits["crew"]:
        if crew["job"] == "Director":
            director.append(crew["name"])

    trailer = ""
    for video in videos["results"]:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer = "https://www.youtube.com/watch?v=" + video["key"]
            break

    if type == "movie":
        date = data["release_date"]
    else:
        date = data["first_air_date"]
    
    return {
        "tmdb_url": "https://www.themoviedb.org/movie/" + str(data["id"]),
        "title": data["title"] if type == "movie" else data["name"],
        "year": str(datetime.strptime(date, "%Y-%m-%d").year),
        "poster_url": "https://image.tmdb.org/t/p/w500" + data["poster_path"],
        "original_title": data["original_title"] if type == "movie" else data["original_name"],
        "director": ", ".join(director),
        "country": ", ".join(countries),
        "genre": ", ".join(genres),
        "cast": "\n".join(cast),
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
