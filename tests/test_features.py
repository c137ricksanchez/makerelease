"""Test senza rete per le funzionalità aggiunte (validazione, tipi, template, selezione TMDB)."""

import os

import pytest

from makerelease import MakeRelease, ReleaseType, SearchCancelled, constants, metadata
from makerelease.app import parse_release_type

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)


# --- Tipi di release -------------------------------------------------------


def test_release_types_include_tv_episode():
    assert "tv_episode" in [t.value for t in ReleaseType]
    assert parse_release_type("tv_episode") == ReleaseType.TV_EPISODE


def test_tv_episode_is_single_file_with_tv_metadata():
    mr = MakeRelease("", False, "tv_episode", THIS_FILE, "")
    assert mr.type == ReleaseType.TV_EPISODE
    assert mr.type_id == "tv"
    assert mr.folder_release is False
    assert mr.get_file() == THIS_FILE


# --- Validazione percorso / tipo ------------------------------------------


def test_missing_path_raises():
    with pytest.raises(ValueError):
        MakeRelease("", False, "movie", os.path.join(THIS_DIR, "non_esiste.mkv"), "")


def test_folder_type_with_file_raises():
    # tv_single richiede una cartella: passando un file deve fallire
    with pytest.raises(ValueError):
        MakeRelease("", False, "tv_single", THIS_FILE, "")


def test_file_type_with_folder_raises():
    # movie richiede un file: passando una cartella deve fallire
    with pytest.raises(ValueError):
        MakeRelease("", False, "movie", THIS_DIR, "")


# --- Selezione del template ------------------------------------------------


def test_template_default_is_all():
    mr = MakeRelease("", False, "movie", THIS_FILE, "")
    assert mr.templates == constants.templates


def test_template_specific():
    if not constants.templates:
        pytest.skip("nessun template in config/")
    tpl = constants.templates[0]
    mr = MakeRelease("", False, "movie", THIS_FILE, "", template=tpl)
    assert mr.templates == [tpl]


def test_template_invalid_raises():
    with pytest.raises(ValueError):
        MakeRelease("", False, "movie", THIS_FILE, "", template="non_esiste.jinja")


# --- Selezione del titolo TMDB (console chooser) ---------------------------


def _candidates(n):
    return [{"id": str(i), "title": f"T{i}", "year": "2020"} for i in range(1, n + 1)]


def test_console_chooser_multi_choice(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *a, **k: "2")
    assert metadata._console_chooser(_candidates(3)) == "2"


def test_console_chooser_default_first(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *a, **k: "")
    assert metadata._console_chooser(_candidates(3)) == "1"


def test_console_chooser_single_override(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *a, **k: "55")
    assert metadata._console_chooser(_candidates(1)) == "55"


# --- search() con chooser iniettato (senza rete) ---------------------------


def _fake_tmdb_results(n):
    return {
        "total_results": n,
        "results": [
            {
                "id": i,
                "title": f"T{i}",
                "name": f"T{i}",
                "release_date": "2020-01-01",
                "first_air_date": "2020-01-01",
            }
            for i in range(1, n + 1)
        ],
    }


def test_search_uses_injected_chooser(monkeypatch):
    monkeypatch.setattr(metadata.tmdb, "search_movie", lambda *a, **k: _fake_tmdb_results(3))
    chosen = metadata.search("Foo", "2020", "tv", chooser=lambda candidates: candidates[1]["id"])
    assert chosen == "2"


def test_search_raises_when_cancelled(monkeypatch):
    monkeypatch.setattr(metadata.tmdb, "search_movie", lambda *a, **k: _fake_tmdb_results(2))
    with pytest.raises(SearchCancelled):
        metadata.search("Foo", "2020", "tv", chooser=lambda candidates: None)
