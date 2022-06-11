# makerelease

**makerelease** è un comodo script per velocizzare la pubblicazione di film sul forum MIRCrew! 🚀

> **ATTENZIONE:**
> Questo repository è pubblicato a scopo informativo e didattico.

Funzionalità:

- Crea il report MediaInfo
- Crea il file .torrent
- Ottiene i metadati da TheMovieDB (titolo, anno, durata, trama, regista, cast, ecc.)
- Estrae gli screenshot
- Genera il grafico del bitrate
- Carica tutte le immagini su Imgur
- Prepara il testo del post da pubblicare sul forum con tutte le informazioni del film, poster, trailer, report e link magnet!

## Requisiti

- Python 3
- FFmpeg
- MediaInfo

## Installazione

### Windows 10+

1. Installa Python
    - `winget install Python.Python.3`
2. Installa Git
    - `winget install Git.Git`
3. Clona il repository
    - `git clone https://github.com/c137ricksanchez/automatic-releaser.git`
4. Installa le dipendenze
    - `cd automatic-releaser`
    - `pip install -r requirements.txt`
5. Scarica [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/latest) ed estrai `ffmpeg.exe` e `ffprobe.exe` nella cartella di makerelease

### Linux

1. Installa Python, Git, FFmpeg e MediaInfo
    - Arch: `pacman -S python python-pip git ffmpeg mediainfo`
    - Debian/Ubuntu: `apt install python3 python3-pip git ffmpeg mediainfo`
    - Fedora: `dnf install python3 python3-pip git ffmpeg mediainfo`
        - **NOTA**: Per installare FFmpeg devi attivare i repository [RPM Fusion](https://docs.fedoraproject.org/en-US/quick-docs/setup_rpmfusion/)!
2. Clona il repository
    - `git clone https://github.com/c137ricksanchez/automatic-releaser.git`
3. Installa le dipendenze
    - `cd automatic-releaser`
    - `pip3 install -r requirements.txt`

### macOS

1. Installa Homebrew
    - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Installa Python usando Homebrew
    - `brew install python3`
3. Installa Git usando Homebrew
    - `brew install git`
4. Clona il repository
    - `git clone https://github.com/c137ricksanchez/automatic-releaser.git`
5. Installa le dipendenze
    - `cd automatic-releaser`
    - `pip3 install -r requirements.txt`

## Utilizzo

1. Configura lo script modificando i file nella cartella `config`
    - `keys.json`
        - Rinomina il file `keys.example.json` in `keys.json` e inserisci la chiave delle API di TheMovieDB (se non ne hai una, registrati e [ottienila qui](https://www.themoviedb.org/settings/api)).
    - `screenshots.txt`
        - Inserisci i timestamp dove lo script andrà ad estrarre gli screenshot.
    - `template.txt`
        - Scrivi il template base del post da pubblicare sul forum. Le variabili come ad esempio `$TITLE` verranno sostituite in automatico con i dati del film.
    - `trackers.txt`
        - Inserisci la *trackers list* che verrà usata per generare il file *.torrent* e il magnet.
2. Metti uno o più film che vuoi rellare nella cartella `movies`
3. Esegui `./makerelease.py`

## Autori

- Rick Sanchez
- Norman
