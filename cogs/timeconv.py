import discord
from discord.ext import commands

from data import data
import pytz
from datetime import datetime
import settings

EMBCOLOR=settings.TIMECONV_COLOR

class TimeConv(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(help="Convert your time to other times",
					  usage="<a time> [optional timezone]",
					  name="time",
					  aliases=["t"])
	async def timeconvert(self, ctx, *args):
		args = list(args)
		emb = discord.Embed(color=EMBCOLOR)
		user = data.get_user_data(ctx.author.id)
		emb.set_author(name=user["name"] + "'s " + " ".join(args))
		timestr = args[0].replace(":","").replace(" ","").lower()
		now = datetime.now()
		add = 0
		hours = 0
		minutes = 0
		found_am = False
		found_pm = False
		start = len(timestr)-1

		# check for AM
		if (len(timestr) > 1) and (timestr[-2] == 'a'):
			found_am = True
		if (len(args) > 1) and ('am' in args[1].lower()):
			found_am = True

		# check for PM
		if (len(timestr) > 1) and (timestr[-2] == 'p'):
			add = 12
			timestr = timestr[:-2]
			found_pm = True
		if (len(args) > 1) and ('pm' in args[1].lower()):
			add = 12
			found_pm = True

		# check for attached time zone
		if (timestr[-1] == "t") and (len(timestr) > 3):
			args.append(timestr[-3:])
			timestr = timestr[:-3]

		# get hours and minutes
		if "now" in args[0].lower():
			hours = now.hour
			minutes = now.minute
		else:
			if (len(timestr) == 2) or (len(timestr) == 1):
				hours = int(timestr)
			elif len(timestr) == 3:
				hours = int(timestr[:1])
				minutes = int(timestr[1:])
			elif len(timestr) == 4:
				hours = int(timestr[:2])
				minutes = int(timestr[2:])

		if hours == 12:
			if found_am:
				hours = 0
			elif found_pm:
				add = 0
		hours += add

		# use default tz for user
		if (len(args) == 1) or (args[-1].lower() in ['am','pm']):
			tz = pytz.timezone(user['timezone'])
		# use supplied tz
		else:
			if args[-1].lower() == 'kst':
				tz = pytz.timezone('Asia/Seoul')
			else:
				try:
					tz = pytz.timezone(args[-1])
				except:
					emb.description = "Sorry idk what that time zone is. Try [one from here.](https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones)"
					await ctx.send(embed=emb)
					return
		
		timeobj = tz.localize(datetime(now.year, now.month, now.day, hour=hours, minute=minutes))

		# convert the time
		fmt12 = "%I:%M %p %Z"
		fmt24 = "%H:%M %Z"
		msgstr = ""

		zones = [pytz.timezone("US/Pacific"),
				 pytz.timezone("US/Eastern"),
				 pytz.timezone("Chile/Continental"),
				 pytz.timezone("Europe/London"),
				 pytz.timezone("Europe/Berlin"),
				 pytz.timezone("Asia/Seoul")]

		counter = 0
		for z in zones:
			newtime = timeobj.astimezone(z)
			msgstr += newtime.strftime(fmt12)
			if timeobj.day != newtime.day:
				diff = timeobj.day - newtime.day
				if (diff == 1) or (diff < -25):
					msgstr += " -1"
				else:
					msgstr += " +1"
			msgstr += "\n"
			counter += 1
			if counter % 3 == 0:
				if counter / 3 == 1:
					msgstr = msgstr.replace("-03","NAY")
					emb.add_field(name="Americas", value=msgstr, inline=True)
				if counter / 3 == 2:
					emb.add_field(name="Eurasia", value=msgstr, inline=True)
				msgstr = ""

		await ctx.send(embed=emb)

def setup(bot):
	bot.add_cog(TimeConv(bot))

