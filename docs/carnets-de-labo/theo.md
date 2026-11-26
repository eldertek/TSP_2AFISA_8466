# Carnet de labo - André Théo LAURET

## 01 / 10 / 2026
Suite au départ de Marin, l'effectif de notre équipe est réduit. Je reprends donc l'ensemble du travail qui lui était attribué. Afin de rester concentrés sur les objectifs essentiels du cahier des charges, nous décalons certaines fonctionnalités optionnelles et priorisons le socle nécessaire au fonctionnement du projet.

Nous réévaluerons cette organisation lors des prochaines séances, à la mi-octobre. Si l'avancement et la charge de travail le permettent, nous pourrons alors réintégrer une partie des fonctionnalités optionnelles dans les priorités.

J'ai installé les dépendances sur une nouvelle instance de Python, car mon ordinateur est équipé d'un processeur ARM. Or, OpenCV n'est pas compatible avec cette architecture. J'ai donc dû réinstaller avec l'architecture x64 afin de pouvoir installer les dépendances et retester la base.

## 08 / 10 / 2026
Installation de Docker Desktop et de Windows Subsystem for Linux afin de mettre en place un environnement Docker pour le projet.

Nous devons réfléchir au fait de choisir entre un seul Dockerfile ou plusieurs. L'avantage de plusieurs Dockerfiles est d'avoir des images adaptées à nos différents cas d'usage (site/admin/workers) et plus légères individuellement. L'inconvénient est que nous devrons segmenter et séparer notre code. En revanche, on peut simplifier en mettant tout dans une seule image et affiner les comportements via des lignes de commande.

Marin a quitté le projet mais il détient les accès au repository. On a donc décidé de recréer le repo sur mon compte (eldertek/TSP_2AFISA_8466) afin de pouvoir le mettre à disposition des encadrants. Les issues ne peuvent pas être transférées d'un compte à un autre, on les a donc recopiées avec un lien vers les anciennes, et on a remis les mêmes assignations.

On a ajouté l'application indexing et j'ai développé une fonction pour détecter les visages avec le détecteur YuNet d'OpenCV (la reconnaissance, avec les empreintes SFace, viendra ensuite). J'ai également mis en place un formulaire pour uploader les images et les passer au détecteur. Le résultat est affiché sur la page /indexing/, indiquant le nombre de visages détectés et leurs coordonnées. 
Mise en place du formatage automatique avec black et isort via pre-commit, et explication dans le README.

## 12 / 11 / 2026
On a mis à jour le cahier des charges en version 2.1 et adapté les issues en conséquence, notamment avec l'ajout de la tâche T15 pour gérer les files d'indexation et de recherche avec Celery et Redis.

J'ai développé les quatre modèles de la base de données dans l'application indexing (Album, Photo, Person et Face) et je les ai enregistrés dans l'interface d'administration de Django. Pour les photos, on a choisi de mettre le on_delete à SET_NULL sur l'album et sur l'utilisateur qui l'a déposée. Comme ça, si un album est supprimé ou qu'un administrateur quitte le bureau d'une année sur l'autre, les photos restent conservées et pourront être affichées dans un album par défaut. Pour les visages, l'empreinte SFace est stockée en binaire afin de prendre moins de place et d'être plus rapide à lire avec NumPy, et la suppression d'une personne supprime en cascade ses visages sans toucher aux photos d'origine.

Au moment de commiter, la sécurité Windows (Smart App Control) a bloqué l'exécution de black et isort lancés par pre-commit. Comme il est impossible de désactiver cette sécurité sans devoir réinstaller Windows par la suite, j'ai préféré passer par WSL. J'ai réparé le DNS de ma distribution Linux qui bloquait l'accès à pip, puis j'ai installé black et isort dans un environnement virtuel sur WSL pour pouvoir formater le code avant les commits.

J'ai ensuite mis en place l'architecture Docker complète du projet avec trois conteneurs dans compose.yaml : la base de données PostgreSQL, le serveur applicatif Django servi par Gunicorn, et un reverse proxy Nginx exposé sur le port 8080 pour servir directement les fichiers statiques et les médias partagés via des volumes. J'ai remplacé opencv-python par opencv-python-headless pour éviter les erreurs de bibliothèques graphiques manquantes dans le conteneur Linux. Enfin, j'ai ajouté un script entrypoint.sh qui applique les migrations, collecte les fichiers statiques et crée automatiquement le compte administrateur au démarrage, ainsi que le script run.sh à la racine pour tout lancer en une seule commande.

## 13 / 11 / 2026
J'ai complété la partie détection avec l'extraction des empreintes biométriques grâce au modèle SFace d'OpenCV dans indexing/faces.py. Après la détection par YuNet, chaque visage est aligné et découpé avec alignCrop puis transformé en un vecteur de 128 flottants converti en binaire (512 octets). J'ai ensuite mis à jour la vue d'indexation (protégée par login_required) pour enregistrer la photo déposée et chacun des visages détectés avec ses coordonnées et son empreinte directement dans la base PostgreSQL.

J'ai ensuite développé le moteur de recherche par similarité dans recherche/service.py pour remplacer les fausses données de test. Lorsqu'un utilisateur dépose une photo, on détecte son visage et on extrait son empreinte SFace, puis on la compare avec la distance cosinus d'OpenCV à l'ensemble des empreintes stockées en base (récupérées en une seule requête grâce à select_related sur la photo et l'album). Les résultats dépassant le seuil de reconnaissance (0.363) sont triés par score décroissant et affichés dans la galerie.

On a également harmonisé tout le code en anglais en renommant l'application recherche en search, et supprimé l'ancien module en ligne de commande intetes devenu obsolète. Enfin, j'ai implémenté le retrait de l'index en un clic (T10) : lors d'une recherche, les visages reconnus sont associés à l'entité Person de l'utilisateur connecté, et la vue remove_from_index permet de supprimer cette entité ainsi que toutes ses empreintes associées en cascade, tout en conservant les photos dans les albums.

J'ai ensuite configuré Celery avec Redis comme broker dans Django et ajouté trois nouveaux services dans compose.yaml : le conteneur Redis et deux workers séparés (worker_indexing sur la file indexing et worker_search sur la file search) qui partagent le volume des médias avec le serveur web. L'upload d'une photo déclenche désormais une tâche asynchrone index_photo pour ne plus bloquer le serveur web pendant la détection et le calcul des empreintes, tandis que la recherche passe par sa propre file prioritaire search_faces_task.

## 20 / 11 / 2026
J'ai complété la page d'indexation (F1) pour permettre de sélectionner un album existant ou d'en créer un nouveau avec sa date d'événement, puis d'envoyer plusieurs photos d'un coup vers la file Celery indexing. J'ai également restreint l'accès à cette page aux membres du staff (erreur 403 pour les comptes étudiants classiques).

J'ai ensuite écrit les tests unitaires dans indexing/tests.py et search/tests.py afin de vérifier la détection YuNet, l'extraction SFace, le contrôle d'accès sur /indexing/, l'upload multi-photos, la recherche par similarité et le retrait de l'index en un clic (9 tests au total avec ceux d'Amandine). Enfin, j'ai ajouté un workflow GitHub Actions (.github/workflows/ci.yml) qui vérifie automatiquement le formatage black/isort, les migrations, les tests unitaires et le build de l'image Docker à chaque push.

## 21 / 11 / 2026
J'ai généré le graphe des modèles de la base de données (docs/models.png) avec django-extensions et Graphviz afin de documenter l'architecture des tables et leurs relations vers User. J'ai également mis à jour le README pour refléter le projet actuel (lancement Docker via run.sh, identifiants admin, architecture des 6 services, roadmap et tests).

J'ai ensuite mis en place les pages d'erreur personnalisées (templates/403.html, 404.html et 500.html) en déclarant le dossier templates à la racine dans settings.py et en passant l'accès refusé de /indexing/ sur PermissionDenied. J'ai complété les tests dans search/tests.py pour vérifier les trois codes d'erreur (12 tests qui passent au total) et demandé à Amandine sur l'issue #3 d'habiller le design de ces pages.

J'ai aussi développé la fonctionnalité de téléchargement en archive ZIP (F10) dans search/views.py à l'aide de zipfile et io.BytesIO. Chaque résultat de recherche expose désormais son photo_id et la vue download_archive vérifie que l'étudiant ne peut télécharger que les photos où son visage est associé à son compte (avec .distinct() pour éviter les doublons), puis j'ai ajouté un test unitaire qui ouvre le ZIP généré pour vérifier son contenu et le contrôle d'accès (13 tests qui passent).

## 25 / 11 / 2026
J'ai poussé le regroupement automatique des visages en personnes anonymes (T6 / F3) et fermé les issues terminées (#4, #8 et #11).

Suite au retour d'Amandine sur l'issue #12 (YuNet ne détectait aucun visage sur les grandes photos de smartphone au-dessus de 1600 px), j'ai ajouté une fonction resize_image_if_needed dans indexing/faces.py qui réduit les images dépassant 1600 px avant la détection YuNet, puis remet les coordonnées des boîtes et des points clés à l'échelle d'origine. Cela corrige automatiquement l'indexation et la recherche sans modifier le reste du code, et un nouveau test unitaire vérifie la détection sur une image de 3000 px (15 tests au total).

J'ai ensuite fait un audit du projet par rapport à la grille de notation et corrigé plusieurs points de performance et de qualité : mise en cache du modèle SFace (37 Mo) avec @lru_cache dans indexing/faces.py pour éviter de le recharger à chaque visage (ce qui réduit le temps des 15 tests de 28 s à 20 s), suppression des requêtes N+1 dans Face.__str__ (self.photo_id) et dans indexing/admin.py via list_select_related, puis nettoyage de .gitignore, Dockerfile, compose.yaml et formatage de manage.py. J'ai également fermé l'issue #9 (couverte par /admin/ et /indexing/) et ouvert l'issue #17 pour qu'Amandine ajoute HTMX côté front.

J'ai enfin mis en place le backend des notifications en temps réel (T11 / F8) avec Django Channels, Daphne et channels-redis : remplacement de Gunicorn par Daphne (ASGI) dans le Dockerfile, ajout des en-têtes WebSocket dans Nginx, création du consumer NotificationConsumer sur /ws/notifications/ et envoi automatique d'une notification sur le groupe user_<id> depuis la tâche Celery index_photo dès qu'une nouvelle photo d'un étudiant est indexée (testé sous Docker avec Redis).

## 26 / 11 / 2026
J'ai ajouté deux tests unitaires pour le consumer WebSocket NotificationConsumer dans search/tests.py afin de vérifier le refus des utilisateurs anonymes et la réception des notifications pour un utilisateur authentifié (17 tests au total), puis mis à jour le README pour documenter Daphne, les WebSockets et les pages d'erreur.

En vue de la soutenance blanche du lendemain, j'ai déroulé un test complet de bout en bout sur la stack Docker (Nginx, Daphne, PostgreSQL, Redis et les deux workers Celery) : refus d'une adresse non académique, création d'un compte étudiant, blocage en 403 sur /indexing/ et refus sur /admin/, recherche faciale en moins d'une seconde, téléchargement en archive ZIP et retrait RGPD. Ce test en conditions réelles a permis de détecter une faute de frappe dans assign_person (regognizer au lieu de recognizer dans indexing/faces.py) qui faisait échouer le worker d'indexation dès qu'un visage existait déjà en base. J'ai corrigé le bug et complété le test PersonClusteringTest dans indexing/tests.py pour qu'il exécute réellement index_photo et vérifie le regroupement en 3 personnes anonymes sur 5 visages.
