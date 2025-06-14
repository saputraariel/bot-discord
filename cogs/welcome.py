import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from utils.embeds import create_embed

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_data = self.load_welcome_data()

    def load_welcome_data(self):
        """Load welcome messages from JSON file"""
        try:
            with open('data/welcome_messages.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_welcome_data(self):
        """Save welcome messages to JSON file"""
        os.makedirs('data', exist_ok=True)
        with open('data/welcome_messages.json', 'w') as f:
            json.dump(self.welcome_data, f, indent=2)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle member join events"""
        guild_id = str(member.guild.id)
        if guild_id in self.welcome_data and self.welcome_data[guild_id].get('enabled', False):
            channel_id = self.welcome_data[guild_id].get('channel_id')
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    welcome_msg = self.welcome_data[guild_id].get('welcome_message', 'Welcome {user} to {server}!')
                    welcome_msg = welcome_msg.replace('{user}', member.mention)
                    welcome_msg = welcome_msg.replace('{server}', member.guild.name)
                    welcome_msg = welcome_msg.replace('{member_count}', str(member.guild.member_count))

                    embed = create_embed(
                        title="👋 Welcome!",
                        description=welcome_msg,
                        color=discord.Color.green()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"Member #{member.guild.member_count}")

                    if self.welcome_data[guild_id].get('welcome_image'):
                        embed.set_image(url=self.welcome_data[guild_id]['welcome_image'])

                    await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Handle member leave events"""
        guild_id = str(member.guild.id)
        if guild_id in self.welcome_data and self.welcome_data[guild_id].get('enabled', False):
            channel_id = self.welcome_data[guild_id].get('channel_id')
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    goodbye_msg = self.welcome_data[guild_id].get('goodbye_message', 'Goodbye {user}!')
                    goodbye_msg = goodbye_msg.replace('{user}', str(member))
                    goodbye_msg = goodbye_msg.replace('{server}', member.guild.name)
                    goodbye_msg = goodbye_msg.replace('{member_count}', str(member.guild.member_count))

                    embed = create_embed(
                        title="👋 Goodbye!",
                        description=goodbye_msg,
                        color=discord.Color.orange()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"We now have {member.guild.member_count} members")

                    if self.welcome_data[guild_id].get('goodbye_image'):
                        embed.set_image(url=self.welcome_data[guild_id]['goodbye_image'])

                    await channel.send(embed=embed)

    @app_commands.command(name="welcome", description="Configure welcome messages (Administrator only)")
    async def welcome_setup(self, interaction: discord.Interaction):
        """Configure welcome messages"""
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create a simple setup interface
        guild_id = str(interaction.guild.id)
        current_config = self.welcome_data.get(guild_id, {})
        
        embed = create_embed(
            title="🔧 Welcome System Configuration",
            description="Current welcome system settings:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Status",
            value="✅ Enabled" if current_config.get('enabled', False) else "❌ Disabled",
            inline=True
        )
        
        channel_id = current_config.get('channel_id')
        channel = self.bot.get_channel(channel_id) if channel_id else None
        embed.add_field(
            name="Channel",
            value=channel.mention if channel else "Not set",
            inline=True
        )
        
        embed.add_field(
            name="Welcome Message",
            value=current_config.get('welcome_message', 'Not set'),
            inline=False
        )
        
        embed.add_field(
            name="Goodbye Message",
            value=current_config.get('goodbye_message', 'Not set'),
            inline=False
        )
        
        embed.add_field(
            name="Available Variables",
            value="`{user}` - User mention\n`{server}` - Server name\n`{member_count}` - Member count",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setwelcome", description="Set welcome message and channel (Administrator only)")
    @app_commands.describe(
        channel="Channel for welcome messages",
        message="Welcome message (use {user}, {server}, {member_count})",
        image_url="Optional image URL for welcome messages"
    )
    async def set_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, image_url: str = None):
        """Set welcome message and channel"""
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.welcome_data:
            self.welcome_data[guild_id] = {}
        
        self.welcome_data[guild_id]['enabled'] = True
        self.welcome_data[guild_id]['channel_id'] = channel.id
        self.welcome_data[guild_id]['welcome_message'] = message
        
        if image_url:
            self.welcome_data[guild_id]['welcome_image'] = image_url
        
        self.save_welcome_data()
        
        embed = create_embed(
            title="✅ Welcome Message Configured",
            description=f"Welcome messages will be sent to {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="Message", value=message, inline=False)
        if image_url:
            embed.add_field(name="Image", value=image_url, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setgoodbye", description="Set goodbye message (Administrator only)")
    @app_commands.describe(
        message="Goodbye message (use {user}, {server}, {member_count})",
        image_url="Optional image URL for goodbye messages"
    )
    async def set_goodbye(self, interaction: discord.Interaction, message: str, image_url: str = None):
        """Set goodbye message"""
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.welcome_data:
            embed = create_embed(
                title="❌ Welcome System Not Configured",
                description="Please use `/setwelcome` first to configure the welcome system.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.welcome_data[guild_id]['goodbye_message'] = message
        
        if image_url:
            self.welcome_data[guild_id]['goodbye_image'] = image_url
        
        self.save_welcome_data()
        
        embed = create_embed(
            title="✅ Goodbye Message Configured",
            description="Goodbye message has been set.",
            color=discord.Color.green()
        )
        embed.add_field(name="Message", value=message, inline=False)
        if image_url:
            embed.add_field(name="Image", value=image_url, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="togglewelcome", description="Enable/disable welcome system (Administrator only)")
    async def toggle_welcome(self, interaction: discord.Interaction):
        """Toggle welcome system on/off"""
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = create_embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.welcome_data:
            self.welcome_data[guild_id] = {'enabled': False}
        
        self.welcome_data[guild_id]['enabled'] = not self.welcome_data[guild_id].get('enabled', False)
        self.save_welcome_data()
        
        status = "enabled" if self.welcome_data[guild_id]['enabled'] else "disabled"
        color = discord.Color.green() if self.welcome_data[guild_id]['enabled'] else discord.Color.red()
        
        embed = create_embed(
            title=f"✅ Welcome System {status.title()}",
            description=f"Welcome system has been {status}.",
            color=color
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
