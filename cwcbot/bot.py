#!/usr/bin/env python3.7

from discord.ext.commands import Bot
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cwcbot.events.base_event import Event
from cwcbot.events import *
import json
import os
import sys
import traceback


# Scheduler that will be used to manage events
sched = AsyncIOScheduler()


# Load configurations
dirname = os.path.dirname(__file__)
CONFIG_FILE_NAME = 'config.json'
config_file_path = os.path.abspath(f"{dirname}/../{CONFIG_FILE_NAME}")
with open(config_file_path) as config_file:
    config = json.load(config_file)


# Instantiate bot
print("\nLoading commands...")
initial_extensions = ['cwcbot.cogs.schedule']
client = Bot(command_prefix='!')
n_cmd = 0
for extension in initial_extensions:
    try:
        client.load_extension(extension)
        n_cmd += 1
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()
print(f"{n_cmd} commands loaded")


# Load all events
print("\nLoading events...")
n_ev = 0
for ev in Event.__subclasses__():
    event = ev()
    sched.add_job(event.run, 'interval', (client, config,),
                  seconds=event.interval_minutes)
    n_ev += 1
sched.start()
print(f"{n_ev} events loaded")


# Startup
@client.event
async def on_ready():
    print('\nLogged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def run_bot():
    client.run(config['token'])
