import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from utils.embeds import create_embed

class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Display server information")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = create_embed(
            title=f"🏛️ {guild.name} Server Information",
            color=discord.Color.blue()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(
            name="📊 Basic Info",
            value=f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n"
                  f"**Created:** {guild.created_at.strftime('%B %d, %Y')}\n"
                  f"**Server ID:** {guild.id}\n"
                  f"**Region:** {guild.preferred_locale}",
            inline=True
        )
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots
        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {total_members}\n"
                  f"**Humans:** {humans}\n"
                  f"**Bots:** {bots}\n"
                  f"**Online:** {online_members}",
            inline=True
        )
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        embed.add_field(
            name="📝 Channels",
            value=f"**Text:** {text_channels}\n"
                  f"**Voice:** {voice_channels}\n"
                  f"**Categories:** {categories}\n"
                  f"**Total:** {text_channels + voice_channels}",
            inline=True
        )
        features = guild.features
        if features:
            feature_list = []
            feature_names = {
                'COMMUNITY': 'Community Server',
                'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
                'MEMBER_VERIFICATION_GATE_ENABLED': 'Membership Screening',
                'PREVIEW_ENABLED': 'Server Preview',
                'PARTNERED': 'Partnered',
                'VERIFIED': 'Verified',
                'DISCOVERABLE': 'Discoverable',
                'BANNER': 'Banner',
                'VANITY_URL': 'Vanity URL',
                'ANIMATED_ICON': 'Animated Icon',
                'INVITE_SPLASH': 'Invite Splash',
                'NEWS': 'News Channels',
                'COMMERCE': 'Commerce',
                'THREADS_ENABLED': 'Threads Enabled'
            }
            for feature in features:
                if feature in feature_names:
                    feature_list.append(feature_names[feature])
            if feature_list:
                embed.add_field(
                    name="✨ Features",
                    value="\n".join(f"• {feature}" for feature in feature_list[:10]),
                    inline=False
                )
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        embed.add_field(
            name="🚀 Nitro Boost",
            value=f"**Level:** {boost_level}/3\n"
                  f"**Boosts:** {boost_count}",
            inline=True
        )
        role_count = len(guild.roles) - 1
        embed.add_field(
            name="🎭 Roles",
            value=f"**Total:** {role_count}\n"
                  f"**Highest:** {guild.roles[-1].mention if len(guild.roles) > 1 else '@everyone'}",
            inline=True
        )
        emoji_count = len(guild.emojis)
        static_emojis = sum(1 for emoji in guild.emojis if not emoji.animated)
        animated_emojis = sum(1 for emoji in guild.emojis if emoji.animated)
        embed.add_field(
            name="😀 Emojis",
            value=f"**Total:** {emoji_count}\n"
                  f"**Static:** {static_emojis}\n"
                  f"**Animated:** {animated_emojis}",
            inline=True
        )
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }
        embed.add_field(
            name="🔒 Security",
            value=f"**Verification:** {verification_levels.get(guild.verification_level, 'Unknown')}\n"
                  f"**2FA Required:** {'Yes' if guild.mfa_level else 'No'}\n"
                  f"**Explicit Filter:** {guild.explicit_content_filter.name.title()}",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="membercount", description="Show current member count")
    async def membercount(self, interaction: discord.Interaction):
        guild = interaction.guild
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots
        embed = create_embed(
            title=f"👥 {guild.name} Member Count",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total Members", value=total_members, inline=True)
        embed.add_field(name="Humans", value=humans, inline=True)
        embed.add_field(name="Bots", value=bots, inline=True)
        embed.add_field(name="Online", value=online_members, inline=True)
        embed.add_field(name="Offline", value=total_members - online_members, inline=True)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set_welcomedm", description="Set custom welcome DM message (Admin only)")
    @app_commands.describe(message="Custom welcome message", image_url="Optional image URL to include")
    async def set_welcomedm(self, interaction: discord.Interaction, message: str, image_url: str = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an administrator to use this command.", ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        welcome_data = {"message": message, "image_url": image_url}
        if not os.path.exists("data"):
            os.makedirs("data")
        config_path = os.path.join("data", "welcome_dm_config.json")
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        data[guild_id] = welcome_data
        with open(config_path, "w") as f:
            json.dump(data, f, indent=4)
        await interaction.response.send_message("✅ Welcome DM message set successfully!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ServerCog(bot))