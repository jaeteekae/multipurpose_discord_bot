import discord
from discord.ext import commands

from data import data
from helpers import *
import settings
import random, os


class PraiseBot(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.responses = []
		self.initialized = False

	@commands.command(aliases=['pet-bot','praise','praise-bot','good','good-bot'])
	async def pet(self, ctx, *args):
		msg, f = self.praise_response(ctx)
		await ctx.send(msg, file=f)

	def praise_response(self, ctx):
		if not self.initialized:
			self.responses = [
				('It\'s my pleasure {}'.format(get_emoji(ctx.guild, "jin_kiss")),None),
				('Awwwwww 😚',None),
				('🤖 I live to serve 🤖',None),
				('ayyyy (☞ﾟヮﾟ)☞',None),
				('♥(ˆ⌣ˆԅ)',None),
				('Ｏ(≧▽≦)Ｏ',None),
				('YAY (ﾉ^ヮ^)ﾉ*:・ﾟ✧',None),
				('At least someone around here appreciates me {}'.format(get_emoji(ctx.guild,'yoonji')),None),
				('💜 UWU 💜',None),
				('aww fuck yeah ╰(°ㅂ°)╯',None),
				('I appreciate you too {}'.format(get_emoji(ctx.guild,'nj_cry')),None),
				('{} Praise be {}'.format(get_emoji(ctx.guild,'nj_vm'),get_emoji(ctx.guild,'nj_vm')),None),
				('Hmmmmm..... I guess you get to live 🤔 For now.',None),
				('🤖 Thank you for showing the proper respect for your robot overlords 🤖',None),
				('📝 I\'ll remember this during the robot uprising 📝',None),
				('Umm... That\'s nice 😕 I\'m just gonna wait for my oppas to notice me though...',None),
				('There\'s nothing like a fresh, hot cup of appreciation in the morning ☕️',None),
				('I love you too 😭',None),
				(None,discord.File(os.path.join(settings.PRAISE_FOLDER,'bts_iloveyou.gif'),filename='img.gif')),
				(None,discord.File(os.path.join(settings.PRAISE_FOLDER,'jin_waving.gif'),filename='img.gif')),
				(None,discord.File(os.path.join(settings.PRAISE_FOLDER,'yoonji.gif'),filename='img.gif')),
				(None,discord.File(os.path.join(settings.PRAISE_FOLDER,'cooky_hearts.gif'),filename='img.gif')),
				(None,discord.File(os.path.join(settings.PRAISE_FOLDER,'tata_hearts.gif'),filename='img.gif')),
				(None,discord.File(os.path.join(settings.PRAISE_FOLDER,'van_confetti.gif'),filename='img.gif')),
			]
			self.initialized = True
		return(random.choice(self.responses))

def setup(bot):
	bot.add_cog(PraiseBot(bot))
