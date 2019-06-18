# Work with Python 3.6
import discord
from discord.ext import commands
import logging

import random, json, os, pickle, time, requests, validators
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import secret
import pdb
# pdb.set_trace()

logging.basicConfig(level=logging.INFO)

TOKEN = secret.TOKEN
PREFIX = "!"

AWAY_FILE = "data/away.json"
AWAY_COLOR = 0x72FF7B

BDAY_FILE = "data/bdays.json"
BDAY_COLOR = 0x494ce5

GIF_FILE = "data/gif_shortcuts.json"
GIF_FOLDER = "gifs"

help_cmd = discord.ext.commands.DefaultHelpCommand(no_category="What can Apricot-Flower-Baby do for you")
bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True, help_command=help_cmd)

class DataObj:
    away = {}
    bdays = {}
    gifs = {}

    def __init__(self):
        try:
            with open(AWAY_FILE,'r') as f:
                obj = json.load(f)
                self.away = obj
        except:
            pass

        try:
            with open(GIF_FILE,'r') as f:
                obj = json.load(f)
                self.gifs = obj
        except:
            pass

        with open(BDAY_FILE,'r') as f:
            obj = json.load(f)
            self.bdays = obj

data = DataObj()

def write_to_disk():
    with open(AWAY_FILE,'w') as f:
        json.dump(data.away,f)
    with open(GIF_FILE,'w') as f:
        json.dump(data.gifs,f)

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

############ OUT OF OFFICE ############
class Out_of_Office(commands.Cog, name="Out of Office"):
    @bot.command(help="Set yourself away for when people mention you in chat", 
                 usage="<message_here>")
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
        data.away[memid] = obj

        response = 'Marking you away, {}, with the message *"{}"*\nWe will miss you {}'.format(ctx.author.mention, msg, emoji)
        await ctx.send(response)

    @bot.command(help="Use to stop being away")
    async def back(ctx, *args):
        memid = str(ctx.author.id)

        if memid not in data.away:
            emoji = get_emoji(ctx.guild, "v_derp")
            response = "You weren't away, {} {}".format(ctx.author.mention, emoji)
            await ctx.send(response)
            return
        else:
            obj = data.away.pop(memid)
            now = time.time()
            # elapsed in seconds
            elapsed = now - obj["time"]
            timestring = generate_timestring(elapsed)

            msg = "Welcome back, {}!".format(ctx.author.mention)
            desc = "__You were away for__: {}\n __You are no longer__: {}\n👋".format(timestring,obj["message"])
            emb = discord.Embed(description=desc,color=AWAY_COLOR)
            await ctx.send(msg,embed=emb)

def send_away_msg(mem):
    obj = data.away[str(mem.id)]
    elapsed = time.time()-obj["time"]
    timestring = generate_timestring(elapsed)

    el_delta = timedelta(seconds=elapsed)
    left_at = datetime.now() - el_delta
    since = left_at.strftime('**%I:%M%p** on %x')

    titletxt = "**{}** is away!".format(mem.display_name)
    responsetxt = "__Duration__: {}\n__Since__: {}\n__Message__: {}\n🏃‍♀️".format(timestring,since,obj["message"])
    return(titletxt, responsetxt)

######## BIRTHDAYS ########
@bot.command(help="Check the next birthday in the chat")
async def birthday(ctx, *args):
    today = datetime.today()
    this_year = today.year
    this_month = today.month
    this_day = today.day
    sumthisday = 31*this_month+this_day
    closest_bday = [12,31,365]

    for person in data.bdays:
        dob = person['dob'].split('/')
        mon = int(dob[0])
        day = int(dob[1])
        sumdays = 31*mon+day
        diff = sumdays-sumthisday

        # is a contender
        if diff>0 and diff<closest_bday[2]:
            closest_bday[0] = mon
            closest_bday[1] = day
            closest_bday[2] = diff

    for person in data.bdays:
        dob = person['dob'].split('/')
        mon = int(dob[0])
        day = int(dob[1])
        if (mon*31+day)-sumthisday>0:
            yr = this_year
        else:
            yr = this_year+1
        datestr = date(yr,mon,day).strftime('On %A, %B %d')

        if mon==closest_bday[0] and day==closest_bday[1]:

            msg = "🎊 The next birthday is " + person['name'] + "'s! 🎊\n" + datestr
            emb = discord.Embed(description=msg,color=BDAY_COLOR)
            await ctx.send(embed=emb)


######### GIF DICTIONARY #########
class Gif_Dictionary(commands.Cog, name="Gif Dictionary"):
    @bot.command(name="gif-add",
                 help="Add a gif (or image) to the gif dictionary", 
                 usage="<shortcut> <uploaded file OR URL>")
    async def gif_add(ctx, *args):
        if not args:
            await ctx.send("{}, plz resend & let me know what I should call this gif".format(ctx.author.mention))
            return

        shortcut = args[0]
        url = ''

        if len(shortcut)>20:
            await ctx.send("{}, the shortcut `{}` is too long. Plz resend with shortcut under 20 characters".format(ctx.author.mention, shortcut))
            return

        # check if shortcut already exists
        if shortcut in data.gifs:
            await ctx.send("{}, the shortcut `{}` is already in use. Plz resend with a different one".format(ctx.author.mention, shortcut))
            return
            
        # img is attached
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        # img is a link
        else:
            if len(args)<2 or not validators.url(args[1]):
                await ctx.send("{}, it looks like you didnt send me a gif to save :(".format(ctx.author.mention))
                return
            url = args[1]

        # download img
        _, ext = os.path.splitext(url)
        img_data = requests.get(url).content
        path = os.path.join(GIF_FOLDER,shortcut+ext)
        with open(path, 'wb') as f:
            f.write(img_data)

        # add img to dictionary
        data.gifs[shortcut] = path

        await ctx.send("Success! Added `{}` to the Gif Dictionary".format(shortcut))

    @bot.command(name="gif-list",
                 help="See the gifs already in the gif dictionary", 
                 usage="[optional prefix]")
    async def gif_list(ctx, *args):
        if args:
            pref = args[0]
            msg = 'All gifs that start with '
        else:
            pref = ''

        shortcuts = data.gifs.keys()
        filtered = filter(lambda x: x.startswith(pref), shortcuts)
        filtered.sort()


##### GENERAL MESSAGE HANDLING #####
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for ment in message.mentions:
        if str(ment.id) in data.away:
            title,desc = send_away_msg(ment)
            emb = discord.Embed(title=title,description=desc,color=AWAY_COLOR)
            await message.channel.send(embed=emb)

    await bot.process_commands(message)


scheduler = BackgroundScheduler()
scheduler.add_job(write_to_disk, 'interval', hours=1)
scheduler.start()

bot.run(TOKEN)