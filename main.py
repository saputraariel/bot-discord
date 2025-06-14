import discord
from discord.ext import commands
import asyncio
import os
import json
import logging

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
    # This will be handled by the welcome cog
    pass

@bot.event
async def on_member_remove(member):
    """Handle member leave events for goodbye messages"""
    # This will be handled by the welcome cog
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
    async with bot:
        await load_cogs()
        # Get token from environment variable
        token = os.getenv('DISCORD_TOKEN', 'MTM2MTYzODE2NzIzNjcwNjQyNg.GBDfux.veKT1kHxf6dkHbHXOyh51o4z_gLNFN1PFbfsZY')
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
