import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
from utils.embeds import create_embed

# yt-dlp configuration
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    @app_commands.command(name="play", description="Play music from YouTube")
    @app_commands.describe(query="Song title or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        """Play music from YouTube"""
        
        # Check if user is in a voice channel
        if not interaction.user.voice:
            embed = create_embed(
                title="❌ Not in Voice Channel",
                description="You need to join a voice channel first to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        channel = interaction.user.voice.channel
        
        # Check bot permissions
        permissions = channel.permissions_for(interaction.guild.me)
        if not permissions.connect or not permissions.speak:
            embed = create_embed(
                title="❌ Missing Permissions",
                description="I need permission to connect and speak in voice channels.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Defer the response since this might take a while
        await interaction.response.defer()

        try:
            # Connect to voice channel if not already connected
            voice_client = None
            if interaction.guild.id not in self.voice_clients:
                try:
                    voice_client = await channel.connect()
                    self.voice_clients[interaction.guild.id] = voice_client
                except Exception as e:
                    embed = create_embed(
                        title="❌ Connection Failed",
                        description=f"Could not connect to voice channel: {str(e)}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    return
            else:
                voice_client = self.voice_clients[interaction.guild.id]
                
            # Move to user's channel if in different channel
            if voice_client.channel != channel:
                try:
                    await voice_client.move_to(channel)
                except Exception as e:
                    embed = create_embed(
                        title="❌ Cannot Move",
                        description=f"Could not move to your voice channel: {str(e)}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    return

            # Stop current audio if playing
            if voice_client.is_playing():
                voice_client.stop()

            # Create the audio source
            try:
                player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
            except Exception as e:
                embed = create_embed(
                    title="❌ Error Loading Audio",
                    description=f"Could not find or load audio for: **{query}**\nTry using a different search term or YouTube URL.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Play the audio
            voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

            # Create embed with song info
            embed = create_embed(
                title="🎵 Now Playing",
                description=f"**{player.title}**",
                color=discord.Color.blue()
            )
            embed.add_field(name="Requested by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            
            if hasattr(player, 'duration') and player.duration:
                duration = f"{player.duration // 60}:{player.duration % 60:02d}"
                embed.add_field(name="Duration", value=duration, inline=True)
            
            if hasattr(player, 'thumbnail') and player.thumbnail:
                embed.set_thumbnail(url=player.thumbnail)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            embed = create_embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="stop", description="Stop music and disconnect from voice channel")
    async def stop(self, interaction: discord.Interaction):
        """Stop music and disconnect"""
        
        if interaction.guild.id in self.voice_clients:
            voice_client = self.voice_clients[interaction.guild.id]
            await voice_client.disconnect()
            del self.voice_clients[interaction.guild.id]
            
            embed = create_embed(
                title="⏹️ Music Stopped",
                description="Disconnected from voice channel.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = create_embed(
                title="❌ Not Playing",
                description="I'm not currently playing music.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="pause", description="Pause current music")
    async def pause(self, interaction: discord.Interaction):
        """Pause current music"""
        
        if interaction.guild.id in self.voice_clients:
            voice_client = self.voice_clients[interaction.guild.id]
            if voice_client.is_playing():
                voice_client.pause()
                embed = create_embed(
                    title="⏸️ Music Paused",
                    description="Music has been paused.",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
            else:
                embed = create_embed(
                    title="❌ Not Playing",
                    description="No music is currently playing.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = create_embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="resume", description="Resume paused music")
    async def resume(self, interaction: discord.Interaction):
        """Resume paused music"""
        
        if interaction.guild.id in self.voice_clients:
            voice_client = self.voice_clients[interaction.guild.id]
            if voice_client.is_paused():
                voice_client.resume()
                embed = create_embed(
                    title="▶️ Music Resumed",
                    description="Music has been resumed.",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
            else:
                embed = create_embed(
                    title="❌ Not Paused",
                    description="Music is not currently paused.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = create_embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
