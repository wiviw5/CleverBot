"""
This file is a part of the module "Minecraft Server"

This requires the package: https://pypi.org/project/mcstatus/ / https://github.com/py-mine/mcstatus (mcstatus, made by Dinnerbone)
"""
import base64
import io
import re
import time

import discord
import dns.resolver
from discord import app_commands
from discord.ext import commands
from mcstatus import JavaServer
from mcstatus.status_response import JavaStatusResponse

from utils.bot_config import getMainGuildID
from utils.utils import isOwner


class MCServer(commands.Cog, name="Minecraft Server Commands"):
    def __init__(self, bot):
        self.bot = bot

    mcserver = app_commands.Group(name="server", description="All Minecraft Server related commands", guild_ids=[getMainGuildID()])

    @mcserver.command(name="mcinfo", description="Replies with info a server's information.")
    @app_commands.describe(address='Server Address')
    @app_commands.describe(port='Server Port')
    @app_commands.describe(players='Whether or not to show the online player list.')
    async def mcinfo(self, interaction: discord.Interaction, address: str, port: int = 25565, players: bool = False):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        status = await getServerStatus(address=address, port=port, retry=0)
        if isinstance(status, str):
            await interaction.followup.send(f"This server is currently unavailable.\nPlease retry again later.\n\nError ID: `{status}`")
            return
        status: JavaStatusResponse

        embed = discord.Embed(color=5200474, title=f"Server Response in: `{round(status.latency, 2)}ms`", description=f"Online Players: `{status.players.online}`")
        embed.add_field(name="MOTD", value=status.motd.to_plain(), inline=False)
        embed.set_footer(text=f"{address} - {status.version.name}")

        if players:
            if status.players.sample is not None and len(status.players.sample) > 0:
                names = ""
                for player in status.players.sample:
                    names = names + f"{player.name} - {player.uuid}" + "\n"
                embed.add_field(name="Players", value=names, inline=False)

        filename = "server-icon.png"
        if status.favicon is not None:
            file = discord.File(io.BytesIO(base64.b64decode(status.favicon.removeprefix("data:image/png;base64,"))), filename=filename)
        else:
            file = discord.File(filename)
        embed.set_thumbnail(url=f"attachment://{filename}")
        await interaction.followup.send(embed=embed, file=file)

    @mcserver.command(name="mcembed", description="Makes an embed with specific information.")
    @app_commands.describe(name='Server Name')
    @app_commands.describe(address='Server Address')
    @app_commands.describe(port='Server Port')
    @app_commands.describe(players='Whether to include a player embed button or not.')
    async def serverembed(self, interaction: discord.Interaction, name: str, address: str, port: int, players: bool = False):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        status = await getServerStatus(address=address, port=port, retry=0)
        if isinstance(status, str):
            await interaction.followup.send(f"This server is currently unavailable.\nPlease retry again later.\n\nError ID: `{status}`")
            return
        await interaction.followup.send("Server found! Generating Embed.")
        status: JavaStatusResponse

        embed = discord.Embed(color=5200474, title=f"{name}", description=f"Server Address\n`{address}`")
        embed.set_footer(text=f"{status.version.name}")

        filename = "server-icon.png"
        if status.favicon is not None:
            file = discord.File(io.BytesIO(base64.b64decode(status.favicon.removeprefix("data:image/png;base64,"))), filename=filename)
        else:
            file = discord.File(filename)
        embed.set_thumbnail(url=f"attachment://{filename}")

        view = discord.ui.View(timeout=None)
        view.add_item(MCButtonView(address=address, port=port, players=players))
        await interaction.channel.send(embed=embed, file=file, view=view)


async def setup(bot):
    await bot.add_cog(MCServer(bot))


class MCButtonView(discord.ui.DynamicItem[discord.ui.Button], template=r'minecraftserver:info:\{(?P<info>[^}]*)\}'):
    def __init__(self, address: str, port: int, players: bool) -> None:
        if players:
            label = "Get Player Status"
            style = discord.ButtonStyle.success
        else:
            label = "Get Server Status"
            style = discord.ButtonStyle.primary
        self.address: str = address
        self.players: bool = players
        self.port: int = port
        super().__init__(
            discord.ui.Button(
                label=label,
                style=style,
                custom_id=f"minecraftserver:info:{{{address}:{port}:{players}}}"
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        info = str(match['info'])
        information = info.split(":")
        return cls(address=information[0], port=int(information[1]), players=information[2] == "True")

    async def callback(self, interaction: discord.Interaction) -> None:
        status = await getServerStatus(address=self.address, port=self.port, retry=0)
        if isinstance(status, str):
            await interaction.response.send_message(f"This server is currently unavailable.\nPlease retry again later.\n\nError ID: `{status}`", ephemeral=True)
            return
        status: JavaStatusResponse

        embed = discord.Embed(color=5200474, title=f"Server Response in: `{round(status.latency, 2)}ms`", description=f"Online Players: `{status.players.online}`")
        embed.add_field(name="MOTD", value=status.motd.to_plain(), inline=False)
        embed.set_footer(text=f"{self.address} - {status.version.name}")

        if self.players:
            if status.players.sample is not None and len(status.players.sample) > 0:
                names = ""
                for player in status.players.sample:
                    names = names + f"{player.name} - {player.uuid}" + "\n"
                embed.add_field(name="Players", value=names, inline=False)

        filename = "server-icon.png"
        if status.favicon is not None:
            file = discord.File(io.BytesIO(base64.b64decode(status.favicon.removeprefix("data:image/png;base64,"))), filename=filename)
        else:
            file = discord.File(filename)
        embed.set_thumbnail(url=f"attachment://{filename}")
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)


async def getServerStatus(address: str, port: int, retry: int) -> [JavaStatusResponse, str]:
    """
    This is for getting a server with automatic retries. Retries go as such:

    Retry state 0 -> Fresh request.

    Retry state 1 -> Invalid port. Retried only once.

    Retry state 2 -> DNS/lifetime expiration. Retried once after 5 seconds.
    """
    server = JavaServer(address, port)
    try:
        status = await server.async_status()
    except ConnectionRefusedError:
        # This is state 1.
        if retry != 0:
            return getErrorType(1)
        retryServer = await JavaServer.async_lookup(address=address)
        return await getServerStatus(address=address, port=retryServer.address.port, retry=1)
    except dns.resolver.LifetimeTimeout:
        # This is state 2.
        if retry != 0:
            return getErrorType(2)
        time.sleep(5)
        return await getServerStatus(address=address, port=port, retry=2)



    return status


def getErrorType(code: int) -> str:
    match code:
        case 1:
            return "Invalid port"
        case 2:
            return "Lifetime expiration"
        case _:
            return "Unknown Error"
