# Carnet de labo - Amandine LINCK

[01/10/26]
Clône du dépôt IA_declic de l'équipe, puis création de l'environnement virtuel et installation des dépendances. 

J'ai ensuite créé le projet Django, lancé le serveur pour la première fois. J'ai ensuite créé l'application de recherche avec une vue accueil et un template en Tailwind et ses URLs.

On a aussi confirmé aujourd'hui que Marin a bien quitté le groupe (sachant qu'il est absent depuis plusieurs séances). On a donc discuté avec Théo pour savoir ce qu'on allait pouvoir faire et comment est-ce qu'on va se répartir le travail. 

Au final, on pense pouvoir rendre l'application dans les temps, étant donné que du temps était déjà prévu en plus pour des tests et éventuellement des fonctionnalités supplémentaires. On se concentre pour l'instant sur les fonctions nécessaires à l'application. Pour les fonctionnalités supplémentaires on verra si on a le temps plus tard. 

Niveau répartition globalement Théo reprend le travail de Marin et je continue sur mes tâches. On a décidé de se répartir les tâches comme ça car il a déjà de l'expérience et est à l'aise avec le développement tandis que moi je débute. 

[08/10/26]
Plan du jour : 
    - Création d'une fausse fonction de recherche en attendant d'avoir la vraie pour pouvoir créer l'interface
    - Création du formulaire pour la page de recherche 
    - Création de la page de résultats (boucler sur résultatss, afficher pour chacun une carte tailwind et les mettre en grille)

Update : on change de github car Marin n'est plus dans le groupe mais est le seul à avoir les droits. 

Il faut aussi qu'on change le cahier des charges et qu'on l'update avec le départ de Marin. Je me lance dans la réécriture du cahier des charges. 

Le cahier des charges a été réécrit il ne me reste plus qu'à l'uploader sur Moodle. 

J'ai téléchargé black formatter et isort sur vsc.

La fausse fonction de recherche a été faite. 


[15/10/26]
Lecture des consignes officielles du module. Points retenus :
    - le cahier de labo se fait dans les issues (pour des raisons pratiques, on a continué à le faire dans les md, on mettra les issues à jour plus tard)
    - Docker est obligatoire (docker compose up -d, PostgreSQL et non SQLite, reverse proxy);
    - répartition de la note sur 100 points (40% code, 20% gestion de projet, 20% app Django, +5 CI/CD)

Mise à jour du cahier des charges en v2.1 : 
    - les fonctionnalités sont regroupées en lots : MVP (F1, F2, F4 à F7), lot 1 (F9), lot 2 (F8), lot 3 (F3, F10)
    - PostgreSQL et Docker Compose ajoutés dans la stack 
    - historique des versions complété

Le nouveau cahier des charges a été mis à jour sur Moodle pour le 18/10. 

[04/11/26]
RAS car absente. 

[05/11/26]
Objectif du jour : finir la base de l'interface de T5 (formulaire, résultats).

Ce que j'ai fait : 
    - la fausse fonction rechercher(photo) dans rechercher/service.py qui renvoie une liste de dico avec les éléments "importants" (nom de la photo, nom de l'événement, date de publication et score de ressemblance)
    - le formulaire de dépôt de photo dans accueil.html
    - la vue accueil qui gère le POST, récupère le fichier et appelle rechercher()
    - l'affichage des résultats en cartes Tailwind

Problèmes rencontrés et les solutions que j'ai trouvé : 
    - beaucoup de problèmes liés au fait que c'est ma première prise en main de django et tailwind (oubli de fermeture d'un {% for %}, resultat.nom qui n'affichait rien pcq c'était pas le bon nom, grid appliqué sur les mauvais conteneurs, etc.)

[07/11/26]
Objectif du jour : commencer T8 (c'est la connexion avec l'adresse mail de l'école).

Ce que j'ai fait :
    - mise à jour du cahier des charges de référence : on travaille sur la dernière version du cahier des charges (celle du 15/10) ce qui change les dates de fin des étapes. 
    - ajout des URLs de connexion de Django sous accounts/ dans config/urls.py
    - création du template de la page de connexion registration/login.html
    - création d'un compte de test avec createsuperuser, résultat : la connexion fonctionne avec nom utilisateur + mdp et non adresse mail pour l'instant

Problèmes rencontrés et les solutions que j'ai trouvé :
    - erreur 404 lors de la création de la page de connexion : l'url n'existait pas, il fallait inclure les urls d'authentification de Django
    - erreur de TemplateDoesNotExist : c'est normal, la vue de connexion est fournie par Django mais pas le template HTML, je l'ai donc écris moi même
    - pour l'instant on se connecte avec son nom d'utilisateur, rien n'empeche quelqu'un d'extérieur à l'école de créer un compte et de se connecter, conformément au cahier des charges il faut se connecter avec l'adresse de l'école (à faire pour la prochaine séance)

Reste à faire : 
    - faire en sorte qu'on puisse se connecter uniquement avec l'adresse mail de l'école

