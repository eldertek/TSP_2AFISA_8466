def rechercher(photo):
    """
    Fausse fonction de recherche d'images.
    Elle me sert à retourner les informations dont j'ai besoin pour test le front.
    Elle renvoie une liste avec un dictionnaire par photo trouvée.
    Dans chaque dictionnaire on a 4 clefs :
        - photo : le nom ou chemin de la photo
        - evenement : le nom de l'evenement/album
        - date : la date de publication de l'album
        - score : un nombre entre 0 et 1 qui représente la ressemblance
    """
    return [
        {
            "photo": "photo1.jpg",
            "evenement": "Gala - Stand",
            "date": "2026-02-26",
            "score": 0.8,
        },
        {
            "photo": "photo2.jpg",
            "evenement": "Gala - Volant",
            "date": "2026-02-26",
            "score": 0.7,
        },
        {
            "photo": "photo1.jpg",
            "evenement": "Gala - Volant",
            "date": "2026-02-26",
            "score": 0.9,
        },
        {
            "photo": "photo1.jpg",
            "evenement": "Soirée Hypnos - Volant",
            "date": "2026-02-03",
            "score": 0.6,
        },
        {
            "photo": "photo46.jpg",
            "evenement": "Soirée Parainnage - Volant",
            "date": "2025-10-18",
            "score": 0.8,
        },
        {
            "photo": "photo67.jpg",
            "evenement": "Gala - Stand",
            "date": "2026-02-26",
            "score": 0.9,
        },
    ]
