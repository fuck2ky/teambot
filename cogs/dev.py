from discord.ext import commands


def setup(bot):
    bot.add_cog(DevCog(bot))


class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload_extensions(self, context):
        for extension in self.bot.loaded_extensions:
            self.bot.reload_extension(extension)
