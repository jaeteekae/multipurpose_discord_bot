# Work with Python 3.6
import discord
from discord.ext import commands
import logging

import os, time, validators
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import pdb, re

import settings
from helpers import *
from data import data, session
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
bot.shh = False
bot.fish_regex = re.compile(r"\bfish")
bot.kst_regex = re.compile(r"kst\b")

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

##### GENERAL MESSAGE HANDLING #####
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "’" in message.content:
        message.content = message.content.replace("’","'")

    if "\"" in message.content:
        message.content = message.content.replace("\"","^")

    if settings.PRODUCTION:
        lowered = message.content.lower()

        # if bot.shh:
        #     shher = bot.get_cog('Shh')
        #     if (await shher.unnacceptable_msg(message)):
        #         await message.delete()

        if bot.fish_regex.search(lowered):
            await message.channel.send("👮‍♀️ You seem to have said **_fish_** when you meant **_swim thing_**.\nPlease don't make this mistake again.")

        # reroute notifs
        if settings.LC_CHANNEL_ID == message.channel.id:
            chn_id, msg = await reroute_bot_msg(message)
            if msg:
                chn = bot.get_channel(int(chn_id))
                await chn.send(msg)

        # change color
        if settings.ROLES_CHANNEL_ID == message.channel.id:
            ch_msg = await change_role_color(message, message.author)
            if ch_msg:
                sent = await message.channel.send(ch_msg)
            else:
                sent = await message.channel.send("I don't know what that is. Just send a hex code")
            time.sleep(3)
            await sent.delete()
            await message.delete()
            return

        # kst bot - off
        # if bot.kst_regex.search(lowered):
        #     msg = kst_converter(lowered)
        #     if msg:
        #         await message.channel.send(msg)

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
            data.track_message(str(message.channel.id),str(message.author.id))
            data.track_emoji(message.content)

    # execute prefix commands
    await bot.process_commands(message)

######## AUTODELETE FOR #RECEIPTS ########
@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.is_custom_emoji():
        data.track_emoji_react(payload.emoji)
        return

    chan = bot.get_channel(payload.channel_id)
    msg = await chan.fetch_message(payload.message_id)

    if payload.channel_id == settings.RECEIPTS_CHANNEL_ID:
        if str(payload.emoji) == '🗑':
            await msg.delete()

    if str(payload.emoji) == '📌':
        await msg.pin()

    elif (str(payload.emoji) == '🧾') or (str(payload.emoji) == '📸'):
        if data.already_receipted(payload.message_id):
            return
        else:
            data.add_receipt(payload.message_id)
        text, emb, vid = receipt_message(message=msg, text=msg.content, author=msg.author, receipter=payload.member)
        r_channel = bot.get_channel(settings.RECEIPTS_CHANNEL_ID)
        await r_channel.send(embed=emb)
        if text:
            await r_channel.send(text)
        if vid:
            await r_channel.send(vid)

@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.emoji) == '📌':
        chan = bot.get_channel(payload.channel_id)
        msg = await chan.fetch_message(payload.message_id)
        # don't unpin if there are still pin reacts on the msg
        for r in msg.reactions:
            if r.emoji == '📌':
                return
        await msg.unpin()

@bot.event
async def on_raw_message_delete(payload):
    if payload.channel_id == settings.RECEIPTS_CHANNEL_ID:
        chan = bot.get_channel(payload.channel_id)
        message = await chan.fetch_message(payload.message_id)
        url = message.embeds[0].author.url
        msg_id = url[url.rfind('/')+1:]
        data.remove_receipt(int(msg_id))

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        await bot.process_commands(after)  

@bot.event
async def on_member_update(before, after):
    bday_role = data.guild.get_role(716014074009485332)
    if (bday_role in before.roles) and (bday_role not in after.roles):
        bday_channel = bot.get_channel(settings.BIRTHDAY_CHANNEL_ID)
        await bday_channel.send("{} is gone... for now 👀".format(after.display_name))
    if (bday_role not in before.roles) and (bday_role in after.roles):
        bday_channel = bot.get_channel(settings.BIRTHDAY_CHANNEL_ID)
        await bday_channel.send("{} HAS ARRIVED 🥳".format(after.display_name))

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
    scheduler.add_job(data.write_to_disk, 'cron', minute='*/5')
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


