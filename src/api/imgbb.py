import base64
from typing import Dict

import requests

from .. import utils
from . import imgbly

api_key = utils.get_api_key("imgbb")


def upload_image(path: str) -> Dict[str, str]:
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

        if "success" not in resp:
            print(
                "Si è verificato un errore durante il caricamento delle immagini su ImgBB"
            )
            print(
                "errore ImgBB nel tentativo di caricare l'immagine: ",
                path,
                "  -->  ",
                resp["error"]["message"],
            )
            print("Tentativo di caricamento alternativo su https://imgbly.com/")
            imgbly_upload = imgbly.upload_image(path)
            return imgbly_upload
            # exit(-1)

        full_image = resp["data"]["url"]
        thumbnail = resp["data"]["display_url"]

        return {"full": full_image, "thumb": thumbnail}
