from datetime import datetime
import discord
import json, os

from data import data
from settings import *
import validators


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

def extract_links(text):
    pieces = text.split(' ')
    links = list(filter(lambda x: validators.url(x), pieces))
    without_imgs = list(filter(lambda x: (not is_image(x)) and ('tenor.com' not in x), links))
    return without_imgs

def extract_new_links(text):
    all_links = extract_links(text)
    #include credit?
    new_links = list(filter(lambda x: x not in data.links, all_links))

    nowts = datetime.now().timestamp()
    for l in new_links:
        data.links[l] = nowts

    return new_links

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
    links = " ".join(extract_links(message.content))
    hasVideo = False

    emb = discord.Embed(description=text, color=RECEIPT_COLOR)

    if author:
        auth = author.display_name + " in #" + message.channel.name + ":"
        emb.set_author(name=auth, icon_url=author.avatar_url, url=msg_url)
    else:
        auth = "Posted in #" + message.channel.name + ":"
        emb.set_author(name=auth, url=msg_url)

    if message.attachments:
        url = message.attachments[0].url
        _, ext = os.path.splitext(url)
        ext = ext.lower()
        if ext != ".mov":
            emb.set_image(url=url)
        else:
            hasVideo = True

    if receipter:
        ft_txt = "🧾ed by {}".format(receipter.display_name)
        emb.set_footer(text=ft_txt, icon_url=receipter.avatar_url)

    if hasVideo:
        return links, emb, url
    else:
        return links, emb, None


