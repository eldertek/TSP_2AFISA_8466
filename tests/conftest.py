from pathlib import Path

import pytest

from intetes.indexation import Analyseur

DONNEES = Path(__file__).parent / "donnees"


@pytest.fixture(scope="session")
def analyseur():
    # le premier lancement télécharge les deux modèles (environ 39 Mo)
    return Analyseur()


@pytest.fixture
def album():
    return DONNEES / "album"


@pytest.fixture
def photo_recherche():
    return DONNEES / "recherche-armstrong.jpg"
