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
		self.timewords = ['24', 'day', 'twenty', 'week', 'month', 'all', 'alltime', 'all-time', 'one', '1']
		self.top_emoji = '👑'
		self.my_id = '246457096718123019'

	@commands.command(help="Get some stats, you nosy person\nTime can be 24 hours, 1 week, 1 month, or all time\nExamples:\n\t!stats @Jules 24 hours\n\t!more-stats #general 1 week\n\t!most-stats everyone 1 month\n\t!stats channels all time", 
					  usage="<@person|#channel|people|channels> <time>")
	async def stats(self, ctx, *args):
		args = list(args)
		if len(args) == 0:
			resp, emb = self.message_handle(ctx, ['everyone', '24', 'hours'], self.person_stats_all, self.channel_stats_all)
		elif args[0] in self.timewords:
			args.insert(0, 'everyone')
			resp, emb = self.message_handle(ctx, args, self.person_stats_all, self.channel_stats_all)
		else:
			resp, emb = self.message_handle(ctx, args, self.person_stats_all, self.channel_stats_all)
		await ctx.send(resp,embed=emb)

	@commands.command(name="top-emojis",
					  aliases=['emojis-top','emoji-top','top-emoji'],
					  help="Get a list of the most used emojis in the channel")
	async def top_emojis(self, ctx, *args):
		estats = self.get_emoji_stats()
		estats.sort(key=lambda x: x[1],reverse=True)
		estats = estats[:5]

		desc = ""
		for eid, num in estats:
			desc += "{} : {} uses\n".format(get_emoji_by_id(data.guild,int(eid)),str(num))

		resp = "The top 5 most used emojis are:"
		emb = discord.Embed(description=desc, color=settings.STATS_COLOR)		
		await ctx.send(resp, embed=emb)

	@commands.command(name="bottom-emojis",
					  aliases=['emojis-bottom','emoji-bottom','bottom-emoji'],
					  help="Get a list of the least used emojis in the channel")
	async def bottom_emojis(self, ctx, *args):
		estats = self.get_emoji_stats()
		estats.sort(key=lambda x: x[1])
		estats = estats[:5]
		
		desc = ""
		for eid, num in estats:
			desc += "{} : {} uses\n".format(get_emoji_by_id(data.guild,int(eid)),str(num))

		resp = "The 5 least used emojis are:"
		emb = discord.Embed(description=desc, color=settings.STATS_COLOR)
		await ctx.send(resp, embed=emb)

	@commands.command(name="emoji-stats",
					  aliases=['stats-emojis', 'stats-emoji'],
					  help="See how frequently all emojis are used")
	async def emoji_stats(self, ctx, *args):
		estats = self.get_emoji_stats()
		estats.sort(key=lambda x: x[1], reverse=True)
		
		msgs = []
		desc = ""
		i = 0
		for eid, num in estats:
			if i%50 == 0 and i!=0:
				msgs.append(desc)
				desc = ""
			elif i%5 == 0 and i!=0:
				desc += '\n'
			desc += " {}:`{} `".format(get_emoji_by_id(data.guild,int(eid)),str(num))
			i += 1
		if i > 50:
			msgs.append(desc)

		resp = "**Total Emoji Usage (since August 12, 2019):**"
		emb = discord.Embed(description=msgs[0], color=settings.STATS_COLOR)
		await ctx.send(resp, embed=emb)

		for m in msgs[1:]:
			emb = discord.Embed(description=m, color=settings.STATS_COLOR)
			await ctx.send(embed=emb)			

	@commands.command(help="Hand out some superdy duper special crowns to the people who spend all day on this darn server")
	async def coronation(self, ctx, *args):
		dethroned = []
		usurpers = []
		maintainers = []
		datalist = []

		timedata = data.get_day_stats()
		datalist_wbot = self.channel_data(timedata, '*')
		datalist_wbot = [x for (x,y) in datalist_wbot]
		for memid in datalist_wbot:
			if memid == self.my_id:
				continue
			mem = data.guild.get_member(int(memid))
			if mem and not mem.bot:
				datalist.append(memid)
		datalist = datalist[:5]

		# remove dethroned members
		for mem in data.guild.members:
			if self.top_emoji in mem.display_name:
				pid = str(mem.id)
				if pid in datalist:
					maintainers.append(pid)
				else:
					dethroned.append(pid)
					await mem.edit(nick=(mem.display_name.replace(self.top_emoji,"")))

		# add the usurpers
		for pid in datalist:
			if pid in maintainers:
				continue
			else:
				usurpers.append(pid)
				mem = data.guild.get_member(int(pid))
				await mem.edit(nick=(mem.display_name+self.top_emoji))

		resp = ':guardsman: **Hear Ye Hear Ye! Please rise for your new royal family!** :guardsman:'
		desc = ''

		dethroned = list(map(lambda x: '<@{}>'.format(x), dethroned))
		usurpers = list(map(lambda x: '<@{}>'.format(x), usurpers))
		maintainers = list(map(lambda x: '<@{}>'.format(x), maintainers))
		if len(usurpers) > 0:
			desc += 'The throne has been usurped by {}!'.format(', '.join(usurpers))

		if len(maintainers) > 0:
			if len(desc) > 0:
				desc += '\n\n'
			desc += '{} have maintained their crown!'.format(', '.join(maintainers))

		if len(dethroned) > 0:
			if len(desc) > 0:
				desc += '\n\n'
			desc += '{} have been dethroned!'.format(', '.join(dethroned))

		emb = discord.Embed(description=desc, color=settings.STATS_COLOR)
		await ctx.send(resp,embed=emb)

	def message_handle(self, ctx, args, pers_func, chan_func):
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

	def person_stats_all(self, person, timedata, timestr):
		desc = ''
		pid = str(person.id)
		datalist = self.person_data(timedata, pid)
		calc = 0

		for (ch,num) in datalist:
			line = '<#{}>: **{}** messages\n'.format(ch, str(num))
			calc += num
			desc += line

		resp = "There have been **{}** messages sent by **{}** in the past **{}**:".format(calc,person.display_name,timestr)
		emb = discord.Embed(description=desc,color=settings.STATS_COLOR)
		return(resp, emb)

	def channel_stats_all(self, channel, timedata, timestr):
		desc = ''
		chid = str(channel.id)
		calc = 0

		datalist = self.channel_data(timedata, chid)

		for (pid,num) in datalist:
			line = '<@{}>: **{}** messages\n'.format(pid, str(num))
			desc += line
			calc += num

		resp = "There have been **{}** messages sent to **{}** in the past **{}**:".format(calc,channel.mention,timestr)
		emb = discord.Embed(description=desc,color=settings.STATS_COLOR)
		return(resp, emb)

	def stats_for_time(self, timeargs):
		time = ' '.join(timeargs)
		time = time.lower()

		if ('24' in time) or ('twenty' in time) or ('day' in time):
			return(data.get_day_stats(),time)
		elif 'week' in time:
			return(data.get_week_stats(),time)
		elif 'month' in time:
			return(data.get_month_stats(),time)
		elif ('all' in time) or ('alltime' in time) or ('all-time' in time):
			return(data.get_all_stats(),time)

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
			for per in data.guild.members:
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
			for ch in data.guild.channels:
				if ch.name == name:
					channel = ch
					break
		return channel

	def person_data(self, timedata, pid):
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
		return(datalist)

	def channel_data(self, timedata, chid):
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
		return(datalist)

	def get_emoji_stats(self):
		estats = data.stats['emojis']
		eusage = []
		emojis = data.guild.emojis

		for e in emojis:
			eid = str(e.id)
			if eid in estats:
				eusage.append((eid, estats[eid]))
			else:
				eusage.append((eid, 0))

		return eusage




def setup(bot):
	bot.add_cog(Stats(bot))

