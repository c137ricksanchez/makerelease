import os

root = os.path.dirname(os.path.realpath(__file__)) + "/../../"
config = os.path.join(root, "config")

keys = os.path.join(config, "keys.json")
screenshots = os.path.join(config, "screenshots.txt")
trackers = os.path.join(config, "trackers.txt")

# Trova tutti i file che iniziano con "template" nella cartella config
templates = [file for file in os.listdir(config) if file.startswith("template") and file.endswith(".jinja")]
