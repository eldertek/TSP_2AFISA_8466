"""Indexation d'un album : une entrée par photo, avec ses visages et leurs empreintes.

Le format JSON Lines sert d'échange avec la recherche en attendant la base de l'index.
"""

import json
from collections.abc import Callable, Iterator
from pathlib import Path

from .albums import lire_photo, lister_photos
from .visages import Analyseur


def indexer_album(
    album: Path,
    analyseur: Analyseur | None = None,
    suivi: Callable[[int, int, Path], None] | None = None,
) -> Iterator[dict]:
    """Analyse chaque photo de l'album. Une photo illisible donne une entrée avec « erreur »."""
    album = Path(album)
    analyseur = analyseur or Analyseur()
    photos = lister_photos(album)
    for rang, chemin in enumerate(photos, start=1):
        if suivi:
            suivi(rang, len(photos), chemin)
        entree = {"photo": chemin.relative_to(album).as_posix()}
        try:
            image = lire_photo(chemin)
        except (OSError, ValueError) as erreur:
            entree["erreur"] = f"photo illisible : {erreur}"
            yield entree
            continue
        entree["largeur"], entree["hauteur"] = image.shape[1], image.shape[0]
        entree["visages"] = [
            {
                "boite": list(visage.boite),
                "score": round(visage.score, 4),
                "empreinte": [round(float(v), 6) for v in visage.empreinte],
            }
            for visage in analyseur.analyser(image)
        ]
        yield entree


def ecrire_jsonl(entrees, fichier: Path) -> int:
    """Écrit une entrée par ligne et renvoie le nombre d'entrées."""
    fichier = Path(fichier)
    fichier.parent.mkdir(parents=True, exist_ok=True)
    nombre = 0
    with fichier.open("w", encoding="utf-8") as sortie:
        for entree in entrees:
            sortie.write(json.dumps(entree, ensure_ascii=False) + "\n")
            nombre += 1
    return nombre


def lire_jsonl(fichier: Path) -> list[dict]:
    with Path(fichier).open(encoding="utf-8") as entree:
        return [json.loads(ligne) for ligne in entree if ligne.strip()]
