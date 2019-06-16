# Work with Python 3.6
import discord
from discord.ext import commands
import logging

import random, json, os, pickle, time
import secret
import pdb
    # pdb.set_trace()

logging.basicConfig(level=logging.INFO)

TOKEN = secret.TOKEN
PREFIX = '!'
DATA_FILE = './data.pkl'
data = {'away': {}}

bot = commands.Bot(command_prefix=PREFIX)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def away(ctx, *,args):
    response = ''
    now = time.time()
    msg = str(args)

    response = 'from: ' + ctx.author.mention + '\nmessage: ' + msg + '\ntime: ' + str(now)
    await ctx.send(response)
    print("achieved!")


bot.run(TOKEN)