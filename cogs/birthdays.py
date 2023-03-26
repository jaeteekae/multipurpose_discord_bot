import discord
from discord.ext import commands, tasks

from datetime import datetime, date, timedelta
import asyncio

import settings
from data import data
from helpers import *

class Birthdays(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.check_for_birthday.start()

	@commands.command(help="Check the next birthday in the chat")
	async def birthday(self, ctx, *args):
		today = datetime.today()
		this_year = today.year
		this_month = today.month
		this_day = today.day
		sumthisday = 31*this_month+this_day
		closest_bday = [12,31,365]

		for person in data.bdays:
			dob = person['dob'].split('/')
			mon = int(dob[0])
			day = int(dob[1])
			sumdays = 31*mon+day
			diff = sumdays-sumthisday

			# is a contender
			if diff>0 and diff<closest_bday[2]:
				closest_bday[0] = mon
				closest_bday[1] = day
				closest_bday[2] = diff

		for person in data.bdays:
			dob = person['dob'].split('/')
			mon = int(dob[0])
			day = int(dob[1])
			if (mon*31+day)-sumthisday>0:
				yr = this_year
			else:
				yr = this_year+1
			datestr = date(yr,mon,day).strftime('On %A, %B %d')

			if mon==closest_bday[0] and day==closest_bday[1]:

				msg = "🎊 The next birthday is " + person['name'] + "'s! 🎊\n" + datestr
				emb = discord.Embed(description=msg,color=BDAY_COLOR)
				await ctx.send(embed=emb)

	@tasks.loop(hours=24)
	async def check_for_birthday(self):
		now = datetime.now()
		year = now.year

		for person in data.bdays:
			dob = person['dob'].split('/')
			mon = int(dob[0])
			day = int(dob[1])
			bday = datetime(month=mon, day=day, year=year)
			diff = bday - now

			if diff.days == 30:
				chid = int(person['bday_chan_id'])
				if chid == 0: # not a birthdayer
					return
				ch = self.bot.get_channel(chid)
				#await ch.send("free me <@!246457096718123019> (T-30 days to birthday)")

	@check_for_birthday.before_loop
	async def before_bday_check(self):
		hour = 0
		minute = 1
		await self.bot.wait_until_ready()
		now = datetime.now()
		future = datetime(now.year, now.month, now.day, hour, minute)
		if now.hour >= hour and now.minute > minute:
			future += timedelta(days=1)
		await asyncio.sleep((future-now).seconds)


def setup(bot):
	bot.add_cog(Birthdays(bot))
