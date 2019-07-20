import discord
from discord.ext import commands

import settings
from data import data
from helpers import *
from datetime import datetime


class OSHA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="osha-violation",
                     help="Report an OSHA violation 👮‍♀️", 
                     usage="<@person>")
    async def osha_violation(self, ctx, *args):
    	return

def setup(bot):
	bot.add_cog(OSHA(bot))