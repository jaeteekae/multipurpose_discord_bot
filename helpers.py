from datetime import datetime
import discord
import json, os

from data import data
from settings import *


def is_image(url):
    _, ext = os.path.splitext(url)
    if not ext:
        return False
    ext = ext.lower()
    img_exts = ['jpeg','exif','gif','bmp','png','webp','hdr','img','jpg','ico','tif']
    for iext in img_exts:
        if iext in ext:
            return True
    return False

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

def get_emoji(guild, name):
    emoji = discord.utils.get(guild.emojis, name=name)
    return str(emoji)

