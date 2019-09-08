import discord


async def send_embed(sender, body):
    embed = discord.Embed(title=body, colour=discord.Colour.dark_blue())
    return await sender.send(embed=embed)
