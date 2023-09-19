from typing import Dict
import json
import http.client
from codecs import encode
import requests
import io
from PIL import Image
from bs4 import BeautifulSoup

BASE_URL = "https://www.imgbly.com/"

def imgbly_upload(path: str) -> Dict[str, str]:
    print("Avvio caricamento con ImgBly di:", path)
    
    # Apri l'immagine originale
    original_image = Image.open(path)
    
    # Carica l'immagine originale
    with open(path, "rb") as f:
        image_data = f.read()

    full_res = upload(path, image_data)
    thumb_res = upload_thumb(path, original_image)

    full_url = f"{BASE_URL}ib/{full_res['data']['id']}.png"
    thumb_url = f"{BASE_URL}ib/{thumb_res['data']['id']}.png"
    res = {"full":full_url, "thumb":thumb_url}
    print(f'  |---> Caricamento completato con successo:\n    |---> Piena risoluzione: {full_url} - Risoluzione ridotta: {thumb_url}')
    return res


def upload(path, image_data) -> str:
    # Effettua una richiesta GET alla pagina principale di ImgBly
    response = requests.get(BASE_URL)

    csrf_token_value = ''
    # Verifica se la richiesta è andata a buon fine
    if response.status_code == 200:
        # Parsa il contenuto HTML della pagina
        soup = BeautifulSoup(response.text, "html.parser")
        # Trova il tag meta con l'attributo csrf-token
        csrf_token = soup.find("meta", {"name": "csrf-token"})

        xsrf_token = response.cookies["XSRF-TOKEN"]
        imgbly_session = response.cookies["imgbly_session"]
        # Estrai il valore del token CSRF
        if csrf_token:
            csrf_token_value = csrf_token["content"]
            # print("CSRF Token:", csrf_token_value) #enable it for debug
        else:
            print("Token CSRF non trovato nella pagina.")
    else:
        print("Errore nella richiesta GET:", response.status_code)
        exit(-1)
    conn = http.client.HTTPSConnection("www.imgbly.com")
    dataList = []
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

    # caricamento immagine full resolution
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=uploads; filename=image.png'))
    dataList.append(encode('Content-Type: image/png'))
    dataList.append(encode(''))
    dataList.append(image_data)
    dataList.append(encode('--'+boundary+'--'))
    dataList.append(encode(''))

    body = b'\r\n'.join(dataList)
    payload = body
    headers = {
        'accept': 'application/json',
        'x-csrf-token': f'{csrf_token_value}',
        'Cookie': f'XSRF-TOKEN={xsrf_token}; imgbly_session={imgbly_session}',
        'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
    }
    conn.request("POST", "/upload", payload, headers)
    res = conn.getresponse()
    response_data = res.read()
    if res.status == 200:
        # Esegui il parsing JSON solo una volta
        resp = json.loads(response_data.decode("utf-8"))
        return resp
    else:
        # Gestisci qui eventuali errori di stato della risposta
        print(f"Errore nella richiesta: {res.status}")
        return None


def upload_thumb(path, original) -> str:
    # Calcola le dimensioni della thumbnail mantenendo il rapporto d'aspetto
    width = 960
    ratio = width / float(original.size[0])
    height = int(float(original.size[1]) * ratio)
    
    # Crea la thumbnail
    thumbnail = original.resize((width, height), Image.LANCZOS)
    
    # Salva la thumbnail in un buffer di memoria
    thumbnail_buffer = io.BytesIO()
    thumbnail.save(thumbnail_buffer, format="PNG")
    
    # Carica la thumbnail
    thumbnail_data = thumbnail_buffer.getvalue()

    return upload(path, thumbnail_data)
