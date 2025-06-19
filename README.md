# 📩 VoteReminder — Le bot Discord pour ne plus oublier de voter !

![Banner](https://raw.githubusercontent.com/LiliaBekrar/VoteReminder/master/assets/banner.png)

VoteReminder est un petit bot Discord développé en Python et déployé sur Railway.  
Il a été conçu pour mes amis qui oubliaient régulièrement de voter sur une application.  
Résultat : un bot simple et efficace qui envoie des **rappels personnalisés** en DM avec des **boutons interactifs**.

---

## 🚀 Déploiement rapide

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/o3aVuv?referralCode=your-code-here)

---

## 🧠 Fonctionnalités

- 🔔 Envoie automatique de rappels Discord en message privé
- ✅ Boutons interactifs :
  - *J’ai voté* → repousse le rappel de 1h30
  - *Repousser* → relance le rappel dans 1h30 (ou plus via commande)
- 🧾 Commandes slash pour activer/désactiver les rappels
- 💾 Stockage des préférences utilisateurs
- 🐍 Codé en Python et hébergé sur Railway

---

## 🛠️ Stack technique

- **Python 3.10**
- **discord.py**
- **python-dotenv**
- **apscheduler**
- **Railway**

---

## 💬 Commandes disponibles

| Slash Commande | Description                            |
|----------------|----------------------------------------|
| `/rappel`      | Active les rappels automatiques        |
| `/repousser`   | Définit un délai personnalisé          |
| `/stop`        | Supprime l’utilisateur de la liste     |

---

## ⚙️ Installation manuelle

### En local

```bash
# Cloner le dépôt
git clone https://github.com/LiliaBekrar/VoteReminder.git
cd VoteReminder

# Copier le fichier d'environnement
cp .env.example .env

# Installer les dépendances Python
pip install -r requirements.txt

# Lancer le bot
python main.py
```

---

## ❤️ À propos

> J’en avais marre que mes potes oublient de voter sur une appli.  
> Alors j’ai décidé de coder un petit bot utile, fun, rapide à déployer.  
> Résultat : **VoteReminder est né** 🎉

Ce projet est né d’un besoin très concret dans mon cercle d’amis,  
mais il peut facilement s’adapter à n’importe quelle communauté ou serveur Discord qui a besoin d’un rappel régulier et personnalisable.

---

Développé avec 💖 par [Lilia](https://github.com/LiliaBekrar)

---
