#!/usr/bin/env python3.7

from discord.ext.commands import Bot
from datetime import date
import calendar

client = Bot(command_prefix='!')


# Startup
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# Bot Commands
@client.command(pass_context=True)
async def schedule(context, *args):
    message = context.message
    await message.delete()
    if args:
        for named_day in expand_arguments(args):
            await schedule_day(context, named_day)
    else:
        today = date.today().weekday()
        for day in range(today, 7):
            await schedule_day(context, calendar.day_name[day])


# Functions
def run_bot():
    client.run('NTQyMTI2NTkyNjIxODA1NTc4.DzpfSg.0saF4oIL0KIuUdweQl-zXaC6cOc')


async def schedule_day(context, day):
    for time in ['Morning EST', 'Afternoon EST', 'Evening EST']:
        message = await context.send(f'{day} {time}')
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')


def expand_arguments(args):
    args_expanded = []
    for arg in args:
        if arg == 'weekend':
            args_expanded.append('Friday')
            args_expanded.append('Saturday')
            args_expanded.append('Sunday')
        else:
            args_expanded.append(arg)
    return args_expanded
