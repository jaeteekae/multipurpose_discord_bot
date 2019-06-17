# Work with Python 3.6
import discord
from discord.ext import commands
import logging

import random, json, os, pickle, time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import secret
import pdb
# pdb.set_trace()

logging.basicConfig(level=logging.INFO)

TOKEN = secret.TOKEN
PREFIX = "!"
AWAY_FILE = "./away.json"
data = {}

bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True)

def init():
    try:
        with open(AWAY_FILE,'r') as f:
            obj = json.load(f)
            data["away"] = obj
    except:
        data["away"] = {}

def write_to_disk():
    with open(AWAY_FILE,'w') as f:
        json.dump(data["away"],f)

def get_emoji(guild, name):
    emoji = discord.utils.get(guild.emojis, name=name)
    return str(emoji)

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

def send_away_msg(mem):
    obj = data["away"][str(mem.id)]
    elapsed = time.time()-obj["time"]
    timestring = generate_timestring(elapsed)

    el_delta = timedelta(seconds=elapsed)
    left_at = datetime.now() - el_delta
    since = left_at.strftime('**%I:%M%p** on %x')

    response = "**{}** is away!\n__Duration:__ {}\n__Since:__ {}\n__Message:__ {}".format(mem.display_name,timestring,since,obj["message"])
    return response

############ OUT OF OFFICE ############
@bot.command()
async def away(ctx, *args):
    if not args:
        response = '{}: plz supply a message so we know why you are away'.format(ctx.author.mention)
        await ctx.send(response)
        return
    else:
        args = " ".join(args)

    emoji = get_emoji(ctx.guild, "jin_kiss")
    response = ''
    memid = str(ctx.author.id)
    now = time.time()
    msg = str(args)

    obj = {"time": now, "message": msg}
    data["away"][memid] = obj

    response = 'Marking you away, {}, with the message *"{}"*\nWe will miss you {}'.format(ctx.author.mention, msg, emoji)
    await ctx.send(response)

@bot.command()
async def back(ctx):
    memid = str(ctx.author.id)

    if memid not in data["away"]:
        emoji = get_emoji(ctx.guild, "v_derp")
        response = "You weren't away, {} {}".format(ctx.author.mention, emoji)
        await ctx.send(response)
        return
    else:
        obj = data["away"].pop(memid)
        now = time.time()
        # elapsed in seconds
        elapsed = now - obj["time"]
        timestring = generate_timestring(elapsed)

        response = "Welcome back, {}!\nYou were away for: {}".format(ctx.author.mention, timestring)
        await ctx.send(response)

##### GENERAL MESSAGE HANDLING #####
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for ment in message.mentions:
        if str(ment.id) in data["away"]:
            await message.channel.send(send_away_msg(ment))

    await bot.process_commands(message)

init()

scheduler = BackgroundScheduler()
scheduler.add_job(write_to_disk, 'interval', hours=1)
scheduler.start()

bot.run(TOKEN)