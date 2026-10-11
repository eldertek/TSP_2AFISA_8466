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