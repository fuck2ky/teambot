from discord.ext import commands
from discord import Embed
import asyncio


def setup(bot):
    bot.add_cog(DevCog(bot))


class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def test(self, context):
        embed = Embed(title='scrim', description='(Times are in 24h format, EST timezone)')
        message = await context.send(embed=embed)
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')

    @commands.command(hidden=True)
    async def reload(self, context):
        """Reloads all the cogs used by this bot"""
        for extension in self.bot.loaded_extensions:
            self.bot.reload_extension(extension)
