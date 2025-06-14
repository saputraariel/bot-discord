import discord
from discord.ext import commands

def is_admin():
    """Check if user has administrator permissions"""
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator
    return predicate

def is_in_voice():
    """Check if user is in a voice channel"""
    async def predicate(interaction: discord.Interaction):
        return interaction.user.voice is not None
    return predicate

def is_bot_in_voice():
    """Check if bot is in a voice channel in the guild"""
    async def predicate(interaction: discord.Interaction):
        return interaction.guild.voice_client is not None
    return predicate

class MissingPermissions(commands.CheckFailure):
    """Exception raised when a user is missing permissions"""
    pass

class NotInVoiceChannel(commands.CheckFailure):
    """Exception raised when a user is not in a voice channel"""
    pass

class BotNotInVoiceChannel(commands.CheckFailure):
    """Exception raised when the bot is not in a voice channel"""
    pass
