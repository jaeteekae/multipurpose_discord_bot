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
    if emoji:
        return str(emoji)
    else:
        return ''

def get_emoji_by_id(guild, eid):
    emoji = discord.utils.get(guild.emojis, id=eid)
    if emoji:
        return str(emoji)
    else:
        return ''

def get_message_link(msg):
    return "http://discordapp.com/channels/" + str(msg.guild.id) + "/" + str(msg.channel.id) + "/" + str(msg.id)

def receipt_message(message, text, author=None, receipter=None):
    msg_url = get_message_link(message)

    emb = discord.Embed(description=text, color=RECEIPT_COLOR)

    if author:
        auth = author.display_name + " in #" + message.channel.name + ":"
        emb.set_author(name=auth, icon_url=author.avatar_url, url=msg_url)
    else:
        auth = "Posted in #" + message.channel.name + ":"
        emb.set_author(name=auth, url=msg_url)

    if message.attachments:
        url = message.attachments[0].url
        emb.set_image(url=url)

    if receipter:
        ft_txt = "🧾ed by {}".format(receipter.display_name)
        emb.set_footer(text=ft_txt, icon_url=receipter.avatar_url)

    return emb






