import discord
from discord.ext import commands

from data import session
import models
import settings, helpers
from datetime import datetime
import re, asyncio

EMBCOLOR=settings.BET_COLOR


class Bet(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(help="Open a betting pool",
					  usage="<name the pool>",
					  name="open-pool",
					  aliases=["pool-open","open"])
	async def open_pool(self, ctx, *args):
		# need a name for the pool
		if len(args) == 0:
			msg = "Don't you want to name your betting pool?"
			await ctx.send(msg)
			return

		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()

		new_pool = models.BettingPool()
		new_pool.name = " ".join(args)
		new_pool.created_at = datetime.now()
		new_pool.finalized = False
		new_pool.owner_id = author.id

		session.add(new_pool)
		session.commit()

		emb = self.help_emb()
		emb.set_author(name="Opening: \"{}\"".format(new_pool.name))
		emb.set_footer(text="This pool has the id #{} and is owned by {}".format(new_pool.id, ctx.author.display_name))
		await ctx.send(embed=emb)


	@commands.command(help="Fancy a gamble?\nExample:```!bet #4 10 crowns LNX will create the next MIR remix```This bets 10 crowns in pool #4 that MIR country version is on the way", 
					  usage="#<id> <#> crowns <bet content>")
	async def bet(self, ctx, *args):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="Bet Failed: {}".format(ctx.author.display_name))

		open_pools = session.query(models.BettingPool).filter_by(finalized=False).all()		
		if len(open_pools) == 0:
			emb.description = "There aren't any open pools to bet on 😔\nUse: ```!open-pool <put-name-here>``` to start a betting pool."
			await ctx.send(embed=emb)
			return
		if len(args) < 4:
			emb.description = "You seem to be missing something there 🤔\n\n**Usage:**\n```!bet #<id number> <#> crowns <bet content>```\n\n**Example**:```!bet #4 10 crowns LNX will create the next MIR remix```"
			await ctx.send(embed=emb)
			return

		numbre = re.compile('\d+')
		pool_id = int(numbre.search(args[0]).group())
		crowns = int(numbre.search(args[1]).group())

		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()
		pool = session.query(models.BettingPool).filter_by(id=pool_id).first()

		if args[2].lower()=="crown" or args[2].lower()=="crowns":
			bet_text = " ".join(args[3:])
		else:
			bet_text = " ".join(args[2:])

		# trying to bet in a nonexistent pool
		if not pool:
			pool_titles = "\n".join(list(map(self.pool_title_msg, open_pools)))
			emb.description = "There is no open pool #{} 🤷‍♀️\n\n**__Open Pools:__**\n{}".format(pool_id, pool_titles)
			await ctx.send(embed=emb)
			return

		# betting more than they have
		if author.crowns < crowns:
			emb.description = "You don't have enough crowns to do that 🧐\n\nYou are currently in possession of: **{} crowns**".format(author.crowns)
			await ctx.send(embed=emb)
			return

		# already bet in this pool
		previous_bet = session.query(models.Bet).filter_by(better_id=author.id,pool_id=pool.id).first()
		if previous_bet:
			emb.description = "You already have a bet in this pool, {}.\n\n\"{}\" for {} crowns".format(ctx.author.display_name, previous_bet.text, previous_bet.crowns)
			await ctx.send(embed=emb)
			return

		# make the bet
		new_bet = models.Bet()
		new_bet.text = bet_text
		new_bet.crowns = crowns
		new_bet.better_id = author.id
		new_bet.pool_id = pool_id
		session.add(new_bet)

		# take away crowns
		author.crowns -= crowns
		session.commit()

		# send success message
		emb.set_author(name="Success: Bet Placed")
		emb.set_footer(text="Bet ID #{}".format(new_bet.id))
		emb.description = "**{}**\n\nBet **{}** crowns that \"{}\"\n\nIn the pool **{}** (#{})".format(ctx.author.display_name, crowns, bet_text, pool.name, pool.id)
		await ctx.send(embed=emb)

	@commands.command(help="End a pool and choose the winner(s)\nExample:```!choose-winners #4 @Dani @Jules```", 
					  usage="#<id> [@winner1] [@winner2] [...]",
					  name="choose-winner",
					  aliases=["choose-winners"])
	async def choose_winner(self, ctx, *args):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="Choose Winner Failed: {}".format(ctx.author.display_name))

		# not enough arguments
		if len(args) < 2:
			emb.description = "You seem to be missing something there 🤔\n\n**Usage:**\n```!choose-winners #<pool id> @winner1 @winner2```\n\n**Example**:```!choose-winners #4 @Dani @Jules```"
			await ctx.send(embed=emb)
			return

		# pool id NAN
		try:
			numbre = re.compile('\d+')
			pool_id = int(numbre.search(args[0]).group())
		except:
			emb.description = "That doesn't seem like a valid pool ID # to me\n\n**Usage:**\n```!choose-winners #<pool id> @winner1 @winner2```\n\n**Example**:```!choose-winners #4 @Dani @Jules```"
			await ctx.send(embed=emb)
			return

		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()
		pool = session.query(models.BettingPool).filter_by(id=pool_id, finalized=False).first()

		# pool doesn't exist
		if not pool:
			emb.description = "There are no open pools with that ID #. Try:```!pool-status```to see ongoing betting pools."
			await ctx.send(embed=emb)
			return

		# choose-winners called by not the owner
		if pool.owner != author:
			emb.description = "You aren't authorized to choose the winners of this pool 😒 Only {} can choose the winners here.".format(pool.owner.real_name)
			await ctx.send(embed=emb)
			return

		# if they didn't use any mentions
		if len(ctx.message.mentions) == 0:
			emb.description = "You have to list the winners using @<name> mentions"
			await ctx.send(embed=emb)
			return

		bets = session.query(models.Bet).filter_by(pool=pool)
		winners = []
		winner_rns = []
		winning_bets = []
		# mentions != betters
		for m in ctx.message.mentions:
			mobj = session.query(models.GCMember).filter_by(discord_id=m.id).first()
			b = bets.filter_by(better=mobj).first()
			if not b:
				emb.description = "Looks like **{}** didn't bet in the pool **{}**. Use:```!pool-status #<id>```to see who did place bets.".format(mobj.real_name, pool.name)
				await ctx.send(embed=emb)
				return
			winners.append(mobj)
			winner_rns.append(mobj.real_name)
			winning_bets.append(b)

		emb = self.pool_emb(pool)
		msg = "{}: react to this post if you want to declare {} the winners of this pool:".format(ctx.author.mention, ", ".join(winner_rns))
		await ctx.send(msg, embed=emb)

		def check(reaction, user):
			return user.id == pool.owner.discord_id

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
		except asyncio.TimeoutError:
			await ctx.send("...nvm then")
		else:
			total_crowns = 0
			winners_bets_sum = 0
			win_strings = []

			for b in bets.all():
				total_crowns += b.crowns
			for b in winning_bets:
				winners_bets_sum += b.crowns

			for i, w in enumerate(winners):
				winnings = round(winning_bets[i].crowns/winners_bets_sum*total_crowns)
				winstr = "**{}** won **{}** crowns for her bet that \"{}\"".format(w.real_name, winnings, winning_bets[i].text)
				win_strings.append(winstr)
				w.crowns += winnings

			pool.finalized = True
			session.commit()

			emb.set_author(name="Closed: {}".format(pool.name))
			emb.set_footer(text="This pool had the id #{}, was owned by {}, and was created on {}".format(pool.id, pool.owner.real_name, pool.created_at))
			emb.description = "\n".join(win_strings)
			await ctx.send(embed=emb)



	@commands.command(help="See the current bets in a pool", 
					  usage="[optional #id]",
					  name="pool-status",
					  aliases=["status-pool", "pools-status", "status-pools"])
	async def pool_status(self, ctx, *args):
		if len(args) == 0:
			open_pools = session.query(models.BettingPool).filter_by(finalized=False).all()
		else:
			numbre = re.compile('\d+')
			pool_id = int(numbre.search(args[0]).group())
			open_pools = session.query(models.BettingPool).filter_by(id=pool_id).all()

		for pool in open_pools:
			await ctx.send(embed=self.pool_emb(pool))

	@commands.command(help="Erase a pool from existence and return all crowns bet", 
					  usage="<pool id#>",
					  name="void-pool",
					  aliases=["pool-void"])
	async def void_pool(self, ctx, *args):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="Void Failed: {}".format(ctx.author.display_name))
		if len(args) == 0:
			emb.description = "Which pool # do you want to void?"
			await ctx.send(embed=emb)
			return

		try:	
			numbre = re.compile('\d+')
			pool_id = int(numbre.search(args[0]).group())
			pool = session.query(models.BettingPool).filter_by(id=pool_id, finalized=False).first()
		except:
			emb.description = "I don't think you gave me an ID# there..."
			await ctx.send(embed=emb)
			return

		if not pool:
			emb.description = "That isn't the ID# of an open pool"
			await ctx.send(embed=emb)
			return						

		emb = self.pool_emb(pool)
		msg = "React to this post if you are **{}** and you want to delete this pool from existence & return all crowns back to their owners".format(pool.owner.real_name)
		await ctx.send(msg, embed=emb)

		def check(reaction, user):
			return user.id == pool.owner.discord_id

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
		except asyncio.TimeoutError:
			await ctx.send("...nvm then")
		else:
			# Void the pool
			emb.set_author(name="Void Success: {}".format(ctx.author.display_name))
			emb.description = "**{}** is no longer in existence".format(pool.name)

			# Add crowns back
			all_bets = session.query(models.Bet).filter_by(pool_id=pool.id).all()
			for b in all_bets:
				b.better.crowns += b.crowns
			session.commit()
			session.query(models.Bet).filter_by(pool_id=pool.id).delete()
			session.delete(pool)
			session.commit()

			await ctx.send(embed=emb)
			
	@commands.command(help="See the commands for betting", 
					  name="bet-help",
					  aliases=["help-bet","help-bets","bets-help"])
	async def bet_help(self, ctx, *args):
		await ctx.send(embed=self.help_emb())

	@commands.command(help="How many crowns you have to spend", 
					  name="my-crowns",
					  aliases=["crowns"])
	async def my_crowns(self, ctx, *args):
		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()
		desc = "**{}**: you have **{}** crowns to spend".format(ctx.author.display_name, author.crowns)
		emb = discord.Embed(description=desc, color=EMBCOLOR)
		await ctx.send(embed=emb)

	@commands.command(help="Your ongoing bets", 
					  name="my-bets")
	async def my_bets(self, ctx, *args):
		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()
		all_bets = session.query(models.Bet).filter_by(better_id=author.id).all()
		bet_text = "\n".join(list(map(self.bet_msg_by_pool, all_bets)))
		
		total_crowns = 0
		for b in all_bets:
			total_crowns += b.crowns

		desc = bet_text + "\n\nYou have **{} crowns** in ongoing bets and **{} crowns** left to spend".format(total_crowns, author.crowns)
		emb = discord.Embed(description=desc, color=EMBCOLOR)
		emb.set_author(name="{}'s Bets".format(ctx.author.display_name))
		await ctx.send(embed=emb)

	def pool_emb(self, pool):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="{} (#{})".format(pool.name, pool.id))
		emb.set_footer(text="This pool has the id #{}, is owned by {}, and was created on {}".format(pool.id, pool.owner.real_name, pool.created_at))

		bets = session.query(models.Bet).filter_by(pool_id=pool.id).all()
		total_crowns = 0
		for b in bets:
			total_crowns += b.crowns
		all_bets = "\n".join(list(map(self.bet_msg_by_person, bets)))
		emb.description = all_bets + "\n\n**Total Crowns in Pool:** {}".format(total_crowns)

		return emb

	def pool_title_msg(self, pool):
		return "**Pool #{}:** {}".format(pool.id, pool.name)

	def bet_msg_by_person(self, bet):
		return "**{}**: {} crowns that {}".format(bet.better.real_name, bet.crowns, bet.text)

	def bet_msg_by_pool(self, bet):
		return "**{}**: {} crowns that {}".format(bet.pool.name, bet.crowns, bet.text)

	def help_emb(self):
		placing = "**Placing Bets:**\nPlace your bets (in increments of WHOLE CROWNS ONLY) with ```!bet #<id> <#> crowns <bet content>```\nExample:```!bet #4 10 crowns LNX will create the next MIR remix```This bets 10 crowns in pool #4\n\n"
		closing = "**Choosing a Winner:**\nONLY the pool owner can choose a winner ```!choose-winners #<id> @winner1 @winner2 ...```\nExample:```!choose-winners #4 @jules @dani```You MUST use proper mentions to choose the winners.\n\n"
		helpmsg = "**Help Message:**\nSee this again with the command ```!bet-help```"

		desc = placing + closing + helpmsg
		emb = discord.Embed(description=desc,color=EMBCOLOR)
		return emb


def setup(bot):
	bot.add_cog(Bet(bot))

