"""Détection des visages (YuNet) et calcul de leur empreinte (SFace)."""

from dataclasses import dataclass, field

import cv2
import numpy as np

from . import modeles

# Seuil de similarité cosinus au-delà duquel deux empreintes sont jugées de la même
# personne (valeur donnée par OpenCV pour SFace sur le jeu LFW). À recalibrer sur les
# vraies photos du club, en particulier les photos de soirée.
SEUIL_MEME_PERSONNE = 0.363

# YuNet ne trouve que les visages d'environ 10 à 300 pixels. On cherche donc deux fois :
# une passe fine pour les petits visages des photos de groupe, une passe réduite pour les
# gros plans (un visage de 525 px sur une photo de 3300 x 4125 est raté en pleine taille).
COTES_DE_DETECTION = (2560, 800)


@dataclass
class Visage:
    """Un visage dans une photo, en coordonnées de la photo d'origine."""

    boite: tuple[int, int, int, int]  # x, y, largeur, hauteur
    score: float
    reperes: np.ndarray  # 5 points : œil droit, œil gauche, nez, coin droit et coin gauche de la bouche
    empreinte: np.ndarray | None = field(default=None, repr=False)  # 128 valeurs, norme 1

    def ligne_opencv(self) -> np.ndarray:
        """Le visage au format attendu par FaceRecognizerSF.alignCrop (15 valeurs)."""
        return np.concatenate([np.array(self.boite, np.float32), self.reperes.ravel(), [self.score]]).astype(np.float32)


def similarite(a: np.ndarray, b: np.ndarray) -> float:
    """Similarité cosinus de deux empreintes normées : 1 = identiques, 0 ou moins = sans rapport."""
    return float(np.dot(a, b))


def _recouvrement(a: tuple, b: tuple) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    largeur = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    hauteur = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    commun = largeur * hauteur
    union = aw * ah + bw * bh - commun
    return commun / union if union else 0.0


class Analyseur:
    """Trouve les visages d'une image et calcule leur empreinte."""

    def __init__(self, seuil_detection: float = 0.8, cotes: tuple[int, ...] = COTES_DE_DETECTION):
        vide = np.array([], np.uint8)
        self.detecteur = cv2.FaceDetectorYN.create(
            "onnx", np.frombuffer(modeles.charger(modeles.YUNET), np.uint8), vide, (320, 320), seuil_detection, 0.3, 5000
        )
        self.encodeur = cv2.FaceRecognizerSF.create("onnx", np.frombuffer(modeles.charger(modeles.SFACE), np.uint8), vide)
        self.cotes = cotes

    def detecter(self, image: np.ndarray) -> list[Visage]:
        hauteur, largeur = image.shape[:2]
        trouves: list[Visage] = []
        for cote in self.cotes:
            echelle = min(1.0, cote / max(hauteur, largeur))
            if echelle < 1.0:
                travail = cv2.resize(image, None, fx=echelle, fy=echelle, interpolation=cv2.INTER_AREA)
            else:
                travail = image
            self.detecteur.setInputSize((travail.shape[1], travail.shape[0]))
            _, lignes = self.detecteur.detect(travail)
            for ligne in [] if lignes is None else lignes:
                valeurs = ligne[:14] / echelle
                trouves.append(
                    Visage(
                        boite=tuple(int(round(v)) for v in valeurs[:4]),
                        score=float(ligne[14]),
                        reperes=valeurs[4:14].reshape(5, 2).astype(np.float32),
                    )
                )
        # un même visage vu par les deux passes : on garde la détection la plus sûre
        retenus: list[Visage] = []
        for visage in sorted(trouves, key=lambda v: v.score, reverse=True):
            if all(_recouvrement(visage.boite, deja.boite) < 0.4 for deja in retenus):
                retenus.append(visage)
        return sorted(retenus, key=lambda v: (v.boite[0], v.boite[1]))

    def empreinte(self, image: np.ndarray, visage: Visage) -> np.ndarray:
        aligne = self.encodeur.alignCrop(image, visage.ligne_opencv())
        vecteur = self.encodeur.feature(aligne).ravel().astype(np.float32)
        return vecteur / np.linalg.norm(vecteur)

    def analyser(self, image: np.ndarray) -> list[Visage]:
        visages = self.detecter(image)
        for visage in visages:
            visage.empreinte = self.empreinte(image, visage)
        return visages
