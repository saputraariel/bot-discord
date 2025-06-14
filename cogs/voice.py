import discord
from discord.ext import commands
from discord import app_commands
from utils.checks import is_admin
from utils.embeds import create_embed

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="move", description="Move a user to a voice channel (Administrator only)")
    @app_commands.describe(user="The user to move", channel="The voice channel to move them to")
    async def move_user(self, interaction: discord.Interaction, user: discord.Member, channel: discord.VoiceChannel):
        """Move a user to a voice channel"""
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check if target user is in a voice channel
        if user.voice is None:
            embed = create_embed(
                title="❌ User Not in Voice",
                description=f"{user.mention} is not currently in a voice channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Move the user
            await user.move_to(channel)
            
            embed = create_embed(
                title="✅ User Moved",
                description=f"Successfully moved {user.mention} to {channel.mention}",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = create_embed(
                title="❌ Permission Error",
                description="I don't have permission to move users in voice channels.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.HTTPException as e:
            embed = create_embed(
                title="❌ Error",
                description=f"An error occurred while moving the user: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(VoiceCog(bot))
