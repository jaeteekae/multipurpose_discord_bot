# Work with Python 3.6
import discord
from discord.ext import commands
import logging

import os, time, validators
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import pdb

import settings
from helpers import *
from data import data
# pdb.set_trace()
if settings.PRODUCTION:
    logging.basicConfig(filename='data/logfile.txt',
                        filemode='a',
                        level=logging.INFO)
    cmdprefix = settings.PREFIX
elif settings.TESTING:
    logging.basicConfig(level=logging.INFO)
    cmdprefix = settings.TESTING_PREFIX

help_cmd = discord.ext.commands.DefaultHelpCommand(no_category="What can Apricot-Flower-Baby do for you")
bot = commands.Bot(command_prefix=cmdprefix, case_insensitive=True, help_command=help_cmd)

############ OUT OF OFFICE ############
def send_away_msg(mem):
    obj = data.away[str(mem.id)]
    elapsed = time.time()-obj["time"]
    timestring = generate_timestring(elapsed)

    el_delta = timedelta(seconds=elapsed)
    est_to_pst = timedelta(hours=3)
    left_at_est = datetime.now() - el_delta
    left_at_pst = left_at_est - est_to_pst
    since = left_at_est.strftime('**%I:%M%p EST** on %x or ')
    since += left_at_pst.strftime('**%I:%M%p PST** on %x')

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

    if "’" in message.content:
        message.content = message.content.replace("’","'")

    # check for away mentions
    for ment in message.mentions:
        if str(ment.id) in data.away:
            title,desc = send_away_msg(ment)
            emb = discord.Embed(title=title,description=desc,color=settings.AWAY_COLOR)
            await message.channel.send(embed=emb)

    # only do these if the message is sent from a server
    if message.guild:
        # check for links in general
        if message.channel.name == 'general':
            new_links = extract_new_links(message.content)
            link_channel = bot.get_channel(settings.LC_CHANNEL_ID)
            for l in new_links:
                await link_channel.send(l)
        # track stats
        if settings.PRODUCTION:
            data.track_message(str(message.channel.id),str(message.author.id))
            data.track_emoji(message.content)

    # execute prefix commands
    await bot.process_commands(message)

######## AUTODELETE FOR #RECEIPTS ########
@bot.event
async def on_reaction_add(reaction, user):
    if type(reaction.emoji) != str:
        data.track_emoji_react(reaction.emoji)

    if reaction.message.channel.id == settings.RECEIPTS_CHANNEL_ID:
        if reaction.emoji == '🗑':
            await reaction.message.delete()

    if reaction.emoji == '📌':
        await reaction.message.pin()

    if reaction.emoji == '🧾':
        if data.already_receipted(reaction.message.id):
            return
        else:
            data.add_receipt(reaction.message.id)
        reactors = await reaction.users().flatten()
        emb = receipt_message(message=reaction.message, text=reaction.message.content, author=reaction.message.author, receipter=reactors[0])
        r_channel = bot.get_channel(settings.RECEIPTS_CHANNEL_ID)
        await r_channel.send(embed=emb)

@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '📌':
        # don't unpin if there are still pin reacts on the msg
        for r in reaction.message.reactions:
            if r.emoji == '📌':
                return
        await reaction.message.unpin()

@bot.event
async def on_message_delete(message):
    if message.channel.id == settings.RECEIPTS_CHANNEL_ID:
        url = message.embeds[0].author.url
        msg_id = url[url.rfind('/')+1:]
        data.remove_receipt(int(msg_id))

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        await bot.process_commands(after)   

@bot.event
async def dm(ctx):
    await bot.process_commands(ctx)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == settings.MAIN_GUILD_NAME:
            main_guild = guild
            data.set_guild(main_guild)
    if not data.stats_initted:
        memb_stats = {}
        members = list(filter(lambda x: not x.bot, main_guild.members))
        for m in members:
            memb_stats[str(m.id)] = {}
        stats = {'hours': [{}],
                 'days':  [{}],
                 'all_time': memb_stats,
                 'emojis': {}}
        data.set_stats(stats)

if settings.PRODUCTION:
    scheduler = BackgroundScheduler()
    scheduler.add_job(data.write_to_disk, 'cron', minute='*/30')
    scheduler.add_job(data.turnover_stats, 'cron', hour=0, minute=1)
    scheduler.add_job(data.turnover_hour, 'cron', minute=59)
    scheduler.start()

extensions = ['cogs.gif_dictionary',
              'cogs.away',
              'cogs.birthdays',
              'cogs.stats',
              'cogs.convert',
              # 'cogs.osha',
              'cogs.praisebot',
              'cogs.bet',
              'cogs.receipt']

if __name__ == '__main__':
    for ext in extensions:
        bot.load_extension(ext)

bot.run(settings.TOKEN, bot=True, reconnect=True)


