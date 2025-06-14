import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv  # Pastikan python-dotenv ada
import logging

# Load .env file (untuk lokal development)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_member_join(member):
    """Handle member join events for welcome messages"""
    pass

@bot.event
async def on_member_remove(member):
    """Handle member leave events for goodbye messages"""
    pass

async def load_cogs():
    """Load all cogs"""
    cogs = [
        'cogs.voice',
        'cogs.music',
        'cogs.avatar',
        'cogs.welcome',
        'cogs.welcome_dm',
        'cogs.server'
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'Loaded {cog}')
        except Exception as e:
            print(f'Failed to load {cog}: {e}')

async def main():
    await load_cogs()
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        print("TOKEN tidak ditemukan di environment variables!")
        return
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
