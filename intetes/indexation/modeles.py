"""Modèles ONNX du zoo OpenCV : YuNet pour détecter les visages, SFace pour les empreintes.

Ils sont téléchargés au premier usage dans un dossier de cache (variable d'environnement
INTETES_MODELES, sinon ~/.cache/intetes/modeles) puis vérifiés par leur SHA-256.
Licences : YuNet sous licence MIT, SFace sous licence Apache 2.0
(https://github.com/opencv/opencv_zoo).
"""

import hashlib
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ZOO = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models"


@dataclass(frozen=True)
class Modele:
    fichier: str
    url: str
    sha256: str


YUNET = Modele(
    "face_detection_yunet_2026may.onnx",
    f"{ZOO}/face_detection_yunet/face_detection_yunet_2026may.onnx",
    "ebafce4e3c118d6554634be5c27ab333b4c047a9a8c3faf1d7cf93101c22f0f0",
)
SFACE = Modele(
    "face_recognition_sface_2021dec.onnx",
    f"{ZOO}/face_recognition_sface/face_recognition_sface_2021dec.onnx",
    "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
)


def dossier_cache() -> Path:
    return Path(os.environ.get("INTETES_MODELES") or Path.home() / ".cache" / "intetes" / "modeles")


def charger(modele: Modele) -> bytes:
    """Contenu du modèle, téléchargé s'il manque.

    On donne les octets à OpenCV plutôt qu'un chemin : sous Windows, OpenCV n'ouvre pas
    un fichier dont le chemin contient des accents.
    """
    chemin = dossier_cache() / modele.fichier
    if not chemin.exists():
        chemin.parent.mkdir(parents=True, exist_ok=True)
        partiel = chemin.with_name(chemin.name + ".part")
        urllib.request.urlretrieve(modele.url, partiel)
        partiel.replace(chemin)
    contenu = chemin.read_bytes()
    if hashlib.sha256(contenu).hexdigest() != modele.sha256:
        chemin.unlink()
        raise RuntimeError(f"{modele.fichier} est corrompu, il a été supprimé : relancer pour le retélécharger")
    return contenu
