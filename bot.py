import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import re
import pytz
import logging
import sys

# SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuration du logging pour Railway : envoyer les logs sur stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  # Envoie directement sur stdout
)

# Définition du fuseau horaire français
PARIS_TZ = pytz.timezone("Europe/Paris")

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
# Si DATABASE_URL est défini, on l'utilise (pour PostgreSQL sur Railway), sinon on utilise SQLite en local.
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    logging.info("Utilisation de la base de données PostgreSQL.")
else:
    engine = create_engine("sqlite:///user_data.db", connect_args={"check_same_thread": False})
    logging.info("Utilisation de SQLite en local.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Définition du modèle utilisateur
class UserData(Base):
    __tablename__ = "user_data"
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, index=True)
    rappel_quotidien = Column(String)
    next_reminder = Column(DateTime)
    postpone_time = Column(Integer, default=90)

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# Configuration des intents Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents)

# Fonctions d'accès à la base de données
def get_user(session, discord_id: str):
    return session.query(UserData).filter(UserData.discord_id == discord_id).first()

def create_or_update_user(discord_id: str, daily_time: str, next_reminder: datetime, postpone_time: int = 90):
    session = SessionLocal()
    user = get_user(session, discord_id)
    if user:
        user.rappel_quotidien = daily_time
        user.next_reminder = next_reminder
        user.postpone_time = postpone_time
    else:
        user = UserData(
            discord_id=discord_id,
            rappel_quotidien=daily_time,
            next_reminder=next_reminder,
            postpone_time=postpone_time
        )
        session.add(user)
    session.commit()
    session.close()
    logging.info(f"Enregistrement mis à jour pour l'utilisateur {discord_id}")

def delete_user(discord_id: str):
    session = SessionLocal()
    user = get_user(session, discord_id)
    if user:
        session.delete(user)
        session.commit()
        logging.info(f"Utilisateur {discord_id} supprimé de la base de données.")
    session.close()

# Fonction qui calcule le prochain rappel quotidien en fonction de l'heure française
def calculate_daily_reminder(daily_str):
    now = datetime.now(PARIS_TZ)
    try:
        daily_time = datetime.strptime(daily_str, "%H:%M").time()
    except ValueError:
        raise ValueError("Format d'heure invalide pour le rappel quotidien. Utilisez HH:MM.")
    new_reminder = datetime.combine(now.date(), daily_time)
    new_reminder = PARIS_TZ.localize(new_reminder)
    if new_reminder <= now:
        new_reminder += timedelta(days=1)
    return new_reminder

# Commande de démarrage : inscription de l'utilisateur avec un rappel quotidien
@bot.command()
async def start(ctx, time_str: str):
    user_id = str(ctx.author.id)
    logging.info(f"Commande start reçue de {ctx.author.name} ({user_id}) avec l'heure : {time_str}")
    try:
        datetime.strptime(time_str, "%H:%M")  # Validation du format
        next_reminder = calculate_daily_reminder(time_str)
        create_or_update_user(user_id, time_str, next_reminder)
        await ctx.send(f"{ctx.author.name}, vous avez été inscrit avec succès ! Votre rappel quotidien est fixé à {time_str}.\nVotre prochain rappel est prévu pour {next_reminder.strftime('%H:%M:%S')}.")
    except ValueError as e:
        await ctx.send("Format d'heure invalide. Utilisez `?start HH:MM`.")
        logging.error(f"Erreur dans start pour {ctx.author.name} ({user_id}): {e}")

# Commande pour afficher le prochain rappel
@bot.command()
async def next(ctx):
    user_id = str(ctx.author.id)
    session = SessionLocal()
    user = get_user(session, user_id)
    if user:
        nr = user.next_reminder.astimezone(PARIS_TZ)
        await ctx.send(f"{ctx.author.name}, votre prochain rappel est prévu pour : {nr.strftime('%H:%M:%S')} (heure de Paris).")
        logging.info(f"!next: {ctx.author.name} ({user_id}) -> {nr.strftime('%H:%M:%S')}")
    else:
        await ctx.send("Vous n'êtes pas inscrit pour des rappels. Utilisez `?start HH:MM` pour vous inscrire.")
        logging.info(f"!next: {ctx.author.name} ({user_id}) non inscrit.")
    session.close()

# Commande pour se désinscrire
@bot.command()
async def stop(ctx):
    user_id = str(ctx.author.id)
    delete_user(user_id)
    await ctx.send("Votre inscription a été supprimée et vous ne recevrez plus de rappels.")

# Commande pour repousser le rappel
@bot.command()
async def repousser(ctx, delay: str):
    user_id = str(ctx.author.id)
    session = SessionLocal()
    user = get_user(session, user_id)
    if not user:
        await ctx.send("Vous n'êtes pas inscrit pour des rappels. Utilisez `?start HH:MM` pour vous inscrire.")
        logging.info(f"{ctx.author.name} ({user_id}) a tenté de repousser sans inscription.")
        session.close()
        return
    try:
        delay_td = parse_delay(delay)
        new_nr = datetime.now(PARIS_TZ) + delay_td
        user.next_reminder = new_nr
        session.commit()
        await ctx.send(f"Votre rappel a été repoussé à : {new_nr.strftime('%H:%M:%S')}.")
        logging.info(f"{ctx.author.name} ({user_id}) a repoussé son rappel à {new_nr.strftime('%Y-%m-%d %H:%M:%S')}.")
    except ValueError as e:
        await ctx.send(str(e))
        logging.error(f"Erreur dans repousser pour {ctx.author.name} ({user_id}): {e}")
    session.close()

# Fonction de parsing pour le délai
def parse_delay(delay_str: str) -> timedelta:
    delay_str = delay_str.strip()
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", delay_str)
    if m:
        return timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
    m = re.fullmatch(r"(\d{1,2})h(\d{1,2})(?:m|mn)?", delay_str)
    if m:
        return timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
    m = re.fullmatch(r"(\d{1,2})h", delay_str)
    if m:
        return timedelta(hours=int(m.group(1)))
    m = re.fullmatch(r"(\d{1,2})(?:m|mn)", delay_str)
    if m:
        return timedelta(minutes=int(m.group(1)))
    raise ValueError("Format de délai invalide. Utilisez par exemple '1h30', '3m', '12:45', etc.")

# Commande pour marquer le rappel comme effectué et programmer un rappel dans 90 minutes
@bot.command()
async def voter(ctx):
    user_id = str(ctx.author.id)
    session = SessionLocal()
    user = get_user(session, user_id)
    if not user:
        await ctx.send("Vous n'êtes pas inscrit pour des rappels. Utilisez `?start HH:MM` pour vous inscrire.")
        logging.info(f"{ctx.author.name} ({user_id}) a tenté de voter sans inscription.")
        session.close()
        return
    new_nr = datetime.now(PARIS_TZ) + timedelta(minutes=90)
    user.next_reminder = new_nr
    session.commit()
    await ctx.send(f"Merci d'avoir voté ! Votre prochain rappel est prévu pour {new_nr.strftime('%H:%M:%S')}.")
    logging.info(f"{ctx.author.name} ({user_id}) a voté. Next reminder: {new_nr.strftime('%Y-%m-%d %H:%M:%S')}.")
    session.close()

# Commande d'aide
@bot.command()
async def aide(ctx):
    help_message = (
        "Commandes disponibles :\n"
        "`?start HH:MM` - Inscrit ou modifie votre rappel quotidien (formats acceptés : 12:45, 1h40, etc.).\n"
        "`?next` - Affiche l'heure du prochain rappel.\n"
        "`?repousser <temps>` - Repousse le rappel actuel d'un délai spécifié.\n"
        "`?voter` - Marque le rappel comme effectué et planifie un rappel dans 90 minutes.\n"
        "`?stop` - Désinscrit et annule vos rappels.\n"
        "`?aide` - Affiche ce message d'aide."
    )
    await ctx.send(help_message)
    logging.info(f"Message d'aide envoyé à {ctx.author.name} ({ctx.author.id}).")

# Boucle de rappel qui vérifie toutes les minutes si un rappel doit être envoyé
@tasks.loop(minutes=1)
async def reminder_loop():
    now = datetime.now(PARIS_TZ)
    session = SessionLocal()
    users = session.query(UserData).all()
    for user in users:
        nr = user.next_reminder.astimezone(PARIS_TZ)
        if now >= nr:
            discord_user = await bot.fetch_user(user.discord_id)
            if discord_user:
                logging.info(f"Envoi du rappel à {discord_user.name} ({user.discord_id})")
                view = View()
                vote_button = Button(label="Voter", url="https://nationsglory.fr/vote", style=discord.ButtonStyle.link)
                voted_button = Button(label="J'ai voté", style=discord.ButtonStyle.success)
                postpone_button = Button(label="Repousser", style=discord.ButtonStyle.secondary)

                async def voted_callback(interaction):
                    if interaction.user.id == int(user.discord_id):
                        new_nr = datetime.now(PARIS_TZ) + timedelta(minutes=90)
                        user.next_reminder = new_nr
                        session.commit()
                        await interaction.response.send_message("✅ Prochain rappel dans 1h30.", ephemeral=True)
                        logging.info(f"{discord_user.name} a cliqué sur 'J'ai voté'. Nouveau rappel à {new_nr.strftime('%H:%M:%S')}.")

                async def postpone_callback(interaction):
                    if interaction.user.id == int(user.discord_id):
                        postpone_time = user.postpone_time or 90
                        new_nr = datetime.now(PARIS_TZ) + timedelta(minutes=postpone_time)
                        user.next_reminder = new_nr
                        session.commit()
                        await interaction.response.send_message(f"🔔 Prochain rappel dans {postpone_time} minutes.", ephemeral=True)
                        logging.info(f"{discord_user.name} a cliqué sur 'Repousser'. Nouveau rappel à {new_nr.strftime('%H:%M:%S')}.")

                voted_button.callback = voted_callback
                postpone_button.callback = postpone_callback

                view.add_item(vote_button)
                view.add_item(voted_button)
                view.add_item(postpone_button)

                reminder_message = (
                    "🗳️ Il est temps de voter !\n\n"
                    "Le bouton 'Repousser' sert à reposer le rappel dans 1h30 par défaut.\n"
                    "Pour personnaliser ce délai, utilisez `?repousser <nombre>m` ou `?repousser <nombre>h`."
                )
                if user.discord_id == "490423881392455691":
                    reminder_message += "\n\n❤️ Et n'oublie pas aussi que je t'aime, signée ta bibouche."

                try:
                    await discord_user.send(reminder_message, view=view)
                    logging.info(f"Rappel envoyé à {discord_user.name}.")
                except Exception as e:
                    logging.error(f"Erreur lors de l'envoi du rappel à {discord_user.name} : {e}")

                # Réinitialiser le rappel quotidien basé sur l'heure définie
                new_daily = calculate_daily_reminder(user.rappel_quotidien)
                user.next_reminder = new_daily
                session.commit()
                logging.info(f"Rappel quotidien réinitialisé pour {discord_user.name} à {new_daily.strftime('%H:%M:%S')}.")
    session.close()

@bot.event
async def on_ready():
    logging.info(f"Bot connecté en tant que {bot.user}")
    reminder_loop.start()

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
