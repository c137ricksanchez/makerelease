import os

root = os.getcwd()
config = os.path.join(root, "config")
movies = os.path.join(root, "movies")

keys = os.path.join(config, "keys.json")
screenshots = os.path.join(config, "screenshots.txt")
trackers = os.path.join(config, "trackers.txt")

# Trova tutti i file che iniziano con "template" nella cartella corrente
templates = [file for file in os.listdir(config) if file.startswith(
    "template") and file.endswith(".txt")]
