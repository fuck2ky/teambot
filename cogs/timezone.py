from discord.ext import commands
import datetime
import pytz
import tzlocal
from modules import persistence
from modules.utils import send_embed


async def show_timezone(context, timezone):
    config = persistence.get_config(context.guild.id)
    if config and config['timezone']:
        configured_timezone = config['timezone']
    else:
        configured_timezone = 'GMT'
    await send_embed(context, f'The currently configured timezone is `{configured_timezone}`')


async def set_timezone(context, timezone):
    try:
        pytz.timezone(timezone)
        persistence.set_config(context.guild.id, 'timezone', timezone)
        await send_embed(context, f'Server timezone correctly set to `{timezone}`')
    except pytz.exceptions.UnknownTimeZoneError:
        await send_embed(context, f'Sorry, the timezone `{timezone}` is not valid. Choose one from '
                                  f'https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568')


def get_localized_now():
    tz_name = tzlocal.get_localzone().zone
    local_tz = pytz.timezone(tz_name)
    local_time = local_tz.localize(datetime.datetime.now())

    config = persistence.get_config(persistence.ConfigName.PINGS)

    if config and config.timezone:
        wanted_tz = pytz.timezone(config.timezone)
        local_time = local_time.astimezone(wanted_tz)
    return local_time


def setup(bot):
    bot.add_cog(TimezoneCog(bot))


class TimezoneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def timezone(self, context, timezone=None):
        if timezone is None:
            await show_timezone(context, timezone)
        else:
            await set_timezone(context, timezone)
