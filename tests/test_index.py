import shutil

from intetes.indexation import indexer_album
from intetes.indexation.__main__ import main
from intetes.indexation.index import ecrire_jsonl, lire_jsonl


def test_indexer_l_album_de_test(analyseur, album, tmp_path):
    entrees = list(indexer_album(album, analyseur))

    assert [e["photo"] for e in entrees] == [
        "aldrin-portrait.jpg",
        "armstrong-portrait.jpg",
        "collins-portrait.jpg",
        "equipage-apollo-11.jpg",
    ]
    assert [len(e["visages"]) for e in entrees] == [1, 1, 1, 3]
    assert all(len(v["empreinte"]) == 128 for e in entrees for v in e["visages"])

    fichier = tmp_path / "index.jsonl"
    assert ecrire_jsonl(entrees, fichier) == 4
    assert lire_jsonl(fichier) == entrees


def test_une_photo_illisible_ne_bloque_pas_l_album(analyseur, album, tmp_path):
    shutil.copy(album / "collins-portrait.jpg", tmp_path / "collins.jpg")
    (tmp_path / "cassee.jpg").write_bytes(b"ceci n'est pas une photo")

    entrees = {e["photo"]: e for e in indexer_album(tmp_path, analyseur)}

    assert "erreur" in entrees["cassee.jpg"]
    assert len(entrees["collins.jpg"]["visages"]) == 1


def test_la_commande_ecrit_l_index(album, tmp_path, capsys):
    sortie = tmp_path / "index.jsonl"

    assert main([str(album), "--sortie", str(sortie)]) == 0

    assert len(lire_jsonl(sortie)) == 4
    assert "4 photos, 6 visages" in capsys.readouterr().out
