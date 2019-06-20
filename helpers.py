from datetime import datetime
import discord

from data import data

def generate_timestring(elapsed):
    days, r = divmod(elapsed, 86400)
    hours, r = divmod(r, 3600)
    minutes, seconds = divmod(r, 60)

    timestring = ""
    if days:
        timestring += "**{:.0f}** days ".format(days)
    if hours:
        timestring += "**{:.0f}** hours ".format(hours)
    if minutes:
        timestring += "**{:.0f}** minutes ".format(minutes)
    if seconds:
        timestring += "**{:.0f}** seconds".format(seconds)

    return(timestring)

def remove_old_links():
    now = datetime.now()
    old = []
    for key, val in data.links.items():
        then = datetime.fromtimestamp(val)
        if (now-then).days>0:
            old.append(key)

    for link in old:
        data.links.pop(link)


def get_emoji(guild, name):
    emoji = discord.utils.get(guild.emojis, name=name)
    return str(emoji)