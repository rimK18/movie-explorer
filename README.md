🎬 Movie Explorer

📌 Description du projet

Movie Explorer est une application web permettant aux utilisateurs de rechercher des films en interrogeant une base de données BigQuery sur Google Cloud.

Elle offre une interface utilisateur interactive développée avec Streamlit, permettant d’effectuer des recherches avancées grâce à divers filtres :

✔️ Recherche par titre (avec autocomplétion)
✔️ Filtrage par langue
✔️ Filtrage par genre
✔️ Filtrage par note moyenne des spectateurs
✔️ Filtrage par année de sortie

Lorsque l’utilisateur sélectionne un film, l’application affiche des détails supplémentaires (synopsis, affiche, casting) grâce à l’API de The Movie Database (TMDB).

L’application est dockerisée et déployée sur Google Cloud Run, permettant un accès facile via une URL publique.

🚀 Lien vers l'application déployée

Service URL : https://movie-explorer-200462783381.europe-west6.run.app

L’application est hébergée sur Google Cloud Run et est accessible publiquement.

⚙️ Installation et Exécution en Local

🔧 Prérequis
Avant d'exécuter l'application localement, assurez-vous d’avoir installé :

✔️ Python 3.9+
✔️ Docker
✔️ Google Cloud SDK
✔️ Un projet Google Cloud avec BigQuery configuré

📥 Cloner le projet

sh
Copier
Modifier
git clone https://github.com/rimK18/movie-explorer.git
cd movie-explorer
📦 Installer les dépendances

sh
Copier
Modifier
pip install -r requirements.txt
🔑 Configurer les identifiants Google Cloud

Assurez-vous d’avoir un fichier d’authentification pour BigQuery et définissez la variable d’environnement correspondante :

sh
Copier
Modifier
export GOOGLE_APPLICATION_CREDENTIALS="bigquery-key.json"
▶️ Lancer l’application localement

sh
Copier
Modifier
streamlit run app.py
L’application sera accessible à l’adresse suivante :
➡️ http://localhost:8501

🐳 Exécution avec Docker

📦 Construire l’image Docker

sh
Copier
Modifier
docker build -t movie-explorer .
▶️ Exécuter le conteneur

sh
Copier
Modifier
docker run -p 8080:8080 movie-explorer
L’application sera accessible à l’adresse suivante :
➡️ http://localhost:8080

🚀 Déploiement sur Google Cloud Run

📤 Pousser l’image sur Google Container Registry

sh
Copier
Modifier
docker tag movie-explorer gcr.io/movie-project-453208/movie-explorer:latest
docker push gcr.io/movie-project-453208/movie-explorer:latest
🌍 Déployer sur Cloud Run

sh
Copier
Modifier
gcloud run deploy movie-explorer \
  --image gcr.io/movie-project-453208/movie-explorer:latest \
  --platform managed \
  --region europe-west6 \
  --allow-unauthenticated
L’application sera accessible via l’URL affichée après le déploiement.

🔍 Fonctionnalités Implémentées

✅ Autocomplétion des titres (SQL)
✅ Filtrage par langue (SQL)
✅ Filtrage par genre (SQL)
✅ Filtrage par moyenne des notes (SQL + jointure avec les avis)
✅ Filtrage par année de sortie (SQL)
✅ Affichage des résultats avec détails et affiches via TMDB
✅ Déploiement sur Google Cloud Run avec Docker

🛠 Technologies utilisées

BigQuery → Stockage des films et avis
Google Cloud Run → Déploiement de l’application
Streamlit → Interface utilisateur
Docker → Containerisation
Python & Pandas → Traitement des données
TMDB API → Récupération des détails des films
📝 Auteurs

📌 Projet réalisé par Karim Bellamri dans le cadre du cours Cloud & Advanced Analytics 2025.
