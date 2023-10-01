# update_check.py

import subprocess
import os
import requests

# Ottieni la versione locale dall'__init__.py
from MakeRelease import __version__  # Sostituisci "MakeRelease" con il nome del tuo pacchetto

# URL del server di controllo degli aggiornamenti da caricarare nella cartella principale e da modificare ogni volta che si rilascia un update
url_server_aggiornamenti = "https://raw.githubusercontent.com/c137ricksanchez/automatic-releaser/master/aggiornamenti.json"

def check_for_update():
    # Ottieni la directory corrente dell'operazione
    repo_dir = os.getcwd()

    try:
        # Effettua una richiesta per ottenere le informazioni sulla versione più recente
        response = requests.get(url_server_aggiornamenti)
        response.raise_for_status()

        # Analizza il file JSON delle informazioni sugli aggiornamenti
        informazioni_aggiornamenti = response.json()

        # Ottieni la versione più recente dal file JSON
        versione_remota = informazioni_aggiornamenti.get("versione")

        # Confronta la versione locale con la versione remota
        if versione_remota and versione_remota > __version__:
            print("Una nuova versione è disponibile!")
            print(f"Versione locale: {__version__}")
            print(f"Versione remota: {versione_remota}")

            # Esegui git pull per aggiornare l'applicazione
            subprocess.check_call(['git', 'pull'])

            print("Aggiornamento completato con successo!")

        else:
            print("L'applicazione è aggiornata.")

    except (requests.exceptions.RequestException, subprocess.CalledProcessError) as e:
        print(f"Errore durante il controllo degli aggiornamenti o l'aggiornamento con Git: {e}")

if __name__ == "__main__":
    # Chiamare la funzione check_for_update() all'avvio dell'applicazione
    check_for_update()
