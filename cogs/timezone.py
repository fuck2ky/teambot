from discord.ext import commands
from datetime import datetime
import pytz
import tzlocal
from modules import persistence
from modules.utils import send_embed, log_command


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


def get_localized_now(server_id):
    timezone = 'GMT'
    config = persistence.get_config(server_id)
    if config and config['timezone']:
        timezone = config['timezone']
    if timezone.lower() == 'est':
        timezone = 'America/New_York'
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def get_pretty_time(hour, minute):
    return f'{str(hour).zfill(2)}:{str(minute).zfill(2)}'


def setup(bot):
    bot.add_cog(Timezone(bot))


class Timezone(commands.Cog):
    """Timezone-related commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def servertime(self, context):
        log_command("servertime", context)
        now = get_localized_now(context.guild.id)
        await send_embed(context, f'The server time is `{get_pretty_time(now.hour, now.minute)}`')

    @commands.command()
    async def timezone(self, context, timezone=None):
        """
        Command to set manage the timezone used by the bot to schedule pings in this server.
        If used without arguments, it displays the timezone currently in use.
        If used with a single argument, it will try to parse is as a timezone and set it for the current server. For
        a list of the possible timezones, look here: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
        """
        log_command("timezone", context)
        if timezone is None:
            await show_timezone(context, timezone)
        else:
            await set_timezone(context, timezone)
