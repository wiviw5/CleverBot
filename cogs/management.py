"""
This file is a crucial part of the bot, namely the loading & unloading of modules for the development & owner of the bot to manage it.
"""
import discord
from discord import app_commands
from discord.ext import commands

from utils.bot_config import getMainGuildID
from utils.utils import getTime, isOwner


class Management(commands.Cog, name="Command management"):
    def __init__(self, bot):
        self.bot = bot

    management = app_commands.Group(name="management", description="All management related commands", guild_ids=[getMainGuildID()])

    @management.command(name="sync", description="Syncs the commands properly for your bot.")
    async def sync(self, interaction: discord.Interaction):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        # await interaction.client.tree.sync() # Global sync. //TODO Add global sync option.
        await interaction.client.tree.sync(guild=discord.Object(getMainGuildID()))
        await interaction.followup.send(f"Successfully done!")
        print(f"User [{interaction.user.id}] Synced commands at: {getTime()}")

    @management.command(name="unsync", description="Will unsync all commands from the bot.")
    async def unsync(self, interaction: discord.Interaction):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"Starting unsync process, this action is not reversible without a bot restart.")
        interaction.client.tree.clear_commands(guild=discord.Object(getMainGuildID()))
        await self.bot.tree.sync(guild=discord.Object(getMainGuildID()))
        print(f"User [{interaction.user.id}] Unsynced commands at: {getTime()}")

    @management.command(name="load", description="Loads a cog")
    @app_commands.describe(cog='Name of the cog to be loaded.')
    async def load(self, interaction: discord.Interaction, cog: str):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except ImportError:
            await interaction.followup.send(f"Failed to load cog: {cog}")
            return
        except discord.ext.commands.ExtensionNotFound:
            await interaction.followup.send(f"Failed to reload cog: {cog}\nReason: Extension not Found.")
            return
        await interaction.followup.send(f"Successfully loaded cog: {cog}")
        print(f"User [{interaction.user.id}] Loaded cog: [{cog}] At: {getTime()}")

    @management.command(name="unload", description="Unloads a cog")
    @app_commands.describe(cog='Name of the cog to be unloaded.')
    async def unload(self, interaction: discord.Interaction, cog: str):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except ImportError:
            await interaction.followup.send(f"Failed to unload cog: {cog}")
            return
        await interaction.followup.send(f"Successfully unloaded cog: {cog}")
        print(f"User [{interaction.user.id}] Unloaded cog: [{cog}] At: {getTime()}")

    @management.command(name="reload", description="Reloads a cog")
    @app_commands.describe(cog='Name of the cog to be reloaded.')
    async def reload(self, interaction: discord.Interaction, cog: str):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        except ImportError:
            await interaction.followup.send(f"Failed to reload cog: {cog}\nReason: Import Error.")
            return
        except discord.ext.commands.ExtensionNotLoaded:
            await interaction.followup.send(f"Failed to reload cog: {cog}\nReason: Extension not Loaded/Not Found.")
            return
        await interaction.followup.send(f"Successfully reload cog: {cog}")
        print(f"User [{interaction.user.id}] Reloaded cog: [{cog}] At: {getTime()}")

    @management.command(name="list_extensions", description="Lists all extensions")
    async def get_extensions(self, interaction: discord.Interaction):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.response.defer(ephemeral=True)
        extensions = ""
        for extension in self.bot.extensions:
            extensions = extensions + str(extension).split(".")[1] + ", "
        await interaction.followup.send(f"Got all extensions: {extensions[:-2]}")
        print(f"User [{interaction.user.id}] Got all extensions at: {getTime()}")
        print(f"Extensions: {extensions[:-2]}")


async def setup(bot):
    await bot.add_cog(Management(bot))
