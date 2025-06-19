# 📩 VoteReminder — Le bot Discord pour ne plus oublier de voter !

![Banner](https://raw.githubusercontent.com/LiliaBekrar/VoteReminder/main/assets/banner.png)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/o3aVuv?referralCode=your-code-here)
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Discord](https://img.shields.io/badge/Discord%20Bot-ready-5865F2?logo=discord)
![License](https://img.shields.io/github/license/LiliaBekrar/VoteReminder)
![Made with ❤️](https://img.shields.io/badge/Made%20with-Love-red)

VoteReminder est un bot Discord développé en Python, conçu pour envoyer des **rappels privés** automatisés à vos membres afin qu’ils n’oublient pas de voter.  
Il est **facile à configurer**, **personnalisable**, et **prêt à être déployé en quelques clics sur Railway**.

---

## 🧠 Fonctionnalités

- 🔔 Rappels privés à l'heure de votre choix
- ✅ Boutons interactifs :
  - *J’ai voté* → repousse de 1h30
  - *Repousser* → personnalisable
  - *Voter* → redirige vers un lien de vote
- ⏰ Système de postponement avec commandes slash
- 🧠 Stockage PostgreSQL (Railway) ou SQLite (local)
- 🌠 Avertissement automatique de météore dans un salon Discord (optionnel)

---

## 💬 Commandes disponibles

| Commande          | Description                                                   |
|-------------------|---------------------------------------------------------------|
| `?start HH:MM`     | Définir l’heure du rappel quotidien                          |
| `?next`            | Afficher la prochaine heure de rappel                        |
| `?repousser délai` | Repousse le rappel (`1h`, `15m`, `1h30`, etc.)               |
| `?voter`           | Confirme le vote et programme un rappel dans 90 min         |
| `?stop`            | Supprime votre inscription                                   |
| `?aide`            | Affiche la liste des commandes                               |

---

## 🚀 Déployer ce bot sur Railway

### Étape 1 — Créer un compte Railway

1. Va sur [https://railway.app](https://railway.app)
2. Clique sur **"Sign in with GitHub"**
3. Autorise Railway à accéder à tes repos

---

### Étape 2 — Forker ce dépôt

1. Clique sur **Fork** (en haut à droite de ce dépôt)  
2. Crée ton propre dépôt sur ton compte GitHub

---

### Étape 3 — Créer un projet Railway

1. Sur Railway, clique sur **"New Project"**
2. Choisis **"Deploy from GitHub Repo"**
3. Sélectionne ton fork du projet `VoteReminder`

---

### Étape 4 — Ajouter les variables d’environnement

Une fois le projet lancé, va dans **l’onglet "Variables"** et ajoute :

| Clé               | Valeur                                                    |
|-------------------|------------------------------------------------------------|
| `DISCORD_TOKEN`   | Ton token Discord (nécessaire)                             |
| `DATABASE_URL`    | *(optionnel)* URL PostgreSQL (Railway l’ajoute si DB liée) |
| `METEOR_CHANNEL_ID` | *(optionnel)* ID du canal pour les alertes météores     |

> ⚠️ Ces infos sont confidentielles. Ne les commits jamais dans GitHub.

---

### Étape 5 — (Facultatif) Ajouter une base PostgreSQL

1. Dans Railway, clique sur **"New" > "Database" > "PostgreSQL"**
2. Attends que la base soit prête
3. Va dans l’onglet "Connect", copie la variable `DATABASE_URL`
4. Colle-la dans ton projet Railway, onglet **Variables**

---

### Étape 6 — Lancer et vérifier

Railway détecte automatiquement le `Dockerfile` et lance le bot :  
Tu verras dans les logs :

```
Bot connecté en tant que VoteReminder#1234
```

✅ Ton bot est en ligne, fonctionne 24h/24, et est prêt à envoyer ses rappels !

---

## ⚙️ Utilisation locale (pour développeurs)

```bash
git clone https://github.com/TON_COMPTE/VoteReminder.git
cd VoteReminder

# Copier le fichier d’exemple
cp .env.example .env

# Modifier le fichier .env avec vos variables
nano .env

# Installer les dépendances
pip install -r requirements.txt

# Lancer le bot
python main.py
```

---

## 📁 Exemple de `.env.example`

```env
DISCORD_TOKEN=your_discord_token_here
DATABASE_URL=optional_if_you_use_postgres
METEOR_CHANNEL_ID=optional_channel_id_for_meteors
```

📌 Ajoute ce fichier dans ton dépôt (mais **jamais le vrai `.env`**)

---

## 🛠️ Stack technique

- Python 3.10
- discord.py
- SQLAlchemy
- apscheduler
- Docker
- Railway

---

## ❤️ À propos

> Ce bot a été créé par Lilia pour ses amis…  
> Et il est maintenant prêt à servir n’importe quel serveur Discord 🥰  
> Simple, fonctionnel, et fait avec amour.

👉 [github.com/LiliaBekrar](https://github.com/LiliaBekrar)

---

## 📌 Notes finales

- 🔗 Le lien de vote est défini dans le code (`PersistentReminderView`)
- ❤️ Un message spécial est réservé à l’utilisateur ID `490423881392455691`

---
