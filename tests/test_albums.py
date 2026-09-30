import numpy as np
from PIL import Image

from intetes.indexation import lire_photo, lister_photos


def creer_image(chemin, taille=(40, 20), couleur=(255, 0, 0), exif=None):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", taille, couleur)
    if exif:
        image.save(chemin, exif=exif)
    else:
        image.save(chemin)


def test_lister_photos_garde_les_images_et_ignore_le_reste(tmp_path):
    for nom in ["a.jpg", "b.PNG", "sous-dossier/c.jpeg", ".cache/cachee.jpg", ".d.jpg"]:
        creer_image(tmp_path / nom)
    (tmp_path / "notes.txt").write_text("pas une photo")

    photos = [p.relative_to(tmp_path).as_posix() for p in lister_photos(tmp_path)]

    assert photos == ["a.jpg", "b.PNG", "sous-dossier/c.jpeg"]


def test_lire_photo_avec_des_accents_dans_le_chemin(tmp_path):
    chemin = tmp_path / "Soirée d'été" / "photo n°1.jpg"
    creer_image(chemin, couleur=(255, 0, 0))

    image = lire_photo(chemin)

    assert image.shape == (20, 40, 3)
    bleu, vert, rouge = image[10, 20]
    assert rouge > 200 and vert < 50 and bleu < 50  # l'image est bien en BGR


def test_lire_photo_redresse_selon_l_orientation_exif(tmp_path):
    exif = Image.Exif()
    exif[0x0112] = 6  # prise appareil tourné : à afficher après une rotation de 90 degrés
    chemin = tmp_path / "tournee.jpg"
    creer_image(chemin, taille=(40, 20), exif=exif)

    image = lire_photo(chemin)

    assert image.shape[:2] == (40, 20)
    assert isinstance(image, np.ndarray)
