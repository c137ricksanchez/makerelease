from typing import Dict
from urllib.parse import urlparse, urlunparse

import requests

client_id = "bcad66c82e13805"


def upload_image(path: str) -> Dict[str, str]:
    url = "https://api.imgur.com/3/image"

    with open(path, "rb") as f:
        image = f.read()

        response = requests.request(
            "POST",
            url,
            headers={"Authorization": f"Client-ID {client_id}"},
            data={"image": image},
        )

        resp = response.json()

        if not resp["success"]:
            raise Exception("Errore Imgur:", resp["data"]["error"])

        full_image = resp["data"]["link"]
        thumbnail = get_thumb(full_image)

        return {"full": full_image, "thumb": thumbnail}


def get_thumb(url: str, size: str = "l") -> str:
    parsed_url = urlparse(url)
    name, ext = parsed_url.path.rsplit(".", 1)
    parsed_url = parsed_url._replace(path=f"{name}{size}.{ext}")

    return urlunparse(parsed_url)
