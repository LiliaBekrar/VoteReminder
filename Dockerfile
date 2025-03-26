# Utiliser une image de base avec Python
FROM python:3.10-slim

# Mettre à jour les paquets et installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    pkg-config \
    libcairo2 \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de ton projet dans le répertoire courant
COPY . /app

# Se déplacer dans le répertoire de l'application (qui sera /app)
WORKDIR /app

# Installer les dépendances de Python
RUN pip install --no-cache-dir -r requirements.txt

# Commande pour démarrer l'application
CMD ["python", "app.py"]
