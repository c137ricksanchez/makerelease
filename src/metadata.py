import math
from datetime import datetime

from src.api import themoviedb as tmdb


def search(title: str, year: int) -> str:
    results = tmdb.search_movie(title, year)

    if results["total_results"] == 0:
        # Alcuni releaser dopo il titolo in italiano mettono anche quello originale
        # Se la ricerca fallisce, provo a cercare solo il primo
        if "-" in title:
            results = tmdb.search_movie(title.split("-")[0], year)
        else:
            print("Nessun risultato.")

            id = input(
                "Inserisci manualmente un ID di IMDb (lascia vuoto per terminare lo script): "
            )
            return id if id else exit(0)

    print("Ho trovato", results["total_results"], "risultati:\n")

    id = 1
    for result in results["results"]:
        print(f"[{id}] {result['title']} ({result['release_date'][:4]})")
        id += 1

    value = check_input(input("\nSeleziona un film [default: 1]: "), id)
    return results["results"][value - 1]["id"]


def get(id: str) -> dict:
    data = tmdb.get_movie(id)
    credits = tmdb.get_movie_credits(id)
    videos = tmdb.get_movie_videos(id)

    countries = []
    for country in data["production_countries"]:
        countries.append(country["name"])

    genres = []
    for genre in data["genres"]:
        genres.append(genre["name"])

    cast = []
    for actor in credits["cast"][:10]:
        cast.append(f"[*]{actor['name']}: {actor['character']}")

    director = []
    for crew in credits["crew"]:
        if crew["job"] == "Director":
            director.append(crew["name"])

    trailer = ""
    for video in videos["results"]:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer = "https://www.youtube.com/watch?v=" + video["key"]
            break

    return {
        "imdb_url": f"https://www.imdb.com/title/{id}",
        "title": data["title"],
        "year": datetime.strptime(data["release_date"], "%Y-%m-%d").year,
        "poster_url": "https://image.tmdb.org/t/p/w500" + data["poster_path"],
        "original_title": data["original_title"],
        "director": ", ".join(director),
        "runtime": parse_runtime(data["runtime"]),
        "country": ", ".join(countries),
        "genre": ", ".join(genres),
        "cast": "\n".join(cast),
        "plot": data["overview"],
        "trailer": trailer,
    }


def check_input(choice: str, max: int, default: int = 1) -> int:
    values = range(1, max)

    if choice == "":
        choice = default

    if int(choice) in values:
        return int(choice)
    else:
        print(f"Scelta non valida. Seleziono {default}")
        return default


def parse_runtime(mins: int) -> str:
    hours = math.floor(mins / 60)
    minutes = mins % 60

    return f"{hours}h {minutes}m"
