import discord


async def send_embed(sender, descr='', title=''):
    embed = discord.Embed(description=descr, colour=discord.Colour.dark_blue())
    if title:
        embed.title = title
    return await sender.send(embed=embed)
