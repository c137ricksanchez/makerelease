from typing import Dict

import requests

from .. import utils

api_key = utils.get_api_key("tmdb")


def search_movie(title: str, year: str, type: str):
    return request_json(
        f"https://api.themoviedb.org/3/search/{type}",
        {"api_key": api_key, "language": "it-IT", "query": title, "year": year},
    )


def get_movie(id: str, type: str):
    return request_json(
        f"https://api.themoviedb.org/3/{type}/{id}",
        {
            "api_key": api_key,
            "language": "it-IT",
            "append_to_response": "credits,videos",
        },
    )


def request_json(url: str, params: Dict[str, str]):
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Errore {response.status_code} - {response.text}")

    return response.json()
