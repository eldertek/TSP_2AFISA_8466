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
