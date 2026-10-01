# INTêtes

Retrouver les photos d'un album où l'on apparaît, en déposant une photo de soi. Projet du module PRO 8501 (projet informatique en Python, FISA 2A, Télécom SudParis).

Un cahier des charges plus complet est disponible dans `docs/Cahier des charges - INTêtes.pdf`.

## Où en est le code

| Partie | Tâche du cahier des charges | État |
|---|---|---|
| Indexation : lecture des albums, détection des visages, empreintes | T3 | en cours, premier socle dans `intetes/indexation` |
| Recherche par similarité | T4 | à venir |
| Interface web, dépôt d'une photo, galerie | T5 | à venir |
| Regroupement des visages en personnes | T6 | à venir |
| Base de l'index et stockage des empreintes | T7 | à venir, l'index est pour l'instant un fichier JSON Lines |

## Installation

Python 3.10 ou plus récent.

```bash
python -m venv .venv
source .venv/bin/activate        # sous Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Au premier lancement, les deux modèles (environ 39 Mo) sont téléchargés dans `~/.cache/intetes/modeles` (ou dans le dossier indiqué par la variable `INTETES_MODELES`), puis vérifiés par leur empreinte SHA-256.

## Indexer un album

```bash
python -m intetes.indexation chemin/vers/album --sortie index.jsonl
```

Les sous-dossiers sont parcourus. Le fichier produit contient une ligne JSON par photo :

```json
{"photo": "soiree/IMG_0042.jpg", "largeur": 6000, "hauteur": 4000,
 "visages": [{"boite": [1204, 855, 180, 231], "score": 0.94, "empreinte": [0.0123, ...]}]}
```

- `boite` : position du visage en pixels de la photo d'origine (x, y, largeur, hauteur) ;
- `empreinte` : 128 nombres qui caractérisent le visage, de norme 1 ;
- une photo illisible donne une ligne avec un champ `erreur` au lieu de `visages`, sans arrêter l'album.

Depuis Python :

```python
from intetes.indexation import Analyseur, indexer_album, lire_photo, similarite, SEUIL_MEME_PERSONNE

analyseur = Analyseur()
[moi] = analyseur.analyser(lire_photo("ma_photo.jpg"))
for entree in indexer_album("album", analyseur):
    for visage in entree.get("visages", []):
        if similarite(moi.empreinte, visage["empreinte"]) >= SEUIL_MEME_PERSONNE:
            print(entree["photo"])
```

## Choix techniques

- **OpenCV 5** avec deux modèles libres du zoo OpenCV : **YuNet** pour détecter les visages (licence MIT) et **SFace** pour calculer les empreintes (licence Apache 2.0). Aucune dépendance difficile à installer (pas de dlib).
- **Détection en deux passes** (photo ramenée à 2560 puis à 800 pixels sur son grand côté) : YuNet ne voit que les visages d'environ 10 à 300 pixels. Mesuré sur un portrait de 3300 x 4125 pixels, le visage de 525 pixels est raté en pleine taille et trouvé dès qu'on réduit la photo. Les doublons entre les deux passes sont fusionnés.
- **Seuil de similarité à 0,363** (valeur donnée par OpenCV pour SFace sur le jeu LFW). Sur l'album de test, deux photos d'une même personne obtiennent entre 0,64 et 0,83, et deux personnes différentes jusqu'à 0,32 : la marge est mince, il faudra recalibrer le seuil sur de vraies photos de soirée (lumière faible, flou, contre-jour).
- Les photos sont lues avec Pillow (orientation EXIF appliquée) et les modèles sont chargés depuis la mémoire : sous Windows, OpenCV n'ouvre pas un chemin qui contient des accents.

## Données personnelles

Une empreinte de visage est une donnée biométrique (article 9 du RGPD). Un index construit sur de vraies photos ne doit jamais être poussé sur le dépôt (les fichiers `index*.jsonl` sont ignorés par Git), et aucune mise en service n'est possible sans le consentement explicite prévu au cahier des charges.

## Tests

```bash
pytest
```

L'album de test (`tests/donnees`) est fait de photos de la NASA de l'équipage d'Apollo 11, dans le domaine public (sources dans `tests/donnees/SOURCES.md`). Aucune photo d'étudiant n'est utilisée.