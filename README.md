<!-- omit from toc -->
# makerelease

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

**makerelease** è un comodo script per velocizzare la pubblicazione di film e serie tv sul forum MIRCrew! 🚀

> ⚠️ **ATTENZIONE:**
> Questo repository è pubblicato a scopo informativo e didattico.

- [Funzionalità](#funzionalità)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
  - [Windows](#windows)
  - [Linux](#linux)
  - [macOS](#macos)
- [Aggiornamento](#aggiornamento)
- [Utilizzo](#utilizzo)
- [Autori](#autori)


## Funzionalità

- Ottiene i dati del film o della serie tv da TheMovieDB
- Crea il report con MediaInfo
- Crea il file .torrent
- Estrae gli screenshot
- Genera il grafico del bitrate
- Carica tutte le immagini su Imgur o ImgBB
- Prepara il testo del post da pubblicare sul forum con tutte le informazioni
- Formatta il titolo (e opzionalmente rinomina anche il nome del file) seguendo il formato consigliato da MIRCrew

Possibilità di scegliere il tipo di release da effettuare:

- **Film**
  1. **Film**: seleziona un singolo file `mkv`, `mp4` o `avi`
  2. **Film + Extra**: seleziona una directory contenente un file video e un numero arbitrario di cartelle `Extra`, `Featurettes`, ecc. La procedura è identica al caso precedente, l'unica differenza è l'aggiunta della directory nel torrent.

- **Serie TV**
  1. **Stagione singola**: seleziona una directory contenente più file video. Lo script identifica la serie dal nome della cartella.
  2. **Serie completa**: seleziona una directory contenente più cartelle. Lo script identifica la serie dal nome della cartella principale.

## Requisiti

- Python 3.8 (o più recente)
- FFmpeg
- MediaInfo

## Installazione

### Windows

1. Installa Python
    - `winget install Python.Python.3.11`
2. Installa Git
    - `winget install Git.Git`
3. Clona il repository
    - `git clone https://github.com/c137ricksanchez/automatic-releaser.git`
4. Installa le dipendenze
    - `cd automatic-releaser`
    - `pip install -r requirements.txt`
5. Scarica [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/latest) ed estrai `ffmpeg.exe` e `ffprobe.exe` nella directory di makerelease

### Linux

1. Installa Python, Git, FFmpeg e MediaInfo
    - Arch: `pacman -S python python-pip git ffmpeg mediainfo`
    - Debian/Ubuntu: `apt install python3 python3-pip git ffmpeg mediainfo`
    - Fedora: `dnf install python3 python3-pip git ffmpeg mediainfo`
        - *Per installare FFmpeg devi attivare i repository [RPM Fusion](https://docs.fedoraproject.org/en-US/quick-docs/setup_rpmfusion/)*
2. Clona il repository
    - `git clone https://github.com/c137ricksanchez/automatic-releaser.git`
3. Installa le dipendenze
    - `cd automatic-releaser`
    - `pip3 install -r requirements.txt`

### macOS

1. Installa Homebrew
    - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Installa Python
    - `brew install python3`
3. Installa Git
    - `brew install git`
4. Clona il repository
    - `git clone https://github.com/c137ricksanchez/automatic-releaser.git`
5. Installa le dipendenze
    - `cd automatic-releaser`
    - `pip3 install -r requirements.txt`

## Aggiornamento

1. Entra nella repository
   - `cd automatic-releaser`
3. Esegui il comando
   - `git pull`

## Utilizzo

1. Nella cartella `config`, rinomina `keys.example.json` in `keys.json`
2. Configura lo script modificando i file nella cartella `config`
    - `keys.json`
        - `imgbb`: Se desideri caricare le immagini su ImgBB, ottieni la [chiave API](https://api.imgbb.com/) e inseriscila qui. **Lascia vuoto per utilizzare Imgur.**
        - `tmdb`: Inserisci la chiave delle API di TheMovieDB (se non ne hai una, registrati e [ottienila qui](https://www.themoviedb.org/settings/api))
    - `screenshots.txt`
        - Inserisci i timestamp dove lo script andrà ad estrarre gli screenshot
    - `template.txt`
        - Scrivi il template base del post da pubblicare sul forum. Le variabili come ad esempio `$TITLE` verranno sostituite in automatico con i dati del film
        - Se non vuoi generare il grafico del bitrate, rimuovi la variabile `$BITRATE_GRAPH`
    - `trackers.txt`
        - Inserisci la *trackers list* che verrà usata per generare il file *.torrent* e il magnet
3. MakeRelease può essere usato sia tramite GUI che tramite linea di comando:
   - GUI
     - Apri il terminale ed esegui:
       - Windows: `python ./gui.py`
       - macOS/Linux: `python3 ./gui.py`
   - Linea di comando
     - Apri il terminale ed esegui il comando utilizzando i flag riportati sotto per scegliere le opzioni:
       - Windows: `python ./makerelease.py`
       - macOS/Linux: `python3 ./makerelease.py`

```
makerelease.py [-h] [-c CREW] [-r] [-p PATH] [-t movie,movie_folder,tv_single,tv_multi]
```

| Short | Long       | Default | Description                                                                     |
| ----- | ---------- | ------- | ------------------------------------------------------------------------------- |
| `-h`  | `--help`   |         | show this help message and exit                                                 |
| `-p`  | `--path`   |         | Percorso della cartella o del file                                              |
| `-t`  | `--type`   |         | Tipo di release, a scelta tra: `movie`, `movie_folder`, `tv_single`, `tv_multi` |
| `-r`  | `--rename` | `False` | Rinomina in automatico il file seguendo il formato consigliato da MIRCrew       |
| `-c`  | `--crew`   |         | Nome della crew da inserire alla fine del nome del file                         |

## Autori

- Rick Sanchez
- Norman
