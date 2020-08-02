import calendar
import discord
from discord.ext import commands, tasks
from discord.utils import get

from cogs import timezone
from modules import persistence
from modules.utils import send_embed

TASKS_LOOP_FREQ = 60.0
TIMEZONE_DESCRIPTION = 'Times are in 24h format, EST timezone'


async def check_pings(bot):
    print('Checking pings.')
    pings = persistence.get_pings()
    for ping in pings:
        now = timezone.get_localized_now(ping['server_id'])
        if now.weekday() == ping['weekday'] and now.hour == ping['hour'] and now.minute == ping['minute']:
            await do_ping(bot, now, ping)


async def do_ping(bot, now, ping):
    print(str(now) + f" triggering ping #{ping.doc_id}")
    channel = bot.get_channel(ping['channel_id'])
    if ping['add_schedule'] is True:
        await schedule_weekend(channel)
    await channel.send(ping['message'])


def add_field(embed, ping):
    weekday = ping['weekday']
    hour = ping['hour']
    minute = ping['minute']
    message = ping['message']
    embed.add_field(
        name=f'`{ping.doc_id}` Every {calendar.day_name[weekday]} at {timezone.get_pretty_time(hour, minute)}',
        value=message,
        inline=False
    )


async def show_pings(context):
    print(f'Showing pings.')
    pings = persistence.get_pings(server_id=context.guild.id)
    pings_embed = discord.Embed(title=f'Configured pings', colour=discord.Colour.dark_blue())
    schedules_embed = discord.Embed(title=f'Configured schedule checks', colour=discord.Colour.dark_blue())
    for ping in pings:
        if ping['add_schedule']:
            add_field(schedules_embed, ping)
        else:
            add_field(pings_embed, ping)
    await context.send(embed=pings_embed)
    await context.send(embed=schedules_embed)


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
    await send_embed(channel, f"Setting a {name} on `{calendar.day_name[weekday]}` at "
                              f"`{timezone.get_pretty_time(hour, minute)}` with the following message:\n{msg}")


async def schedule_weekend(channel):
    await schedule_day(channel, calendar.day_name[4], 12)
    for day in range(5, 7):
        await schedule_day(channel, calendar.day_name[day], 9)


async def schedule_day(channel, day, start=0):
    day_message = await send_embed(channel, TIMEZONE_DESCRIPTION, day)
    time_emojis = filter(lambda em: em.name.startswith('schedule_'), channel.guild.emojis)
    time_emojis = sorted(time_emojis, key=lambda emoji: emoji.name)
    time_emojis = [time_emoji for time_emoji in time_emojis]
    if time_emojis:
        for time_emoji in time_emojis:
            await day_message.add_reaction(time_emoji)
        await day_message.add_reaction('\U0000274c')
    else:
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
            args_expanded.append(calendar.day_name[4])
            args_expanded.append(calendar.day_name[5])
            args_expanded.append(calendar.day_name[6])
        else:
            args_expanded.append(arg)
    return args_expanded


def t_add(time, to_add):
    result = (time + to_add) % 24
    return f"{result:02d}:00"


def setup(bot):
    bot.add_cog(Schedule(bot))


class Schedule(commands.Cog):
    """Commands used to manage pings and schedules"""
    def __init__(self, bot):
        self.bot = bot
        self.taskscheck.start()

    def cog_unload(self):
        self.taskscheck.cancel()

    @tasks.loop(seconds=TASKS_LOOP_FREQ)
    async def taskscheck(self):
        await check_pings(self.bot)

    @commands.command()
    async def addschedule(self, context, weekdayname='', hour='', minute='', *, args=''):
        """
        Creates a weekly schedule poll in the current channel.
        `weekdayname` can be a full week day name like "Monday" or an abbreviation like "wed", case insensitive
        `hour` is the hour of the day, in 24 hour format (0-23)
        `minute` is the minute of the hour (0-59)
        `args` is anything you'd like to include in the poll

        Examples:
        ```>addschedule monday 17 50 Please react with your availability for the match```
        ```>addschedule Wed 10 30 When you guys want to hangout today?```
        """
        await create_ping(context, weekdayname, hour, minute, args, True)

    @commands.command()
    async def addping(self, context, weekdayname='', hour='', minute='', *, args=''):
        """
        Creates a weekly ping in the current channel.
        `weekdayname` can be a full week day name like "Monday" or an abbreviation like "wed", case insensitive
        `hour` is the hour of the day, in 24 hour format (0-23)
        `minute` is the minute of the hour (0-59)
        `args` is anything you'd like to include in the ping

        Examples:
        ```>addping Tuesday 15 00 Practice session is starting!```
        ```>addping thu 19 30 It's this time of the day again```
        """
        await create_ping(context, weekdayname, hour, minute, args, False)

    @commands.command()
    async def schedule(self, context, *args):
        """
        Generates a manual schedule poll.
        If no arguments are provided, a schedule poll will be generated for each weekend day (Friday, Saturday, Sunday).
        Otherwise, you can provide a list of names separated by space for the schedules generated.
        To make a schedule name that includes spaces itself, just use normal quotes ""

        Examples:
        ```>schedule Monday Thursday Friday```
        ```>schedule Match Practice Meetup```
        ```>schedule "Match against X" "Internal tournament"```
        """
        message = context.message
        channel = message.channel
        await message.delete()
        if args:
            for named_day in expand_arguments(args):
                await schedule_day(channel, named_day)
        else:
            await schedule_weekend(channel)

    @commands.command()
    async def listpings(self, context):
        """Lists all the pings anche schedule checks configured in this server"""
        await show_pings(context)

    @commands.command()
    async def deleteping(self, context, ping_id):
        """Deletes a ping or schedule check, by passing it's ID as only parameter, as returned by `>listpings`"""
        if persistence.delete_ping(ping_id):
            await send_embed(context, f'Ping `{ping_id}` deleted.')
        else:
            await send_embed(context, f'Could not delete ping `{ping_id}`, did you type the ID correctly?')
