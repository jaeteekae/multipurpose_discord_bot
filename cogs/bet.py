import discord
from discord.ext import commands

from data import data
import settings, helpers


class Bet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Fancy a gamble?", 
                	  usage="<message_here>")
    async def bet(self, ctx, *args):
        pass

def setup(bot):
	bot.add_cog(Bet(bot))

