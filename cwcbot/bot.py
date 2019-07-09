#!/usr/bin/env python3.7

from discord.ext.commands import Bot
from datetime import date
import json
import os
import sys
import traceback


# Load configurations
CONFIG_FILE_NAME = 'config.json'
config_file_path = os.path.abspath(CONFIG_FILE_NAME)
with open(config_file_path) as config_file:
    config = json.load(config_file)


# Instantiate bot
initial_extensions = ['cwcbot.cogs.schedule']
client = Bot(command_prefix='!')
for extension in initial_extensions:
    try:
        client.load_extension(extension)
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()


# Startup
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def run_bot():
    client.run(config['token'])
