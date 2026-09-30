import cv2
import numpy as np

from intetes.indexation import SEUIL_MEME_PERSONNE, Analyseur, lire_photo, similarite


def test_un_seul_visage_par_portrait(analyseur, album):
    for nom in ["armstrong-portrait.jpg", "aldrin-portrait.jpg", "collins-portrait.jpg"]:
        assert len(analyseur.detecter(lire_photo(album / nom))) == 1, nom


def test_les_trois_visages_de_la_photo_de_groupe(analyseur, album):
    visages = analyseur.detecter(lire_photo(album / "equipage-apollo-11.jpg"))

    assert len(visages) == 3
    assert all(v.score >= 0.8 for v in visages)


def test_aucun_visage_sur_une_image_unie(analyseur):
    assert analyseur.detecter(np.full((600, 800, 3), 128, np.uint8)) == []


def test_empreinte_de_128_valeurs_normee(analyseur, photo_recherche):
    image = lire_photo(photo_recherche)
    [visage] = analyseur.analyser(image)

    assert visage.empreinte.shape == (128,)
    assert abs(np.linalg.norm(visage.empreinte) - 1.0) < 1e-5


def test_la_meme_personne_se_retrouve_dans_la_photo_de_groupe(analyseur, album, photo_recherche):
    [recherche] = analyseur.analyser(lire_photo(photo_recherche))
    groupe = analyseur.analyser(lire_photo(album / "equipage-apollo-11.jpg"))

    scores = [similarite(recherche.empreinte, v.empreinte) for v in groupe]

    # sur la photo officielle, Armstrong est à gauche (les visages sont triés de gauche à droite)
    assert scores[0] >= SEUIL_MEME_PERSONNE
    assert all(s < SEUIL_MEME_PERSONNE for s in scores[1:])


def test_deux_personnes_differentes_restent_sous_le_seuil(analyseur, album):
    [aldrin] = analyseur.analyser(lire_photo(album / "aldrin-portrait.jpg"))
    [collins] = analyseur.analyser(lire_photo(album / "collins-portrait.jpg"))

    assert similarite(aldrin.empreinte, collins.empreinte) < SEUIL_MEME_PERSONNE


def test_un_gros_plan_est_trouve_grace_a_la_passe_reduite(analyseur, photo_recherche):
    image = lire_photo(photo_recherche)
    gros_plan = cv2.resize(image, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)  # visage d'environ 900 px de large

    # en pleine taille, YuNet rate un visage aussi grand (et peut même en voir un faux ailleurs)
    sans_reduction = Analyseur(cotes=(10_000,)).detecter(gros_plan)
    assert all(v.boite[2] < 600 for v in sans_reduction)

    [visage] = analyseur.detecter(gros_plan)
    assert visage.boite[2] > 600
