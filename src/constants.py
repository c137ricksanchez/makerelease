import os

root = os.getcwd()
config = os.path.join(root, "config")
movies = os.path.join(root, "movies")

keys = os.path.join(config, "keys.json")
screenshots = os.path.join(config, "screenshots.txt")
templates = ["template.txt"]
trackers = os.path.join(config, "trackers.txt")
