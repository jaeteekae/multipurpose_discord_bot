import time as tm
from datetime import datetime, timedelta, timezone, date
from datetime import time as dt_time
import discord
import json, os, re

from data import data
from settings import *
import validators
# import filetype


def is_image(url):
    _, ext = os.path.splitext(url)
    if not ext:
        return False
    ext = ext.lower()
    img_exts = ['jpeg','jpg','exif','gif','bmp','png','webp','hdr','img','ico','tif','tiff']
    for iext in img_exts:
        if iext in ext:
            return True
    return False

def extract_links(text):
    pieces = text.split()
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
    img_exts = ['.jpeg','.jpg','.exif','.gif','.bmp','.png','.webp','.hdr','.img','.ico','.tif','.tiff']
    msg_url = get_message_link(message)
    links = " ".join(extract_links(message.content))
    hasImg = False
    url = None

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
        if ext in img_exts:
            emb.set_image(url=url)
            hasImg = True

    if receipter:
        ft_txt = "🧾ed by {}".format(receipter.display_name)
        emb.set_footer(text=ft_txt, icon_url=receipter.avatar_url)

    if not hasImg and url:
        return links, emb, url
    else:
        return links, emb, None

def backspace(msg, start):
    while (msg[start] == ' '):
        start -= 1
    return start

# params are in KST
def time_from_now(hrs, min):
    tomorrow = date.today() + timedelta(days=1)
    timeobj = dt_time(hour=hrs,minute=min,tzinfo=timezone.utc)
    time_to_find = datetime.combine(tomorrow,timeobj)
    now_in_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    diff = time_to_find - now_in_kst
    while diff.days > 0:
        diff -= timedelta(days=1)

    result_hours = diff.seconds//3600
    diff -= timedelta(hours=result_hours)
    return str(result_hours) + " hours and " + str(diff.seconds//60) + " minutes"

# msg is the (all lowercase) string of message.content
def kst_converter(msg):
    kst_regex = re.compile(r"kst\b")
    noon_regex = re.compile(r"noon\b")
    midnight_regex = re.compile(r"midnight\b")
    match = kst_regex.search(msg)
    ret_string = ""
    add = 0

    while match:
        #compute
        start = match.start()

        if msg[match.start()-5:match.start()-1] == "noon":
            time = time_from_now(12,0)
            ret_string += "**" + msg[match.start()-5:match.end()] + "** is in **" + time + "**\n"
        elif msg[match.start()-9:match.start()-1] == "midnight":
            time = time_from_now(0,0)
            ret_string += "**" + msg[match.start()-9:match.end()] + "** is in **" + time + "**\n"
        elif (start == 0) or (msg[start-1] not in ['m',' ','1','2','3','4','5','6','7','8','9','0']):
            pass
        else:
            start = backspace(msg, start-1)
            if (msg[start] == 'm'):
                if (msg[start-1] == 'p'):
                    add = 12
                start -=2
            start = backspace(msg, start)
            if msg[start].isdecimal():
                enddec = start + 1
                while msg[start].isdecimal() or msg[start] == ":":
                    start -= 1
                start += 1
                timestr = msg[start:enddec]
                timestr = timestr.replace(":","")
                if (len(timestr) == 2) or (len(timestr) == 1):
                    time = time_from_now(int(timestr)+add,0)
                elif len(timestr) == 3:
                    time = time_from_now(int(timestr[:1])+add,int(timestr[1:]))                    
                elif len(timestr) == 4:
                    time = time_from_now(int(timestr[:2])+add,int(timestr[2:]))
                else:
                    return ""
                ret_string += "**" + msg[start:match.end()] + "** is in **" + time + "**\n"

        # look for more KST mentions
        msg = msg[match.end():]
        match = kst_regex.search(msg)
    
    return ret_string


async def reroute_bot_msg(msg):
    tries = 0

    # try 3 times to get embed
    while len(msg.embeds) == 0:
        if tries >= 3:
            return MODS_CHANNEL_ID, "failed: " + msg.content
        tm.sleep(1)
        msg = await msg.channel.fetch_message(msg.id)
        tries += 1

    emb = msg.embeds[0]

    # check for haru weverse translation
    if emb.author and emb.author.name and ("haru" in emb.author.name):
        possible_date = emb.description[:6]
        if possible_date.isdecimal():
            return OFFICIALBTS_CHANNEL_ID, msg.content
    
    # check for Hybe Labels youtube upload
    if emb.author and emb.author.name and ("HYBE LABELS" in emb.author.name):
        title = emb.title.lower()
        if "gfriend" in title:
            return GG_CHANNEL_ID, msg.content
        elif "seventeen" in title:
            return SVT_CHANNEL_ID, msg.content
        elif "txt" in title:
            return TXT_CHANNEL_ID, msg.content
        elif ("i-land" in title) or ("belift" in title) or ("enhypen" in title):
            return ILAND_CHANNEL_ID, msg.content
        elif "bts" in title:
            return OFFICIALBTS_CHANNEL_ID, "<@&586395910917980161> " + msg.content
        else:
            # if unknown, just post to #officialbts
            return OFFICIALBTS_CHANNEL_ID, msg.content

    # check for BigHit twitter upload & weed out spam
    if emb.author and emb.author.name and ("@BIGHIT_MUSIC" in emb.author.name):
        #         article, broadcast
        ignore = ["[기사]", "[방송]"]
        for i in ignore:
            if i in emb.description:
                return None, None
        if "#BTS" in emb.description:
            return OFFICIALBTS_CHANNEL_ID, "<@&586395910917980161> " + msg.content
        elif "#TOMORROW_X_TOGETHER" in emb.description:
            return TXT_CHANNEL_ID, msg.content
        else:
            return OFFICIALBTS_CHANNEL_ID, msg.content

    # print("Embed Title: ", emb.title)
    # print("Embed description: ", emb.description)
    # print("Embed url: ", emb.url)
    # print("Embed footer: ", emb.footer)
    # print("Embed author: ", emb.author)
    # print("Embed author name: ", emb.author.name)
    # print("\n\n")
    return None, None


async def repost_link_bot_msg(msg):
    tries = 0

    # try 3 times to get embed
    while len(msg.embeds) == 0:
        if tries >= 3:
            return MODS_CHANNEL_ID, "failed: " + msg.content
        tm.sleep(1)
        msg = await msg.channel.fetch_message(msg.id)
        tries += 1

    emb = msg.embeds[0]

    # check for @BTS_BigHit
    if emb.author and emb.author.name and ("@bts_bighit" in emb.author.name):
        sanitized = emb.description.replace('(','').replace(')','')
        links = "\n".join(extract_links(sanitized))
        if links:
            return OFFICIALBTS_CHANNEL_ID, links
    
    return None, None


async def change_role_color(msg, author):
    code = msg.content
    role = msg.author.roles[-1]

    if len(code) not in [6,7]:
        return None, None
    if len(code) == 7:
        code = code[1:]

    old_color_int = role.color.value
    new_color_int = int("0x"+code, 16)
    old_color_string = "#"+str(hex(old_color_int)[2:])
    new_color_string = "#"+str(code)

    await role.edit(colour=new_color_int)
    ch_msg = "Successfully changed role color to {}".format(new_color_string)

    emb1 = discord.Embed(description=old_color_string, color=old_color_int)
    emb2 = discord.Embed(description=new_color_string, color=new_color_int)
    await author.send(content="**Changed role color from:**", embed=emb1)
    await author.send(content="**to**", embed=emb2)

    return ch_msg




