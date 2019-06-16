# Work with Python 3.6
import discord
from discord.ext import commands

import random
import json
import os, pickle
from datetime import datetime
import pdb

TOKEN = 'NTg3MDkwNzgxNTEzNDQ5NDgy.XQKnvQ.q_zoIIrSZBql0ODzUkRE0Ov3Zsk'
PREFIX = '!'
DATA_FILE = './data.pkl'
data = {'away': {}}

#### INIT DATA STRUCTURE ####
if os.path.isfile(DATA_FILE):
    f = open(DATA_FILE, 'rb')
    data = pickle.load(f)
    f.close()

#### BOT ####
client = commands.Bot(command_prefix=PREFIX)

@client.command(name='ping')
async def ping():
    await client.say('pong')


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely',
    ]
    await client.say(random.choice(possible_responses) + ", " + context.message.author.mention)



############ OUT OF OFFICE ############
@client.command(name='away',
                pass_context=True)
async def go_away(context):
    pdb.set_trace()
    print(context.message)
    print(context.author)
    await client.say("goodbye")

@client.command(name='back',
                pass_context=True)
async def come_back(context):
    await client.say("welcome back")


client.run(TOKEN)

'''
client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
'''