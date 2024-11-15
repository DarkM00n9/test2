from discord.ext import commands
import os, json, asyncio
from utils import log, lang, save_guild, load_guild, random_cooldown
import config_selfbot
import discord

class BackupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def save(self, ctx: commands.Context):
        """Sauvegarde les données d'un serveur, y compris les messages, dans un fichier JSON."""
        try:
            # Vérification si un ID de serveur est fourni
            guild_id = ctx.message.content.split()[1]
            guild = await self.bot.fetch_guild(int(guild_id), with_counts=False)
            await asyncio.sleep(random_cooldown(0.4, 2))  # Délai aléatoire
            guild_channels = await guild.fetch_channels()
        except IndexError:
            # Si aucun ID n'est fourni, utilise le serveur actuel
            guild = ctx.guild
            guild_channels = guild.channels
        except Exception as e:
            await ctx.message.edit(f"Erreur: {str(e)}", delete_after=config_selfbot.deltime)
            return

        backup_file = f"./backups/{guild.id}.json"

        # Vérification si un fichier de sauvegarde existe déjà
        if os.path.exists(backup_file):
            await ctx.message.edit(f"{lang.text('backup_save_already_exist')} {guild.name} {lang.text('backup_save_already_exist_two')}", delete_after=config_selfbot.deltime)
            return

        await ctx.message.edit(lang.text('backup_saving'))

        # Sauvegarde des données de serveur
        backup_data = {
            'guild': {
                'id': guild.id,
                'name': guild.name,
                'channels': []
            },
            'messages': []
        }

        # Collecte les informations des canaux
        for channel in guild_channels:
            if isinstance(channel, discord.TextChannel):
                # Sauvegarde des messages des canaux texte
                messages = []
                async for message in channel.history(limit=100):  # Limité à 100 messages par canal
                    messages.append({
                        'author': message.author.id,
                        'content': message.content,
                        'timestamp': message.created_at.isoformat()
                    })
                
                backup_data['guild']['channels'].append({
                    'id': channel.id,
                    'name': channel.name,
                    'messages': messages
                })
        
        # Sauvegarde dans un fichier JSON
        try:
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=4)
        except Exception as e:
            await ctx.message.edit(f"Erreur lors de la sauvegarde : {str(e)}", delete_after=config_selfbot.deltime)
            return

        await ctx.message.edit(f"{lang.text('backup_success_save')}: {guild.name}", delete_after=config_selfbot.deltime)
        log.success(f"Backup successfully saved for {guild.name}")

    @commands.command()
    async def backups(self, ctx: commands.Context):
        """Affiche la liste des sauvegardes disponibles."""
        backups_list = os.listdir("backups")
        if not backups_list:
            await ctx.message.edit(lang.text('no_backup_error'), delete_after=config_selfbot.deltime)
            return

        response = f"__**🗒️| {lang.text('backup_list')}**__\n"
        for backup_file in backups_list:
            try:
                with open(f"./backups/{backup_file}", "r") as f:
                    guild_info = json.load(f)
                    response += f"👥 {guild_info['name']} (🪪ID: `{guild_info['id']}`)\n"
            except Exception as e:
                log.error(f"Erreur de lecture de la sauvegarde {backup_file}: {str(e)}")
                continue

        await ctx.message.edit(response, delete_after=config_selfbot.deltime)

    @commands.command()
    async def load(self, ctx: commands.Context):
        """Charge une sauvegarde pour le serveur spécifié."""
        try:
            backup_id = ctx.message.content.split()[1]
        except IndexError:
            await ctx.message.edit(lang.text('backup_id_required'), delete_after=config_selfbot.deltime)
            return

        backup_file_path = f"./backups/{backup_id}.json"
        if not os.path.exists(backup_file_path):
            await ctx.message.edit(lang.text('backup_invalid'), delete_after=config_selfbot.deltime)
            return

        try:
            guild_id = ctx.message.content.split()[2]
            guild = await self.bot.fetch_guild(int(guild_id), with_counts=False)
            await asyncio.sleep(random_cooldown(0.4, 2))
            guild_channels = await guild.fetch_channels()
        except IndexError:
            # Si aucun ID de serveur n'est précisé, on utilise le serveur actuel
            guild = ctx.guild
            guild_channels = guild.channels
        except Exception as e:
            await ctx.message.edit(f"Erreur: {str(e)}", delete_after=config_selfbot.deltime)
            return

        # Vérification des permissions avant de charger la sauvegarde
        if not guild.me.guild_permissions.administrator:
            await ctx.message.edit(lang.text('backup_no_permissions'), delete_after=config_selfbot.deltime)
            return

        with open(backup_file_path, "r") as f:
            backup = json.load(f)

        await ctx.message.edit(lang.text('backup_loading'))

        try:
            await load_guild(guild, guild_channels, backup, 0.8, 25.6)
            await ctx.message.edit(lang.text('backup_done'))
            log.success(f"Restaurée: {backup_file_path}")
        except discord.errors.NotFound:
            log.error(f"Erreur: Un ou plusieurs éléments de la sauvegarde n'ont pas pu être trouvés.")
            await ctx.message.edit(lang.text('backup_loading_error'), delete_after=config_selfbot.deltime)

    @commands.command()
    async def delete(self, ctx: commands.Context):
        """Supprime une sauvegarde existante."""
        try:
            backup_id = ctx.message.content.split()[1]
        except IndexError:
            await ctx.message.edit(lang.text('backup_id_required'), delete_after=config_selfbot.deltime)
            return

        backup_file_path = f"./backups/{backup_id}.json"
        if not os.path.exists(backup_file_path):
            await ctx.message.edit(lang.text('backup_invalid'), delete_after=config_selfbot.deltime)
            return

        # Lecture du fichier de sauvegarde
        with open(backup_file_path, "r") as f:
            guild_info = json.load(f)

        # Suppression du fichier de sauvegarde
        os.remove(backup_file_path)
        await ctx.message.edit(f"{guild_info['name']}: {lang.text('backup_delete_done')}", delete_after=config_selfbot.deltime)
        log.success(f"Suppression de la sauvegarde: {backup_file_path}")
