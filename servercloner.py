from discord.ext import commands
import discord
import asyncio
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align

console = Console()
os.system("cls" if os.name == "nt" else "clear")

ascii_title = r"""
██████╗  ██████╗ ███╗   ██╗ ██████╗ ██╗  ██╗██╗   ██╗ █████╗ ███╗   ██╗
██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗╚██╗██╔╝██║   ██║██╔══██╗████╗  ██║
██║  ██║██║   ██║██╔██╗ ██║██║   ██║ ╚███╔╝ ██║   ██║███████║██╔██╗ ██║
██║  ██║██║   ██║██║╚██╗██║██║   ██║ ██╔██╗ ╚██╗ ██╔╝██╔══██║██║╚██╗██║
██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝██╔╝ ██╗ ╚████╔╝ ██║  ██║██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝                                                                                                                                                                                                                                                                                             
"""

console.print(Align.center(ascii_title), style="bold white")

token = Prompt.ask("[bold white]Enter your Discord token[/bold white]")
source_guild_id = Prompt.ask("[bold white]ID of the server where everything will be cloned. [/bold white]")
target_guild_id = Prompt.ask("[bold white]Server ID where everything will be placed. [/bold white]")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@bot.event
async def on_ready():
    console.print(f"\n[bold white]logged in:[/bold white] [white]{bot.user}[/white]")

    source = discord.utils.get(bot.guilds, id=int(source_guild_id))
    target = discord.utils.get(bot.guilds, id=int(target_guild_id))

    if not source:
        console.print(f"[bold white]You are not on the server you want to cloner. ([white]{source_guild_id}[/white])[/bold red]")
        await bot.close()
        return
    if not target:
        console.print(f"[bold white]error ([white]{target_guild_id}[/white])[/bold white]")
        await bot.close()
        return

    console.print(f"[white]Cloning:[/white] [white]{source.name}[/white]")
    console.print(f"[white]h|Until Here:[/white] [white]{target.name}[/white]\n")

    await clone_server(source, target)
    console.print(f"\n[bold white]cloning completed [white]{source.name}[/white] to [white]{target.name}[/white]![/bold red]")
    await bot.close()

async def clone_server(source_guild, target_guild):
    for channel in target_guild.channels:
        try:
            await channel.delete()
            console.print(f"[white]Deleting channels:[/white] [white]{channel.name}[/white] ([white]{channel.id}[/white])")
            await asyncio.sleep(1)
        except Exception as e:
            console.print(f"[white]error to deleting channel {channel.name}: {e}[/white]")
    for role in reversed(target_guild.roles):
        if role.name != "@everyone":
            try:
                await role.delete()
                console.print(f"[white]Deleting roles:[/white] [white]{role.name}[/white] ([white]{role.id}[/white])")
                await asyncio.sleep(1)
            except Exception as e:
                console.print(f"[white]error to deleting roles {role.name}: {e}[/white]")

    role_map = {}
    for role in reversed(source_guild.roles):
        if role.name != "@everyone":
            try:
                new_role = await target_guild.create_role(name=role.name, colour=role.colour)
                role_map[role.id] = new_role
                console.print(f"[white]role created:[/white] [white]{role.name}[/white] ([white]{new_role.id}[/white])")
                await asyncio.sleep(1)
            except Exception as e:
                console.print(f"[white]error to created role {role.name}: {e}[/white]")

    for category in source_guild.categories:
        try:
            new_cat = await target_guild.create_category(name=category.name)
            console.print(f"[white]category created:[/white] [white]{category.name}[/white] ([white]{new_cat.id}[/white])")
            await asyncio.sleep(1)

            for channel in category.channels:
                try:
                    if isinstance(channel, discord.TextChannel):
                        new_channel = await new_cat.create_text_channel(name=channel.name)
                        console.print(f"  [white]canal creado:[/white] [white]{channel.name}[/white] ([white]{new_channel.id}[/white])")
                    elif isinstance(channel, discord.VoiceChannel):
                        new_channel = await new_cat.create_voice_channel(name=channel.name)
                        console.print(f"  [white]channel created:[/white] [white]{channel.name}[/white] ([white]{new_channel.id}[/white])")
                    await asyncio.sleep(1)
                except Exception as e:
                    console.print(f"[white]  error to channel created {channel.name}: {e}[/white]")
        except Exception as e:
            console.print(f"[white] error to category created {category.name}: {e}[/white]")

bot.run(token, bot=False)
