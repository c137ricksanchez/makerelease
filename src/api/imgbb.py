import base64

import requests

from .. import utils

api_key = utils.get_api_key("imgbb")


def upload_image(path: str) -> str:
    url = "https://api.imgbb.com/1/upload"

    with open(path, "rb") as f:
        image = f.read()

        response = requests.post(
            url,
            {
                "key": api_key,
                "image": base64.b64encode(image),
            },
        )

        resp = response.json()

        if not resp["success"]:
            raise Exception("Errore ImgBB")

        return resp["data"]["url"]
