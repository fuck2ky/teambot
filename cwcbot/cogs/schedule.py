from discord.ext import commands
import discord
import calendar


class ScheduleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def schedule(self, context, *args):
        message = context.message
        await message.delete()
        if args:
            for named_day in expand_arguments(args):
                await self.schedule_day(context, named_day)
        else:
            await self.schedule_day(context, calendar.day_name[4], 12)
            for day in range(5, 7):
                await self.schedule_day(context, calendar.day_name[day], 9)

    async def schedule_day(self, context, day, start=0):
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

    def expand_arguments(self, args):
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
