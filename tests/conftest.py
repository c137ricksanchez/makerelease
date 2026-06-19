import os
import shutil

# constants.py legge la cartella config/ all'import: su un clone pulito non esiste.
# Se manca del tutto, la creiamo dall'esempio così i test sono eseguibili ovunque.
# Se esiste già (es. la config reale dell'utente) non la tocchiamo.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG = os.path.join(_ROOT, "config")
_EXAMPLE = os.path.join(_ROOT, "config_example")

if not os.path.isdir(_CONFIG) and os.path.isdir(_EXAMPLE):
    shutil.copytree(_EXAMPLE, _CONFIG)
