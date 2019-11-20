import discord
from discord.ext import commands
import requests, os

from data import data
import settings
import helpers

class Receipt(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		if not os.path.isdir(settings.STATIC_FOLDER):
			os.makedirs(settings.STATIC_FOLDER)
		if not os.path.isdir(settings.TMP_IMG_FOLDER):
			os.makedirs(settings.TMP_IMG_FOLDER)

	@commands.command(help="Receipt a Thing", 
					  usage="!receipt [optional message] [optional uploaded image]",
					  aliases=["r", "receipts"])
	async def receipt(self, ctx, *args):
		emb = helpers.receipt_message(message=ctx.message, text=" ".join(args), receipter=ctx.author)
		r_channel = ctx.bot.get_channel(settings.RECEIPTS_CHANNEL_ID)
		await r_channel.send(embed=emb)


def setup(bot):
	bot.add_cog(Receipt(bot))

