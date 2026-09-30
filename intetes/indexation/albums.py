"""Lecture des albums photo."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def lister_photos(album: Path) -> list[Path]:
    """Photos de l'album et de ses sous-dossiers, dans un ordre stable.

    Les fichiers et dossiers cachés (nom commençant par un point) sont ignorés.
    """
    album = Path(album)
    photos = []
    for chemin in album.rglob("*"):
        relatif = chemin.relative_to(album)
        if any(partie.startswith(".") for partie in relatif.parts):
            continue
        if chemin.is_file() and chemin.suffix.lower() in EXTENSIONS:
            photos.append(chemin)
    return sorted(photos)


def lire_photo(chemin: Path) -> np.ndarray:
    """Image en BGR (convention OpenCV), redressée selon son orientation EXIF.

    Pillow ouvre aussi les chemins avec accents, contrairement à cv2.imread sous Windows.
    """
    with Image.open(chemin) as image:
        image = ImageOps.exif_transpose(image)
        rgb = np.asarray(image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
