import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import create_embed

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Display user or server avatar")
    @app_commands.describe(user="The user whose avatar to display (leave empty for your own)", server="Show server icon instead of user avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None, server: bool = False):
        """Display user avatar or server icon"""
        
        if server:
            # Show server icon
            guild = interaction.guild
            if guild.icon:
                embed = create_embed(
                    title=f"🏛️ {guild.name} Server Icon",
                    color=discord.Color.blue()
                )
                embed.set_image(url=guild.icon.url)
                embed.add_field(name="Server", value=guild.name, inline=True)
                embed.add_field(name="Members", value=guild.member_count, inline=True)
                embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
                
                # Add download links
                embed.add_field(
                    name="Download Links",
                    value=f"[PNG]({guild.icon.replace(format='png', size=1024).url}) | "
                          f"[JPG]({guild.icon.replace(format='jpg', size=1024).url}) | "
                          f"[WEBP]({guild.icon.replace(format='webp', size=1024).url})",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
            else:
                embed = create_embed(
                    title="❌ No Server Icon",
                    description="This server doesn't have an icon set.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # Show user avatar
            target_user = user or interaction.user
            
            embed = create_embed(
                title=f"👤 {target_user.display_name}'s Avatar",
                color=target_user.color if target_user.color != discord.Color.default() else discord.Color.blue()
            )
            embed.set_image(url=target_user.display_avatar.url)
            embed.add_field(name="User", value=target_user.mention, inline=True)
            embed.add_field(name="Username", value=str(target_user), inline=True)
            embed.add_field(name="ID", value=target_user.id, inline=True)
            embed.add_field(name="Joined Server", value=target_user.joined_at.strftime("%B %d, %Y") if target_user.joined_at else "Unknown", inline=True)
            embed.add_field(name="Account Created", value=target_user.created_at.strftime("%B %d, %Y"), inline=True)
            
            # Add download links
            avatar = target_user.display_avatar
            embed.add_field(
                name="Download Links",
                value=f"[PNG]({avatar.replace(format='png', size=1024).url}) | "
                      f"[JPG]({avatar.replace(format='jpg', size=1024).url}) | "
                      f"[WEBP]({avatar.replace(format='webp', size=1024).url})",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AvatarCog(bot))
