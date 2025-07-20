import discord
from discord.ext import commands
import asyncio
import os
from rich.console import Console
from rich.align import Align
from rich.prompt import Prompt
import aiohttp

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
source_guild_id = int(Prompt.ask("[bold white]Enter the ID of the server to clone[/bold white]"))
target_guild_id = int(Prompt.ask("[bold white]Enter the ID of the target server[/bold white]"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@bot.event
async def on_ready():
    console.print(f"\n[bold white]Logged in as:[/bold white] [white]{bot.user}[/white]")
    source = bot.get_guild(source_guild_id)
    target = bot.get_guild(target_guild_id)

    if not source:
        console.print(f"[bold red]You are not in the source server ({source_guild_id})[/bold red]")
        await bot.close()
        return
    if not target:
        console.print(f"[bold red]Target server not found ({target_guild_id})[/bold red]")
        await bot.close()
        return

    console.print(f"[white]Cloning from:[/white] {source.name}")
    console.print(f"[white]To server:[/white] {target.name}\n")

    await clone_server(source, target)

    console.print(f"\n[bold green]Cloning completed![/bold green]")
    await bot.close()

async def clone_server(source, target):
    # Change server name and icon, banner
    try:
        banner = await source.banner_url.read() if source.banner else None
        icon = await source.icon_url.read() if source.icon else None

        await target.edit(
            name=source.name,
            icon=icon,
            banner=banner,
            description=source.description,
            verification_level=source.verification_level,
            default_notifications=source.default_notifications,
            explicit_content_filter=source.explicit_content_filter,
            afk_timeout=source.afk_timeout,
        )
        console.print("[green]Server name, icon, and banner cloned[/green]")
    except Exception as e:
        console.print(f"[red]Error cloning server settings: {e}[/red]")

    # Delete all channels and roles
    for channel in target.channels:
        try:
            await channel.delete()
            console.print(f"Deleting channel: {channel.name}")
            await asyncio.sleep(1)
        except Exception as e:
            console.print(f"Error deleting channel {channel.name}: {e}")
    for role in reversed(target.roles):
        if role.name != "@everyone":
            try:
                await role.delete()
                console.print(f"Deleting role: {role.name}")
                await asyncio.sleep(1)
            except Exception as e:
                console.print(f"Error deleting role {role.name}: {e}")

    # Clone roles
    role_map = {}
    for role in reversed(source.roles):
        if role.name != "@everyone":
            try:
                new_role = await target.create_role(
                    name=role.name,
                    colour=role.colour,
                    hoist=role.hoist,
                    permissions=role.permissions,
                    mentionable=role.mentionable,
                )
                role_map[role.id] = new_role
                console.print(f"Role created: {role.name}")
                await asyncio.sleep(1)
            except Exception as e:
                console.print(f"Error creating role {role.name}: {e}")

    # Clone categories and channels
    for category in source.categories:
        try:
            overwrites = {
                role_map.get(overwrite.id, target.default_role): overwrite
                for overwrite in category.overwrites.values()
            }
            new_cat = await target.create_category(name=category.name, overwrites=overwrites)
            console.print(f"Category created: {category.name}")
            await asyncio.sleep(1)

            for channel in category.channels:
                overwrites = {}
                for target_role_id, overwrite in channel.overwrites.items():
                    target_role = role_map.get(target_role_id, target.default_role)
                    overwrites[target_role] = overwrite
                try:
                    if isinstance(channel, discord.TextChannel):
                        new_channel = await new_cat.create_text_channel(
                            name=channel.name,
                            topic=channel.topic,
                            slowmode_delay=channel.slowmode_delay,
                            nsfw=channel.nsfw,
                            overwrites=overwrites,
                        )
                        console.print(f"  Text channel created: {channel.name}")
                    elif isinstance(channel, discord.VoiceChannel):
                        new_channel = await new_cat.create_voice_channel(
                            name=channel.name,
                            bitrate=channel.bitrate,
                            user_limit=channel.user_limit,
                            overwrites=overwrites,
                        )
                        console.print(f"  Voice channel created: {channel.name}")
                    await asyncio.sleep(1)
                except Exception as e:
                    console.print(f"  Error creating channel {channel.name}: {e}")

        except Exception as e:
            console.print(f"Error creating category {category.name}: {e}")

    # Clone Emojis
    for emoji in source.emojis:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(emoji.url)) as resp:
                    img_bytes = await resp.read()
            await target.create_custom_emoji(name=emoji.name, image=img_bytes)
            console.print(f"Emoji created: {emoji.name}")
            await asyncio.sleep(1)
        except Exception as e:
            console.print(f"Error creating emoji {emoji.name}: {e}")

bot.run(token, bot=False)
