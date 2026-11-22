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

[12/11/26]
Objectif du jour : finir T8, l'inscription doit être réservée aux adresses de l'école.

Ce que j'ai fait : 
    - création du formulaire SchoolEmailUserCreationForm qui hérite de UserCreationForm de Django
    - la méthode clean_username refuse toute adresse qui ne finit pas par @telecom-sudparis.eu ou @imt-bs.eu
    - création de la vue register et de la page d'inscription registration/register.html
    - ajout d'un lien "Créer un compte" sur la page de connexion

Problèmes rencontrés et les solutions que j'ai trouvé : 
    - j'ai d'abord voulu récupérer la valeur avec cleaned_data, mais dans une méthode clean_<champ> il faut appeler super().clean_username() pour garder les vérifications de Django 
    - ma condition était fausse avec "not A or not B" : une adresse valide pour une école était refusée par l'autre condition, il fallait un "and"
    - pour tester le formulaire sans passer par le navigateur, j'ai utilisé python manage.py shell avec Form(data={...}) puis is_valid() et errors

[13/11/26]
Objectif du jour : finir la connexion/déconnexion et tester l'inscription. 

Ce que j'ai fait :
    - LOGIN_REDIRECT_URL vers l'accueil et LOGOUT_REDIRECT_URL vers la page de connexion
    - bouton de déconnexion en formulaire POST avec csrf_token (la déconnexion en GET ne marche plus avec les versions récentes de Django)
    - 2 tests unitaires sur la validation de l'adresse : une adresse de l'école est acceptée, une adresse gmail est refusée
    - après le renommage de l'app recherche en search par Théo, correction de l'import dans les tests et de la balise url du bouton de déconnexion
    - installation de Docker Desktop pour lancer le projet en local

Problèmes rencontrés et les solutions que j'ai trouvé : 
    - conflit de merge sur config/settings.py après un git pull : j'ai gardé la config PostgreSQL de Théo et mes réglages de redirection
    - push refusé (fetch first) parce que Théo avait poussé entre : git pull puis push
    - "Ran 0 tests" : les méthodes de test doivent commencer par test_ sinon Django ne les trouve pas
    - le conteneur web plantait au démarrage (exit 255) : sous Windows, git convertissait entrypoint/sh en fins de ligne CRLF que Linux ne sait pas lire. J'ai ajouté un .gitattributes avec *.sh text eol=lf

[14/11/26]
Objectif du jour : commencer l'internationalisation (i18n) du site textes en anglais traduits en français. 

Ce que j'ai fait : 
    - installation de gettext (nécessaire pour générer les fichiers de traduction)
    - dans settinfs.py : LANGUAGES (français et anglais),
    LOCALE_PATHS vers le dossier locale/ et LocaleMiddleware entre SessionMiddleware et CommonMiddleware
    - textes des templates register.html, home.html et login.html réécrits en anglais avec {% translate %}, et {% blocktranslate %} pour les phrases qui contiennent une variable ("Logged in as ...")
    - attribut lang de la page qui suit la langue active avec get_current_language
    - mise à jour des issues #3, #6 et #12, fermeture de #6 (T8 terminée)

Problèmes rencontrés et les solutions que j'ai trouvé :
    - ImproperlyConfigured sur LOCALE_PATHS : il faut une liste [BASE_DIR / "locale"] et pas un seul chemin 
    - {% translate %} n'accepte pas de variable dans le texte, il faut {% blocktranslate with ... %}

[21/11/26]
Objectif du jour : bouton de retrait de l'index (demande de Théo dans #8) et fin de la galerie T5. 

Ce que j'ai fait : 
    - textes de forms.py passés en anglais avec gettext_lazy, formatage avec black et isort pour passer la CI de Théo 
    - bouton "Remove my face data" en rouge dans home.html, en POST vers remove_from_index, avec une confirmation avant l'envoi (onsubmit="return confirm(...)")
    - galerie : affichage de l'image avec un lien vers la photo d'origine (F5), "No album" pour les photos sans album, et un message "No results found." quand la recherche ne trouve rien
    - test complet sous Docker : indexation d'un album en admin, recherche, puis retrait. La Person et ses Face sont supprimées, les photos restent dans l'album

Problèmes rencontrés et les solutions que j'ai trouvé : 
    - erreur 403 en cliquant sur le bouton de retrait : je m'étais connectée en admin dans le même navigateur, ce qui change le jeton CSRF. Il faut recharger la page après un changement de compte
    - "rien ne se passe" quand je cherche avec une photo : aucun visage n'était détecté sur les grandes images. En testant, une photo de 2687 px donne 0 visage et la même réduite à 1680 px en donne 1. J'ai signalé le bug à Théo dans #12
    - le message "aucun résultat" s'affichait dès l'ouverture de la page : je l'ai conditionné à request.method == "POST"

Reste à faire : 
    - F10 : cases à cocher et vouton de téléchargement ZIP dans la galerie (demande de Théo dans #11)
    - design des pages 403, 404 et 500 (demande de Théo dans #3)
    - fin de l'i18n : makemessages, traduction de .po, compilemessages, sélecteur de langue 

    