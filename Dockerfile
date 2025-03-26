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
    libsystemd-dev \  # Ajoute la bibliothèque manquante
    && rm -rf /var/lib/apt/lists/*

# Copier tous les fichiers du projet dans le répertoire courant
COPY . /app

# Se déplacer dans le répertoire de l'application
WORKDIR /app

# Mettre à jour pip, setuptools, et wheel pour éviter des problèmes avec la version actuelle
RUN pip install --upgrade pip setuptools wheel

# Installer Cython (version inférieure à 3.0.0) et PyYAML sans isolation de build
RUN pip install "cython<3.0.0"
RUN pip install --no-build-isolation pyyaml==5.4.1

# Installer les autres dépendances de Python
RUN pip install --no-cache-dir -r requirements.txt

# Commande pour démarrer l'application
CMD ["python", "bot.py"]
