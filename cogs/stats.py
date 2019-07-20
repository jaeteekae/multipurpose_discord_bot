import discord
from discord.ext import commands

from data import data
from helpers import *
import settings

class MyPerson():
	def __init__(self, id, mention):
		self.id = id
		self.mention = mention
		self.display_name = mention

class MyClass():
	def __init__(self, id, mention):
		self.id = id
		self.mention = mention
		self.display_name = mention

class Stats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.timewords = ['24', 'day', 'twenty', 'week', 'month', 'all', 'alltime', 'all-time']

	@commands.command(help="Get some stats, you nosy person\nTime can be 24 hours, 1 week, 1 month, or all time\nExamples:\n\t!stats @Jules 24 hours\n\t!more-stats #general 1 week\n\t!most-stats everyone 1 month\n\t!stats channels all time", 
					  usage="<@person|#channel|people|channels> <time>")
	async def stats(self, ctx, *args):
		resp, emb = self.message_handle(ctx, args, self.person_stats, self.channel_stats)
		await ctx.send(resp,embed=emb)

	@commands.command(name="more-stats",
					  aliases=['stats-more'],
					  help="Get MORE stats, you nosier person\nTime can be 24 hours, 1 week, 1 month, or all time\nExamples:\n\t!stats @Jules 24 hours\n\t!more-stats #general 1 week\n\t!most-stats everyone 1 month\n\t!stats channels all time", 
					  usage="<@person|#channel|people|channels> <time>")
	async def stats_more(self, ctx, *args):
		resp, emb = self.message_handle(ctx, args, self.person_stats_top_5, self.channel_stats_top_5)
		await ctx.send(resp,embed=emb)

	@commands.command(name="most-stats",
					  aliases=['stats-most'],
					  help="Get the most stats, you nosiest person\nTime can be 24 hours, 1 week, 1 month, or all time\nExamples:\n\t!stats @Jules 24 hours\n\t!more-stats #general 1 week\n\t!most-stats everyone 1 month\n\t!stats channels all time", 
					  usage="<@person|#channel|people|channels> <time>")
	async def stats_most(self, ctx, *args):
		resp, emb = self.message_handle(ctx, args, self.person_stats_all, self.channel_stats_all)
		await ctx.send(resp,embed=emb)

	def message_handle(self, ctx, args, pers_func, chan_func):
		args = list(args)
		error, resp = self.stats_error(args)
		if error:
			return(resp, None)

		resp = ''
		emb = None
		timedata, timestr = self.stats_for_time(args[1:])

		person = self.get_person(ctx, args)
		channel = self.get_channel(ctx, args)

		if person:
			resp,emb = pers_func(person, timedata, timestr)
		elif channel:
			resp,emb = chan_func(channel, timedata, timestr)
		else:
			resp = "I couldn't figure out which channel or person you were looking for, {} :(".format(ctx.author.mention)
		return(resp,emb)

	def person_stats(self, person, timedata, timestr):
		calc = 0
		pid = str(person.id)
		for entry in timedata:
			if pid == '*':
				for chs in entry.values():
					for msgnum in chs.values():
						calc += msgnum
			elif pid in entry:
				for ch, msgnum in entry[pid].items():
					calc += msgnum
		resp = "{} has sent **{}** messages in the past **{}**".format(person.mention,str(calc),timestr)
		emb = discord.Embed(description=resp,color=settings.STATS_COLOR)
		return('', emb)

	def channel_stats(self, channel, timedata, timestr):
		calc = 0
		chid = str(channel.id)
		for entry in timedata:
			for chs in entry.values():
				for ch, msgnum in chs.items():
					if (ch == chid) or (chid == '*'):
						calc += msgnum
		resp = "There have been **{}** messages sent in {} in the past **{}**".format(str(calc), channel.mention, timestr)
		emb = discord.Embed(description=resp,color=settings.STATS_COLOR)
		return('', emb)

	def person_stats_top_5(self, person, timedata, timestr):
		desc = ''
		pid = str(person.id)
		pdata = {}
		for entry in timedata:
			if pid in entry:
				for ch, msgnum in entry[pid].items():
					if ch in pdata:
						pdata[ch] += msgnum
					else:
						pdata[ch] = msgnum
			elif pid == '*':
				for chs in entry.values():
					for ch, msgnum in chs.items():
						if ch in pdata:
							pdata[ch] += msgnum
						else:
							pdata[ch] = msgnum

		datalist = list(pdata.items())
		datalist.sort(key=lambda x: x[1],reverse=True)

		for x in range(5):
			if x >= len(datalist):
				break
			ch, num = datalist[x]
			line = '<#{}>: **{}** messages\n'.format(ch, str(num))
			desc += line

		resp = "These are **{}**'s top 5 channels in the past **{}**:".format(person.display_name,timestr)
		emb = discord.Embed(description=desc,color=settings.STATS_COLOR)
		return(resp, emb)

	def channel_stats_top_5(self, channel, timedata, timestr):
		desc = ''
		chid = str(channel.id)

		pdata = {}
		for entry in timedata:
			for pid in entry:
				for ch, msgnum in entry[pid].items():
					if (ch == chid) or (chid == '*'):
						if pid in pdata:
							pdata[pid] += msgnum
						else:
							pdata[pid] = msgnum
		datalist = list(pdata.items())
		datalist.sort(key=lambda x: x[1],reverse=True)

		for x in range(5):
			if x >= len(datalist):
				break
			pid, num = datalist[x]
			line = '<@{}>: **{}** messages\n'.format(pid, str(num))
			desc += line

		resp = "These are the top 5 posters to **{}** in the past **{}**:".format(channel.mention,timestr)
		emb = discord.Embed(description=desc,color=settings.STATS_COLOR)
		return(resp, emb)

	# I'd like to personally apologize to my professors for copying this code
	def person_stats_all(self, person, timedata, timestr):
		desc = ''
		pid = str(person.id)
		pdata = {}
		for entry in timedata:
			if pid in entry:
				for ch, msgnum in entry[pid].items():
					if ch in pdata:
						pdata[ch] += msgnum
					else:
						pdata[ch] = msgnum
			elif pid == '*':
				for chs in entry.values():
					for ch, msgnum in chs.items():
						if ch in pdata:
							pdata[ch] += msgnum
						else:
							pdata[ch] = msgnum
		datalist = list(pdata.items())
		datalist.sort(key=lambda x: x[1],reverse=True)

		for (ch,num) in datalist:
			line = '<#{}>: **{}** messages\n'.format(ch, str(num))
			desc += line

		resp = "This is **{}**'s channel activity in the past **{}**:".format(person.display_name,timestr)
		emb = discord.Embed(description=desc,color=settings.STATS_COLOR)
		return(resp, emb)

	def channel_stats_all(self, channel, timedata, timestr):
		desc = ''
		chid = str(channel.id)

		pdata = {}
		for entry in timedata:
			for pid in entry:
				for ch, msgnum in entry[pid].items():
					if (ch == chid) or (chid == '*'):
						if pid in pdata:
							pdata[pid] += msgnum
						else:
							pdata[pid] = msgnum
		datalist = list(pdata.items())
		datalist.sort(key=lambda x: x[1],reverse=True)

		for (pid,num) in datalist:
			line = '<@{}>: **{}** messages\n'.format(pid, str(num))
			desc += line

		resp = "These are all the posters to **{}** in the past **{}**:".format(channel.mention,timestr)
		emb = discord.Embed(description=desc,color=settings.STATS_COLOR)
		return(resp, emb)

	def stats_for_time(self, timeargs):
		time = ' '.join(timeargs)
		time = time.lower()

		if ('24' in time) or ('twenty' in time) or ('day' in time):
			return(data.stats['hours'][-24:],time)
		elif 'week' in time:
			return(data.stats['days'][-7:],time)
		elif 'month' in time:
			return(data.stats['days'],time)
		elif ('all' in time) or ('alltime' in time) or ('all-time' in time):
			stats = data.stats['days'].copy()
			allt = data.stats['all_time'].copy()
			stats.append(allt)
			return(stats,time)

	def stats_error(self, args):
		if len(args)<1:
			resp = "You need to send me a person/channel and a time frame\n**Examples**:\n\t`!stats @Jules 24 hours`\n\t`!more-stats #general 1 week`\n\t`!most-stats everyone 1 month`\n\t`!stats channels all time`"
			return(True, resp)

		# default to 1 day if no time argument is supplied
		if len(args)<2:
			args.append('24')
			args.append('hours')

		# check for a valid time frame
		for w in args[1:]:
			if w.lower() in self.timewords:
				return(False, '')
		resp = "You can only get stats for one of these time frames: `24 hours`, `1 week`, `1 month`, or `all time`"
		return(True, resp)

	def get_person(self, ctx, args):
		person = None
		name = args[0].lower()
		if ctx.message.mentions:
			person = ctx.message.mentions[0]
		elif name == 'channels':
			person = MyClass('*','Everyone')
		else:
			for per in ctx.guild.members:
				if per.display_name.lower() == name:
					person = per
					break
		return person

	def get_channel(self, ctx, args):
		channel = None
		name = args[0].lower()
		if ctx.message.channel_mentions:
			channel = ctx.message.channel_mentions[0]
		elif name == 'people' or name == 'everyone':
			channel = MyPerson('*','All channels')
		else:
			for ch in ctx.guild.channels:
				if ch.name == name:
					channel = ch
					break
		return channel


def setup(bot):
	bot.add_cog(Stats(bot))

