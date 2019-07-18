import calendar
from datetime import datetime

import discord
from discord.ext import commands, tasks


class ScheduleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.practice.start()

    def cog_unload(self):
        self.practice.cancel()

    @commands.command(name='schedule', pass_context=True)
    async def schedule_match(self, context, *args):
        message = context.message
        await message.delete()
        if args:
            for named_day in expand_arguments(args):
                await schedule_day(context, named_day)
        else:
            await schedule_weekend(context)

    @tasks.loop(minutes=5.0)
    async def practice(self):
        from datetime import datetime
        from pytz import timezone
        tz = timezone('EST')
        now = datetime.now(tz)

        if self.is_practice_time(now):
            print(str(now) + f" triggering practice post")
            server = self.bot.get_guild(self.config['server_id'])
            tw_role = server.get_role(self.config['tw_role_id'])
            cw_role = server.get_role(self.config['cw_role_id'])

            msg = f"{tw_role.mention} {cw_role.mention} "
            msg += 'EU' if now.hour == 15 else 'US'
            msg += ' Practice time!'

            channel = self.bot.get_channel(
                self.config['practice_channel_id'])
            await channel.send(msg)

    def is_practice_time(self, now):
        return (now.weekday() == 1 or now.weekday() == 3) and (now.hour == 15 or now.hour == 19) and (0 <= now.minute <= 5)


# Module level functions
async def schedule_weekend(context):  # TODO switch from context to channel
    await schedule_day(context, calendar.day_name[4], 12)
    for day in range(5, 7):
        await schedule_day(context, calendar.day_name[day], 9)


async def schedule_day(context, day, start=0):
    await context.send(f'`{day}`')

    times = [t for t in range(start, 21, 3)]

    for time in times:
        full_time = (
            f"EST {t_add(time, 0)} - {t_add(time, 3)}"
            f" | UK  {t_add(time, 5)} - {t_add(time, 8)}"
            f" | EU  {t_add(time, 6)} - {t_add(time, 9)}"
            f" | JAP {t_add(time, 15)} - {t_add(time, 18)}"
        )
        message = await context.send(full_time)
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
