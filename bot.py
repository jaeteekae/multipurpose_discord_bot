# Work with Python 3.6
import discord
from discord.ext import commands
import logging

import random, json, os, pickle, time, validators
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import pdb

from settings import *
from helpers import *
from data import data
# pdb.set_trace()

# logging.basicConfig(filename='data/logfile.txt',
#                     filemode='a',
#                     level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

help_cmd = discord.ext.commands.DefaultHelpCommand(no_category="What can Apricot-Flower-Baby do for you")
bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True, help_command=help_cmd)

def write_to_disk():
    remove_old_links()
    with open(AWAY_FILE,'w') as f:
        json.dump(data.away,f)
    with open(GIF_FILE,'w') as f:
        json.dump(data.gifs,f)
    with open(LINKS_FILE,'w') as f:
        json.dump(data.links,f)

############ OUT OF OFFICE ############
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


######### LINK EXTRACTION #########
# reposts new (not posted in the last 24 hrs) links from #gen to a links-only channel
def extract_new_links(text):
    pieces = text.split(' ')
    links = list(filter(lambda x: validators.url(x), pieces))
    without_imgs = list(filter(lambda x: (not is_image(x)) and ('tenor.com' not in x), links))
    #include credit?
    new_links = list(filter(lambda x: x not in data.links, without_imgs))

    nowts = datetime.now().timestamp()
    for l in new_links:
        data.links[l] = nowts

    return new_links

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

##### GENERAL MESSAGE HANDLING #####
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # check for away mentions
    for ment in message.mentions:
        if str(ment.id) in data.away:
            title,desc = send_away_msg(ment)
            emb = discord.Embed(title=title,description=desc,color=AWAY_COLOR)
            await message.channel.send(embed=emb)

    # check for links in general
    if message.channel.name == 'general':
        new_links = extract_new_links(message.content)
        link_channel = bot.get_channel(secret.LC_CHANNEL_ID)
        for l in new_links:
            await link_channel.send(l)

    # execute prefix commands
    await bot.process_commands(message)


scheduler = BackgroundScheduler()
scheduler.add_job(write_to_disk, 'interval', minutes=30)
scheduler.start()

extensions = ['cogs.gif_dictionary',
              'cogs.away']

if __name__ == '__main__':
    for ext in extensions:
        bot.load_extension(ext)

bot.run(TOKEN, bot=True, reconnect=True)


