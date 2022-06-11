import requests

clientId = "bcad66c82e13805"


def upload_image(path: str) -> str:
    url = "https://api.imgur.com/3/image"

    with open(path, "rb") as f:
        image = f.read()

        response = requests.request(
            "POST",
            url,
            headers={"Authorization": f"Client-ID {clientId}"},
            data={"image": image},
        )

        resp = response.json()

        if not resp["success"]:
            raise Exception("Errore Imgur:", resp["data"]["error"])

        return resp["data"]["link"]
