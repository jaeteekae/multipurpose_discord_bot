import discord
from discord.ext import commands

from data import data
from settings import *
from helpers import *
from pprint import pprint


class Stats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.timewords = ['24', 'day', 'twenty', 'week', 'month', 'all']

	@commands.command(help="Get some stats, you nosy person", 
					  usage="[@person | #channel] [time]")
	async def stats(self, ctx, *args):
		error, resp = self.stats_error(args)
		if error:
			await ctx.send(resp)
			return

		resp = ''
		timedata, timestr = self.stats_for_time(args[1:])

		person = self.get_person(ctx, args)
		channel = self.get_channel(ctx, args)

		if person:
			calc = self.person_stats(person, timedata)
			resp = "{} has sent **{}** messages in the past **{}**".format(person.mention,str(calc),timestr)
		elif channel:
			calc = self.channel_stats(channel, timedata)
			resp = "There have been **{}** messages sent in {} in the past **{}**".format(str(calc), channel.mention, timestr)
		else:
			resp = "I couldn't figure out which channel or person you were looking for, {} :(".format(ctx.author.mention)

		await ctx.send(resp)

	def person_stats(self, person, timedata):
		calc = 0
		pid = str(person.id)
		for entry in timedata:
			if pid in entry:
				for ch, msgnum in entry[pid].items():
					calc += msgnum
		return(calc)

	def channel_stats(self, channel, timedata):
		calc = 0
		chid = str(channel.id)
		for entry in timedata:
			for chs in entry.values():
				for ch, msgnum in chs.items():
					if ch == chid:
						calc += msgnum
		return(calc)

	def stats_for_time(self, timeargs):
		time = ' '.join(timeargs)
		time = time.lower()

		if ('24' in time) or ('twenty' in time) or ('day' in time):
			return(data.stats['days'][-1:],time)
		elif 'week' in time:
			return(data.stats['days'][-7:],time)
		elif 'month' in time:
			return(data.stats['days'],time)
		elif 'all' in time:
			stats = data.stats['days'].copy()
			allt = data.stats['all_time'].copy()
			stats.append(allt)
			return(stats,time)

	def stats_error(self, args):
		if len(args)<2:
			resp = "You need to send me a person/channel and a time frame"
			return(True, resp)

		# check for a valid time frame
		for w in args[1:]:
			if w.lower() in self.timewords:
				return(False, '')
		resp = "You can only get stats for one of these time frames: `24 hours`, `1 week`, `1 month`, or `all time`"
		return(True, resp)

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

	def get_channel(self, ctx, args):
		channel = None
		if ctx.message.channel_mentions:
			channel = ctx.message.channel_mentions[0]
		else:
			name = args[0].lower()
			for ch in ctx.guild.channels:
				if ch.name == name:
					channel = ch
					break
		return channel


def setup(bot):
	bot.add_cog(Stats(bot))

