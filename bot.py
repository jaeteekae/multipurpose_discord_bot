# Work with Python 3.6
import discord
from discord.ext import commands
import logging

import os, time, validators
from datetime import datetime, timedelta
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

    # only do these if the message is sent from a server
    if message.guild:
        # check for links in general
        if message.channel.name == 'general':
            new_links = extract_new_links(message.content)
            link_channel = bot.get_channel(LC_CHANNEL_ID)
            for l in new_links:
                await link_channel.send(l)
        # track stats
        # data.track_message(str(message.channel.id),str(message.author.id))

    # execute prefix commands
    await bot.process_commands(message)

######## AUTODELETE FOR #RECEIPTS ########
@bot.event
async def on_reaction_add(reaction, user):
    if type(reaction.emoji) != str:
        return

    if reaction.message.channel.id == RECEIPTS_CHANNEL_ID:
        if reaction.emoji == '🗑':
            await reaction.message.delete()

    if reaction.emoji == '📌':
        await reaction.message.pin()

@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '📌':
        await reaction.message.unpin()

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        await bot.process_commands(after)

@bot.event
async def dm(ctx):
    await bot.process_commands(ctx)

@bot.event
async def on_ready():
    if not data.stats_initted:
        stats = {'days': [{}],
                 'all_time': {}}
        data.set_stats(stats)


scheduler = BackgroundScheduler()
scheduler.add_job(data.write_to_disk, 'interval', minutes=30)
scheduler.start()

extensions = ['cogs.gif_dictionary',
              'cogs.away',
              'cogs.birthdays',
              'cogs.stats']

if __name__ == '__main__':
    for ext in extensions:
        bot.load_extension(ext)

bot.run(TOKEN, bot=True, reconnect=True)


