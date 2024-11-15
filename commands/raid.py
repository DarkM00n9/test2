from discord.ext import commands
import asyncio

from utils import log, lang, generate_random_string, random_cooldown
import config_selfbot


class RaidCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="renameallchannels", aliases=["rac"])
    async def renameallchannels(self, ctx: commands.Context):
        if ctx.author.guild_permissions.manage_channels:
            guild = ctx.guild
            new_name = ctx.message.content.replace(f"{ctx.invoked_with} ", "").strip()

            if not new_name:
                await ctx.message.edit(lang.text('rename_all_no_name'), delete_after=config_selfbot.deltime)
                return

            await ctx.message.edit(lang.text('rename_all_in_progress').format(guild_name=guild.name))

            log.separate_text("RENAME ALL CHANNELS")

            for channel in guild.text_channels:
                try:
                    await channel.edit(name=new_name)
                    log.success(f"Renamed #{channel.name} to #{new_name}")
                    await asyncio.sleep(random_cooldown(0.4, 1.1))
                except Exception as e:
                    log.error(f"Failed to rename #{channel.name}: {e}")

            log.separate_text("RENAME ALL CHANNELS COMPLETED")
            await ctx.message.edit(lang.text('rename_all_success').format(guild_name=guild.name), delete_after=config_selfbot.deltime)
        else:
            await ctx.message.edit(lang.text('raid_error_permisssion'), delete_after=config_selfbot.deltime)
