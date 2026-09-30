"""Indexation des albums : lecture des photos, détection des visages et calcul des empreintes."""

from .albums import lire_photo, lister_photos
from .index import indexer_album
from .visages import SEUIL_MEME_PERSONNE, Analyseur, Visage, similarite

__all__ = [
    "Analyseur",
    "SEUIL_MEME_PERSONNE",
    "Visage",
    "indexer_album",
    "lire_photo",
    "lister_photos",
    "similarite",
]
