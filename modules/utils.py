import logging

import discord


async def send_embed(sender, descr='', title=''):
    embed = discord.Embed(description=descr, colour=discord.Colour.dark_blue())
    if title:
        embed.title = title
    return await sender.send(embed=embed)


def log_command(command, context):
    author = context.message.author.name
    channel = context.message.channel
    server = context.message.guild
    logging.info("")
    logging.info(f'Command "{command}" used by "{author}" in channel "{channel}", server "{server}"')
