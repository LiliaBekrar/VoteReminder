import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import os
import re

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True  # Pour lire le contenu des messages
intents.members = True          # Pour accéder aux informations des membres

bot = commands.Bot(command_prefix="?", intents=intents)

# Fonction pour charger les données utilisateur depuis un fichier JSON
def load_user_data():
    if os.path.exists("user_data.json"):
        try:
            with open("user_data.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Erreur : user_data.json est corrompu. Réinitialisation des données.")
            return {}
    else:
        return {}

# Fonction pour sauvegarder les données utilisateur dans un fichier JSON
def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f, indent=4)
    print("Données des utilisateurs sauvegardées.")

# Fonction qui calcule le prochain rappel quotidien à partir du rappel_quotidien (format "HH:MM")
def calculate_daily_reminder(daily_str):
    now = datetime.now()
    try:
        daily_time = datetime.strptime(daily_str, "%H:%M").time()
    except ValueError:
        raise ValueError("Format d'heure invalide pour le rappel quotidien. Utilisez HH:MM.")
    new_reminder = datetime.combine(now.date(), daily_time)
    if new_reminder <= now:
        new_reminder += timedelta(days=1)
    return new_reminder

# Données utilisateur globales
user_data = load_user_data()

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    reminder_loop.start()
    print("La boucle de rappels a démarré.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Commande inconnue. Tapez `?aide` pour la liste des commandes disponibles.")
        print(f"Commande inconnue reçue de {ctx.author.name} ({ctx.author.id}).")
    else:
        print(f"Erreur : {error}")
        await ctx.send(f"Une erreur est survenue : {error}")

@bot.command()
async def start(ctx, time_str: str):
    """
    Inscrit un utilisateur avec un rappel quotidien à l'heure spécifiée.
    Formats acceptés : "12:45", "1h40", "2h", "1h45mn", etc.
    Si l'heure n'est pas encore passée aujourd'hui, next_reminder est aujourd'hui à cette heure ; sinon demain.
    """
    user_id = str(ctx.author.id)
    print(f"Commande start reçue de {ctx.author.name} ({user_id}) avec l'heure : {time_str}")
    try:
        # Validation du format "HH:MM"
        datetime.strptime(time_str, "%H:%M")
        next_reminder = calculate_daily_reminder(time_str)
        user_data[user_id] = {
            "rappel_quotidien": time_str,  # Stocke l'heure quotidienne sous forme de chaîne
            "next_reminder": next_reminder.strftime("%Y-%m-%d %H:%M:%S"),
            "postpone_time": 90  # Délai par défaut de 90 minutes
        }
        save_user_data()
        await ctx.send(f"{ctx.author.name}, vous avez été inscrit avec succès ! Votre rappel quotidien est fixé à {time_str}.\nVotre prochain rappel est prévu pour {next_reminder.strftime('%H:%M:%S')}.")
        print(f"{ctx.author.name} ({user_id}) inscrit pour rappel quotidien à {time_str}. Next reminder: {next_reminder.strftime('%Y-%m-%d %H:%M:%S')}")
    except ValueError as e:
        await ctx.send("Format d'heure invalide. Utilisez `?start HH:MM`.")
        print(f"Erreur dans la commande start de {ctx.author.name} ({user_id}) : {str(e)}")

@bot.command()
async def next(ctx):
    """Affiche l'heure du prochain rappel pour l'utilisateur."""
    user_id = str(ctx.author.id)
    if user_id in user_data:
        nr = datetime.strptime(user_data[user_id]["next_reminder"], "%Y-%m-%d %H:%M:%S")
        await ctx.send(f"{ctx.author.name}, votre prochain rappel est prévu pour : {nr.strftime('%H:%M:%S')}.")
        print(f"!next: {ctx.author.name} ({user_id}) -> {nr.strftime('%H:%M:%S')}")
    else:
        await ctx.send("Vous n'êtes pas inscrit pour des rappels. Utilisez la commande `?start HH:MM` pour vous inscrire.")
        print(f"!next: {ctx.author.name} ({user_id}) non inscrit.")

@bot.command()
async def stop(ctx):
    """Désinscrit l'utilisateur et annule ses rappels."""
    user_id = str(ctx.author.id)
    if user_id in user_data:
        del user_data[user_id]
        save_user_data()
        await ctx.send("Votre inscription a été supprimée et vous ne recevrez plus de rappels.")
        print(f"{ctx.author.name} ({user_id}) a été supprimé des rappels.")
    else:
        await ctx.send("Vous n'êtes pas inscrit pour des rappels.")
        print(f"{ctx.author.name} ({user_id}) a tenté de se désinscrire sans être inscrit.")

@bot.command()
async def repousser(ctx, delay: str):
    """
    Repousse le rappel actuel de l'utilisateur d'un délai spécifié.
    Formats acceptés : "12:45", "1h40", "2h", "3m", "3mn", "1h40m", "1h45mn", etc.
    Pour ?repousser, le délai est ajouté à l'instant présent.
    """
    user_id = str(ctx.author.id)
    if user_id not in user_data:
        await ctx.send("Vous n'êtes pas inscrit pour des rappels. Utilisez `?start HH:MM` pour vous inscrire.")
        print(f"{ctx.author.name} ({user_id}) a tenté de repousser sans inscription.")
        return
    try:
        # Utilisation d'une fonction de parsing flexible pour le délai
        delay_td = parse_delay(delay)
        new_nr = datetime.now() + delay_td
        user_data[user_id]["next_reminder"] = new_nr.strftime("%Y-%m-%d %H:%M:%S")
        save_user_data()
        await ctx.send(f"Votre rappel a été repoussé à : {new_nr.strftime('%H:%M:%S')}.")
        print(f"{ctx.author.name} ({user_id}) a repoussé son rappel à {new_nr.strftime('%Y-%m-%d %H:%M:%S')}.")
    except ValueError as e:
        await ctx.send(str(e))
        print(f"Erreur dans !repousser pour {ctx.author.name} ({user_id}) : {str(e)}")

def parse_delay(delay_str: str) -> timedelta:
    """
    Parse un délai depuis une chaîne. Accepté :
      - Format HH:MM (ex: "12:45")
      - Format HhMm ou HhMm(n) (ex: "1h40", "1h45mn")
      - Format Hh (ex: "2h")
      - Format M ou Mn (ex: "3m", "3mn")
    Retourne un objet timedelta.
    """
    delay_str = delay_str.strip()
    # Format HH:MM
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", delay_str)
    if m:
        return timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
    # Format HhMm ou HhMm(n)
    m = re.fullmatch(r"(\d{1,2})h(\d{1,2})(?:m|mn)?", delay_str)
    if m:
        return timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
    # Format Hh
    m = re.fullmatch(r"(\d{1,2})h", delay_str)
    if m:
        return timedelta(hours=int(m.group(1)))
    # Format M ou Mn
    m = re.fullmatch(r"(\d{1,2})(?:m|mn)", delay_str)
    if m:
        return timedelta(minutes=int(m.group(1)))
    raise ValueError("Format de délai invalide. Utilisez par exemple '1h30', '3m', '12:45', etc.")

@bot.command()
async def voter(ctx):
    """
    Marque le rappel comme effectué et planifie un rappel temporaire dans 90 minutes.
    Ce délai temporaire est utilisé si l'utilisateur interagit avec le rappel.
    """
    user_id = str(ctx.author.id)
    if user_id not in user_data:
        await ctx.send("Vous n'êtes pas inscrit pour des rappels. Utilisez `?start HH:MM` pour vous inscrire.")
        print(f"{ctx.author.name} ({user_id}) a tenté de voter sans inscription.")
        return
    new_nr = datetime.now() + timedelta(minutes=90)
    user_data[user_id]["next_reminder"] = new_nr.strftime("%Y-%m-%d %H:%M:%S")
    save_user_data()
    await ctx.send(f"Merci d'avoir voté ! Votre prochain rappel est prévu pour {new_nr.strftime('%H:%M:%S')}.")
    print(f"{ctx.author.name} ({user_id}) a voté. Next reminder: {new_nr.strftime('%Y-%m-%d %H:%M:%S')}.")

@bot.command()
async def aide(ctx):
    """Affiche la liste des commandes disponibles."""
    help_message = (
        "Commandes disponibles :\n"
        "`?start HH:MM` - Inscrit ou modifie votre rappel quotidien (formats acceptés : 12:45, 1h40, 2h, 1h45mn, etc.).\n"
        "`?next` - Affiche l'heure du prochain rappel.\n"
        "`?repousser <temps>` - Repousse le rappel actuel d'un délai spécifié (ex: ?repousser 1h30, ?repousser 3m).\n"
        "`?voter` - Marque le rappel comme effectué et planifie un rappel dans 90 minutes.\n"
        "`?stop` - Désinscrit et annule vos rappels.\n"
        "`?aide` - Affiche ce message d'aide."
    )
    await ctx.send(help_message)
    print(f"Message d'aide envoyé à {ctx.author.name} ({ctx.author.id}).")

# Boucle de rappel qui vérifie toutes les minutes si un rappel doit être envoyé
@tasks.loop(minutes=1)
async def reminder_loop():
    now = datetime.now()
    for user_id, data in user_data.items():
        nr = datetime.strptime(data["next_reminder"], "%Y-%m-%d %H:%M:%S")
        if now >= nr:
            user = await bot.fetch_user(user_id)
            if user:
                print(f"Envoi du rappel à {user.name} ({user_id})")
                view = View()
                vote_button = Button(label="Voter", url="https://nationsglory.fr/vote", style=discord.ButtonStyle.link)
                voted_button = Button(label="J'ai voté", style=discord.ButtonStyle.success)
                postpone_button = Button(label="Repousser", style=discord.ButtonStyle.secondary)

                async def voted_callback(interaction):
                    if interaction.user.id == int(user_id):
                        new_nr = datetime.now() + timedelta(minutes=90)
                        user_data[user_id]["next_reminder"] = new_nr.strftime("%Y-%m-%d %H:%M:%S")
                        save_user_data()
                        await interaction.response.send_message("✅ Prochain rappel dans 1h30.", ephemeral=True)
                        print(f"{user.name} a cliqué sur 'J'ai voté'. Nouveau rappel à {new_nr.strftime('%H:%M:%S')}.")

                async def postpone_callback(interaction):
                    if interaction.user.id == int(user_id):
                        postpone_time = data.get("postpone_time", 90)
                        new_nr = datetime.now() + timedelta(minutes=postpone_time)
                        user_data[user_id]["next_reminder"] = new_nr.strftime("%Y-%m-%d %H:%M:%S")
                        save_user_data()
                        await interaction.response.send_message(f"🔔 Prochain rappel dans {postpone_time} minutes.", ephemeral=True)
                        print(f"{user.name} a cliqué sur 'Repousser'. Nouveau rappel à {new_nr.strftime('%H:%M:%S')}.")

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
                # Easter egg pour l'ID spécifique
                if user_id == "490423881392455691":
                    reminder_message += "\n\n❤️ Et n'oublie pas aussi que je t'aime, signée ta bibouche."

                try:
                    await user.send(reminder_message, view=view)
                    print(f"Rappel envoyé à {user.name}.")
                except Exception as e:
                    print(f"Erreur lors de l'envoi du rappel à {user.name} : {str(e)}")

                # Réinitialiser le rappel quotidien basé sur l'heure définie
                daily_str = data["rappel_quotidien"]
                new_daily = calculate_daily_reminder(daily_str)
                user_data[user_id]["next_reminder"] = new_daily.strftime("%Y-%m-%d %H:%M:%S")
                save_user_data()
                print(f"Rappel quotidien réinitialisé pour {user.name} à {new_daily.strftime('%H:%M:%S')}.")

load_dotenv()  # Charge les variables d'environnement à partir du fichier .env
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
