import discord
from discord.ext import commands

from data import data
from settings import *
from helpers import *


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Get some stats, you nosy person", 
                	  usage="[@person | #channel] [time]")
    async def stats(self, ctx, *args):
    	pass

def setup(bot):
	bot.add_cog(Stats(bot))

