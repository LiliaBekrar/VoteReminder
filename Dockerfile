# Utiliser une image de base avec Python
FROM python:3.10-slim

# Mettre à jour les paquets et installer les dépendances nécessaires, y compris les outils de compilation
RUN apt-get update && apt-get install -y \
    pkg-config \
    libcairo2 \
    libcairo2-dev \
    gcc \
    g++ \
    make \
    meson \
    && rm -rf /var/lib/apt/lists/*

# Copier tous les fichiers du projet dans le répertoire courant
COPY . /app

# Se déplacer dans le répertoire de l'application
WORKDIR /app

# Mettre à jour pip pour éviter des problèmes avec la version actuelle
RUN pip install --upgrade pip

# Installer Cython et PyYAML avant les autres dépendances
RUN pip install Cython==3.0.0
RUN pip install PyYAML==5.4.1

# Installer les autres dépendances de Python
RUN pip install --no-cache-dir -r requirements.txt

# Commande pour démarrer l'application
CMD ["python", "bot.py"]
