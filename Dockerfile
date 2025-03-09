# Utiliser une image Python comme base
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 8080 (nécessaire pour Google Cloud Run)
EXPOSE 8080

# Définir la commande de démarrage
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]

