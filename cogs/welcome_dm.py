import discord
from discord.ext import commands
import json
import os

class WelcomeDMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config_path = os.path.join("data", "welcome_dm_config.json")

        try:
            with open(config_path, "r", encoding="utf-8") as f:  # Tambah encoding utf-8
                    data = json.load(f)

        except FileNotFoundError:
            data = {}

        guild_id = str(member.guild.id)
        if guild_id in data:
            config = data[guild_id]
            message = config.get("message", "Welcome to the server!")
            image_url = config.get("image_url")

            embed = discord.Embed(description=message, color=discord.Color.green())
            if image_url:
                embed.set_image(url=image_url)

            try:
                await member.send(embed=embed)
            except discord.Forbidden:
                print(f"Cannot send DM to {member.name}")

async def setup(bot):
    await bot.add_cog(WelcomeDMCog(bot))
