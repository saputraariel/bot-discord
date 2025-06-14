import discord
from datetime import datetime

def create_embed(title=None, description=None, color=None, footer=None, timestamp=True):
    """Create a standard embed with consistent styling"""
    
    if color is None:
        color = discord.Color.blue()
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    if timestamp:
        embed.timestamp = datetime.utcnow()
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed

def create_error_embed(title, description):
    """Create an error embed with red color"""
    return create_embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )

def create_success_embed(title, description):
    """Create a success embed with green color"""
    return create_embed(
        title=f"✅ {title}",
        description=description,
        color=discord.Color.green()
    )

def create_info_embed(title, description):
    """Create an info embed with blue color"""
    return create_embed(
        title=f"ℹ️ {title}",
        description=description,
        color=discord.Color.blue()
    )

def create_warning_embed(title, description):
    """Create a warning embed with orange color"""
    return create_embed(
        title=f"⚠️ {title}",
        description=description,
        color=discord.Color.orange()
    )
