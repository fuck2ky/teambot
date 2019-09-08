import calendar
import discord
from discord.ext import commands, tasks

from cogs import timezone
from modules import persistence
from modules.utils import send_embed


TASKS_LOOP_FREQ = 60.0


async def check_pings(bot, now):
    print('Checking pings.')
    pings = persistence.get_pings()
    for ping in pings:
        if now.weekday() == ping['weekday'] and now.hour == ping['hour'] and now.minute == ping['minute']:
            await do_ping(bot, now, ping)


async def do_ping(bot, now, ping):
    print(str(now) + f" triggering ping #{ping.doc_id}")
    channel = bot.get_channel(ping['channel_id'])
    if ping['add_schedule'] is True:
        await schedule_weekend(channel)
    await send_embed(channel, ping['message'])


async def show_pings(context, is_schedule_check):
    name = 'schedule checks' if is_schedule_check else 'pings'
    print(f'Showing {name}.')
    pings = persistence.get_pings(is_schedule=is_schedule_check, server_id=context.guild.id)
    embed = discord.Embed(title=f'Configured {name}', colour=discord.Colour.dark_blue())
    for ping in pings:
        weekday = ping['weekday']
        hour = ping['hour']
        minute = ping['minute']
        message = ping['message']
        embed.add_field(
            name=f'Every {calendar.day_name[weekday]} at {hour}:{minute}',
            value=message,
            inline=False
        )
    await context.send(embed=embed)


async def create_ping(context, weekdayname, hour, minute, msg, add_schedule):
    print(f'Creating new ping with weekdayname={weekdayname}, hour={hour}, minute={minute}, msg={msg} '
          f'and add_schedule={add_schedule}')
    message = context.message
    await message.delete()

    channel = message.channel

    if weekdayname == '' or hour == '' or minute == '':
        await channel.send(f"Oops! Weekday and hour are required arguments, please try again")
        return

    # Check weekeday
    try:
        weekdayname = weekdayname.capitalize()
    except:
        await send_embed(channel, f"Oops! `{weekdayname}` doesn't look like a week day name, please try again")
        return
    if weekdayname in calendar.day_name[:]:
        weekday = calendar.day_name[:].index(weekdayname)
    elif weekdayname in calendar.day_abbr[:]:
        weekday = calendar.day_abbr[:].index(weekdayname)
    else:
        await send_embed(channel, f"Oops! `{weekdayname}` is not a full week day name nor an abbreviated version, did "
                                  f"you mispell it?")
        return

    # Check hour
    if not hour.isdigit() or int(hour) not in range(0, 24):
        await send_embed(channel, f"Oops! `{hour}` is not a proper hour number in 24h format, please try again")
        return
    if not minute.isdigit() or int(minute) not in range(0, 60):
        await send_embed(channel, f"Oops! `{minute}` is not a proper minute number, please try again")
        return

    persistence.create_ping(
        channel.guild.id, channel.id, weekday, hour, minute, msg, add_schedule)
    name = 'schedule check' if add_schedule else 'ping'
    await send_embed(channel, f"Setting a {name} on `{calendar.day_name[weekday]}` at `{hour}:{minute}` with the "
                       f"following message:\n{msg}")


async def schedule_weekend(channel):
    await schedule_day(channel, calendar.day_name[4], 12)
    for day in range(5, 7):
        await schedule_day(channel, calendar.day_name[day], 9)


async def schedule_day(channel, day, start=0):
    await channel.send(f'```\n{day}\n```')

    times = [t for t in range(start, 21, 3)]

    for time in times:
        full_time = (
            f"{t_add(time, 0)} - {t_add(time, 3)} EST"
            f" | {t_add(time, 5)} - {t_add(time, 8)} UK"
            f" | {t_add(time, 6)} - {t_add(time, 9)} EU"
            f" | {t_add(time, 15)} - {t_add(time, 18)} JAP"
        )
        message = await send_embed(channel, full_time)
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')


def expand_arguments(args):
    args_expanded = []
    for arg in args:
        if arg == 'weekend':
            args_expanded.append(calendar.day_name[5])
            args_expanded.append(calendar.day_name[6])
            args_expanded.append(calendar.day_name[7])
        else:
            args_expanded.append(arg)
    return args_expanded


def t_add(time, to_add):
    result = (time + to_add) % 24
    return f"{result:02d}:00"


def setup(bot):
    bot.add_cog(ScheduleCog(bot))


class ScheduleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.taskscheck.start()

    def cog_unload(self):
        self.taskscheck.cancel()

    @tasks.loop(seconds=TASKS_LOOP_FREQ)
    async def taskscheck(self):
        now = timezone.get_localized_now()
        await check_pings(self.bot, now)

    @commands.command()
    async def addschedule(self, context, weekdayname='', hour='', minute='', *, args=''):
        await create_ping(context, weekdayname, hour, minute, args, True)

    @commands.command()
    async def addping(self, context, weekdayname='', hour='', minute='', *, args=''):
        await create_ping(context, weekdayname, hour, minute, args, False)

    @commands.command()
    async def schedule(self, context, *args):
        message = context.message
        channel = message.channel
        await message.delete()
        if args:
            for named_day in expand_arguments(args):
                await schedule_day(channel, named_day)
        else:
            await schedule_weekend(channel)

    @commands.command()
    async def listschedules(self, context):
        await show_pings(context, True)

    @commands.command()
    async def listpings(self, context):
        await show_pings(context, False)
