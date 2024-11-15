import discord
from rich.console import Console

console = Console()

async def set_presence(bot, activity_type, name, url=None):
    activity = None

    if activity_type.lower() == "playing":
        activity = discord.Game(name=name)
    elif activity_type.lower() == "streaming":
        if url is None:
            console.print("[red]URL is required for streaming presence.[/red]")
            return
        activity = discord.Streaming(name=name, url=url)
    elif activity_type.lower() == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=name)
    elif activity_type.lower() == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=name)
    else:
        console.print("[red]Invalid activity type. Use 'playing', 'streaming', 'listening', or 'watching'.[/red]")
        return

    await bot.change_presence(activity=activity)
    console.print(f"[green]Presence set to {activity_type} '{name}'.[/green]")
