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
		person = self.get_person(ctx, args)
		if not person:
			await ctx.send('Who dat {}'.format(get_emoji(ctx.guild, 'jm_judge')))
			return

		resp = '💥🚨💥🚨💥🚨💥🚨💥\n👮‍♀️ HANDS UP, {} 👮‍♀️\n💥🚨💥🚨💥🚨💥🚨💥'.format(person.mention)
		desc = 'There have been **{}** since the last incident.\nPrevious record: **{}**'.format('0 days','0 days')
		emb = discord.Embed(description=desc, color=settings.OSHA_COLOR)
		await ctx.send(resp,embed=emb)

	def get_person(self, ctx, args):
		person = None
		if ctx.message.mentions:
			person = ctx.message.mentions[0]
		else:
			name = args[0].lower()
			for per in ctx.guild.members:
				if per.display_name.lower() == name:
					person = per
					break
		return person


def setup(bot):
	bot.add_cog(OSHA(bot))