"""Indexer un album en ligne de commande.

    python -m intetes.indexation chemin/vers/album --sortie index.jsonl
"""

import argparse
import sys
import time
from pathlib import Path

import cv2

from .index import ecrire_jsonl, indexer_album
from .visages import Analyseur


def main(arguments: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(prog="python -m intetes.indexation", description="Indexe les visages d'un album photo.")
    parseur.add_argument("album", type=Path, help="dossier de l'album (les sous-dossiers sont parcourus)")
    parseur.add_argument("--sortie", type=Path, default=Path("index.jsonl"), help="fichier d'index à écrire (JSON Lines)")
    parseur.add_argument("--seuil", type=float, default=0.8, help="score minimal d'une détection (0 à 1)")
    options = parseur.parse_args(arguments)

    if not options.album.is_dir():
        print(f"Album introuvable : {options.album}", file=sys.stderr)
        return 2

    # OpenCV 5 prévient à chaque modèle chargé que les « targets » ne sont pas gérées : sans effet ici
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
    debut = time.monotonic()
    entrees = list(
        indexer_album(
            options.album,
            Analyseur(seuil_detection=options.seuil),
            suivi=lambda rang, total, chemin: print(f"[{rang}/{total}] {chemin.name}", file=sys.stderr),
        )
    )
    ecrire_jsonl(entrees, options.sortie)

    visages = sum(len(e.get("visages", [])) for e in entrees)
    sans_visage = sum(1 for e in entrees if "visages" in e and not e["visages"])
    erreurs = [e for e in entrees if "erreur" in e]
    print(
        f"{len(entrees)} photos, {visages} visages, {sans_visage} photos sans visage, "
        f"{len(erreurs)} erreurs, en {time.monotonic() - debut:.1f} s. Index : {options.sortie}"
    )
    for entree in erreurs:
        print(f"  {entree['photo']} : {entree['erreur']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
