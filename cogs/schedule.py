import calendar
import pytz
import datetime
import tzlocal

import discord
from discord.ext import commands, tasks


CWC_META_SHEET = 'https://docs.google.com/spreadsheets/d/1n_9scATgcWFfoxNBWVQTZ8PALbaevAtCHfysQ1yM3EU/edit?usp=sharing'
TW_PREPARATION_SHEET = 'https://docs.google.com/spreadsheets/d/1o_wi1nGPKwZgiuUWkez8ObEth0Z2IwD5LhgWTTBIgJA/edit?usp=sharing'
CW_PREPARATION_SHEET = 'https://docs.google.com/spreadsheets/d/1AYYdV-W-MJpaasRjSfHHIHm8pOPWq-2Ee41IaJs8wEA/edit?usp=sharing'


class ScheduleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.cwcschedules.start()

    def cog_unload(self):
        self.cwcschedules.cancel()

    @commands.command(name='schedule', pass_context=True)
    async def schedule_match(self, context, *args):
        message = context.message
        channel = message.channel
        await message.delete()
        if args:
            for named_day in expand_arguments(args):
                await schedule_day(channel, named_day)
        else:
            await schedule_weekend(channel)

    @tasks.loop(minutes=5.0)
    async def cwcschedules(self):
        now = get_est_time()
        await self.check_practice_session(now)
        await self.check_match_schedule(now)

    async def check_practice_session(self, now):
        is_us_practice = (now.weekday() == 1 and now.hour == 19)
        is_eu_practice = (now.weekday() == 3 and now.hour == 15)

        if (is_us_practice or is_eu_practice) and is_hour_starting(now.minute):
            print(str(now) + f" triggering practice post")
            server = self.bot.get_guild(self.config['server_id'])
            tw_role = server.get_role(self.config['tw_roaster_role'])
            cw_role = server.get_role(self.config['cw_roaster_role'])

            msg = f"{tw_role.mention} {cw_role.mention} "
            msg += 'EU' if is_eu_practice else 'US'
            msg += ' Practice time!'
            msg += '\n\n Please join the call at: https://hangouts.google.com/call/QCQA0ehAWFu_nSYJAdzMAEEI'
            msg += '\n\n You can use the Google Sheet pinned in the TW and CW general channels to plan the next Match.\nWhile doing that, remember to keep an eye on our meta analysis sheet here: ' + CWC_META_SHEET
            msg += '\nYou can suggest modifications by adding comments on the sheet.'

            channel = self.bot.get_channel(self.config['practice_channel_id'])
            await channel.send(msg)

    async def check_match_schedule(self, now):
        is_match_schedule_time = (now.weekday() == 0 and now.hour == 0)

        if is_match_schedule_time and is_hour_starting(now.minute):
            print(str(now) + f" triggering schedule post")
            server = self.bot.get_guild(self.config['server_id'])

            tw_news = self.bot.get_channel(self.config['tw_news_channel'])
            tw_role = server.get_role(self.config['tw_roaster_role'])
            await schedule_weekend(tw_news)
            await tw_news.send(f"{tw_role.mention} please react according to your availability")

            cw_news = self.bot.get_channel(self.config['cw_news_channel'])
            cw_role = server.get_role(self.config['cw_roaster_role'])
            await schedule_weekend(cw_news)
            await cw_news.send(f"{cw_role.mention} please react according to your availability")


# Module level functions
def is_hour_starting(min):
    return (0 <= min <= 4)


def get_est_time():
    tz_name = tzlocal.get_localzone().zone
    local_tz = pytz.timezone(tz_name)
    local_time = local_tz.localize(datetime.datetime.now())
    est_tz = pytz.timezone('US/Eastern')
    return local_time.astimezone(est_tz)


async def schedule_weekend(channel):
    await schedule_day(channel, calendar.day_name[4], 12)
    for day in range(5, 7):
        await schedule_day(channel, calendar.day_name[day], 9)


async def schedule_day(channel, day, start=0):
    await channel.send(f'`{day}`')

    times = [t for t in range(start, 21, 3)]

    for time in times:
        full_time = (
            f"{t_add(time, 0)} - {t_add(time, 3)} EST"
            f" | {t_add(time, 5)} - {t_add(time, 8)} UK"
            f" | {t_add(time, 6)} - {t_add(time, 9)} EU"
            f" | {t_add(time, 15)} - {t_add(time, 18)} JAP"
        )
        message = await channel.send(full_time)
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
