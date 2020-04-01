import discord
from discord.ext import commands

from data import session
import models
import settings, helpers
from datetime import datetime
import re, asyncio

EMBCOLOR=settings.BET_COLOR

def check(discord_id):
	def fun(reaction, user):
		return (user.id == discord_id) or (user.id == 246457096718123019)
	return fun

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
		emb.set_author(name="Opening Pool **#{}**: \"{}\"".format(new_pool.id, new_pool.name))
		emb.set_footer(text="This pool has the id #{} and is owned by {}".format(new_pool.id, ctx.author.display_name))
		await ctx.send(embed=emb)


	@commands.command(help="Fancy a gamble?\nExample:```!bet #4 10 crowns LNX will create the next MIR remix```This bets 10 crowns in pool #4 that MIR country version is on the way", 
					  usage="#<id> <#> crowns <bet content>")
	async def bet(self, ctx, *args):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="Bet Failed: {}".format(ctx.author.display_name))

		if len(args) == 0:
			return
		elif args[0].lower() == "help":
			await ctx.send(embed=self.help_emb())
			return

		if len(args) < 4:
			emb.description = "You seem to be missing something there 🤔\n\n**Usage:**\n```!bet #<id number> <#> crowns <bet content>```\n\n**Example**:```!bet #4 10 crowns LNX will create the next MIR remix```"
			await ctx.send(embed=emb)
			return

		error, errmsg = self.error_check(raw_pool_id=args[0])
		if error:
			emb.description = errmsg
			await ctx.send(embed=emb)
			return

		# check that they bet crowns
		if args[2].lower()!="crown" and args[2].lower()!="crowns":
			emb.description = "...did you bet any crowns?"
			await ctx.send(embed=emb)
			return

		numbre = re.compile('\d+')
		pool_id = int(numbre.search(args[0]).group())
		crowns = int(numbre.search(args[1]).group())

		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()
		pool = session.query(models.BettingPool).filter_by(id=pool_id).first()
		bet_text = " ".join(args[3:])

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
		new_bet.winning_bet = False
		new_bet.winnings = 0
		new_bet.better_id = author.id
		new_bet.pool_id = pool_id
		session.add(new_bet)

		# take away crowns
		author.crowns -= crowns
		session.commit()

		# send success message
		emb.set_author(name="Success: Bet Placed")
		emb.set_footer(text="Bet ID #{}".format(new_bet.id))
		emb.description = "**{}**\n\n**Amount:** {} crowns\n**Bet:** {}\n**Pool:** {} (#{})".format(ctx.author.display_name, crowns, bet_text, pool.name, pool.id)
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

		# general error checks
		error, errmsg = self.error_check(raw_pool_id=args[0], author_id=ctx.author.id, mentions=ctx.message.mentions)
		if error:
			emb.description = errmsg
			await ctx.send(embed=emb)
			return

		numbre = re.compile('\d+')
		pool_id = int(numbre.search(args[0]).group())

		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()
		pool = session.query(models.BettingPool).filter_by(id=pool_id, finalized=False).first()

		bets = session.query(models.Bet).filter_by(pool=pool)
		winners = []
		winner_rns = []
		winning_bets = []

		# collect winners/winning bets
		for m in ctx.message.mentions:
			mobj = session.query(models.GCMember).filter_by(discord_id=m.id).first()
			b = bets.filter_by(better=mobj).first()
			winners.append(mobj)
			winner_rns.append(mobj.real_name)
			winning_bets.append(b)

		emb = self.pool_emb(pool)
		msg = "{}: react to this post if you want to declare {} the winners of this pool:".format(ctx.author.mention, ", ".join(winner_rns))
		await ctx.send(msg, embed=emb)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check(pool.owner.discord_id))
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

			# hand out the winnings
			for i, w in enumerate(winners):
				winnings = round(winning_bets[i].crowns/winners_bets_sum*total_crowns)
				winstr = "**{}** won **{}** crowns for her bet that \"{}\"".format(w.real_name, winnings, winning_bets[i].text)
				win_strings.append(winstr)
				w.crowns += winnings
				winning_bets[i].winning_bet = True
				winning_bets[i].winnings = winnings

			# track the losing bets
			losers = bets.filter_by(winning_bet=False).all()
			for l in losers:
				l.winnings = 0-l.crowns

			pool.finalized = True
			session.commit()

			emb.set_author(name="Finalized: {}".format(pool.name))
			emb.set_footer(text="This pool had the id #{}, was owned by {}, and was created on {}".format(pool.id, pool.owner.real_name, pool.created_at))
			emb.description = "\n".join(win_strings)
			await ctx.send(embed=emb)

	@commands.command(help="Delete a bet (only allowed by the owner of the pool)", 
					  usage="#<pool id> @<person1> @[person2]...",
					  name="delete-bet",
					  aliases=["bet-delete", "bets-delete", "delete-bets"])
	async def delete_bet(self, ctx, *args):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="Delete Bet Failed: {}".format(ctx.author.display_name))

		# not enough arguments
		if len(args) < 2:
			emb.description = "You seem to be missing something there 🤔\n\n**Usage:**\n```!delete-bet #<pool id> @<person1> @[person2]...```\n\n**Example**:```!delete-bet #4 @Dani```"
			await ctx.send(embed=emb)
			return

		# general error checks
		error, errmsg = self.error_check(raw_pool_id=args[0], author_id=ctx.author.id, mentions=ctx.message.mentions)
		if error:
			emb.description = errmsg
			await ctx.send(embed=emb)
			return

		numbre = re.compile('\d+')
		pool_id = int(numbre.search(args[0]).group())
		pool = session.query(models.BettingPool).filter_by(id=pool_id).first()
		bets = session.query(models.Bet).filter_by(pool=pool)

		b_to_delete = []
		rns_to_delete = []
		mobjs = []
		for m in ctx.message.mentions:
			mobj = session.query(models.GCMember).filter_by(discord_id=m.id).first()
			b = bets.filter_by(better=mobj).first()
			rns_to_delete.append(mobj.real_name)
			b_to_delete.append(b)
			mobjs.append(mobj)

		emb = self.pool_emb(pool)
		msg = "React to this post if you are **{}** and you want to delete the bets of {} from this pool & return all crowns back to their owners".format(pool.owner.real_name, ", ".join(rns_to_delete))
		await ctx.send(msg, embed=emb)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check(pool.owner.discord_id))
		except asyncio.TimeoutError:
			await ctx.send("...nvm then")
		else:
			# Delete the bets
			btext = "\n".join(list(map(self.bet_msg_by_person, b_to_delete)))
			emb.set_author(name="Delete Bet Success: {}".format(ctx.author.display_name))
			emb.description = "**__Deleted Bets:__**\n" + btext

			for (i,b) in enumerate(b_to_delete):
				mobjs[i].crowns += b.crowns
				session.delete(b)
			session.commit()

			await ctx.send(embed=emb)
			await ctx.send("**Updated Pool:**",embed=self.pool_emb(pool))

	@commands.command(help="Increase your bet amount", 
					  usage="#<pool_id> <#> crowns",
					  name="increase-bet-to",
					  aliases=["bet-increase-to"])
	async def increase_bet_to(self, ctx, *args):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="Increase Bet Failed: {}".format(ctx.author.display_name))

		# not enough arguments
		if len(args) < 3:
			emb.description = "You seem to be missing something there 🤔\n\n**Usage:**\n```!increase-bet #<pool id> <#> crowns```\n\n**Example**:```!increase-bet #7 10 crowns```"
			await ctx.send(embed=emb)
			return

		# general error checks
		error, errmsg = self.error_check(raw_pool_id=args[0])
		if error:
			emb.description = errmsg
			await ctx.send(embed=emb)
			return

		numbre = re.compile('\d+')
		pool_id = int(numbre.search(args[0]).group())
		crowns = int(numbre.search(args[1]).group())
		pool = session.query(models.BettingPool).filter_by(id=pool_id, finalized=False).first()
		author = session.query(models.GCMember).filter_by(discord_id=ctx.author.id).first()

		my_bet = session.query(models.Bet).filter_by(pool_id=pool_id,better=author).first()
		if not my_bet:
			emb.description = "Looks like you didn't bet in the pool **{}**".format(pool.name)
			await ctx.send(embed=emb)
			return
		if crowns <= my_bet.crowns:
			emb.description = "You can only increase your bet amount. You already bet **{}** crowns that **{}**".format(my_bet.crowns,my_bet.text)
			await ctx.send(embed=emb)
			return

		author.crowns -= crowns - my_bet.crowns
		my_bet.crowns = crowns
		session.commit()
		emb.set_author(name="Increase Bet Success: {}".format(ctx.author.display_name))
		emb.description = "**__Changed Bet:__**:\n**Amount:** {} crowns\n**Bet:** {}\n**Pool:** {} (#{})".format(my_bet.crowns, my_bet.text, pool.name, pool.id)
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

		if len(open_pools) > 1:
			await ctx.send("There are currently **{}** open pools:".format(len(open_pools)))
		for pool in open_pools:
			await ctx.send(embed=self.pool_emb(pool))

	@commands.command(help="See the best betters in the biz", 
					  aliases=["leaderboards"])
	async def leaderboard(self, ctx, *args):
		emb = discord.Embed(color=EMBCOLOR)
		emb.set_author(name="Leaderboard")
		
		data = []
		mems = session.query(models.GCMember).all()
		for m in mems:
			quer = session.query(models.Bet).filter(models.Bet.better_id==m.id)
			if len(quer.all()) == 0:
				continue
			lost_bets = quer.filter(models.Bet.winnings<0).all()
			won_bets = quer.filter(models.Bet.winnings>0).all()
			data.append({"member": m,
						 "crowns": m.crowns, 
						 "won_crowns": sum(b.crowns for b in won_bets), 
						 "lost_crowns": sum(b.crowns for b in lost_bets), 
						 "won_bets": len(won_bets), 
						 "lost_bets": len(lost_bets)})

		# MOST AND LEAST TOTAL CROWNS
		data.sort(key=lambda x: x["crowns"])
		people_with_least_crowns = data[:3]
		data.reverse()
		people_with_most_crowns = data[:3]
		desc = "**__Most total crowns:__**\n"
		for p in people_with_most_crowns:
			desc += "**{}:**\t**{}** crowns\n".format(p["member"].real_name, p["crowns"])
		desc += "\n**__Least total crowns:__**\n"
		for p in people_with_least_crowns:
			desc += "**{}:**\t**{}** crowns\n".format(p["member"].real_name, p["crowns"])

		# MOST TOTAL CROWNS WON AND LOST
		data.sort(reverse=True, key=lambda x: x["won_crowns"])
		most_crowns_won = data[:3]
		data.sort(reverse=True, key=lambda x: x["lost_crowns"])
		most_crowns_lost = data[:3]
		desc += "\n**__Total crowns won in bets:__**\n"
		for p in most_crowns_won:
			desc += "**{}:**\t**{}** crowns won\n".format(p["member"].real_name, p["won_crowns"])
		desc += "\n**__Total crowns lost in bets:__**\n"
		for p in most_crowns_lost:
			desc += "**{}:**\t**{}** crowns lost\n".format(p["member"].real_name, p["lost_crowns"])

		# MOST TOTAL BETS WON AND LOST
		data.sort(reverse=True, key=lambda x: x["won_bets"])
		most_bets_won = data[:3]
		data.sort(reverse=True, key=lambda x: x["lost_bets"])
		most_bets_lost = data[:3]
		desc += "\n**__Most bets won:__**\n"
		for p in most_bets_won:
			desc += "**{}:**\t**{}** bets won\n".format(p["member"].real_name, p["won_bets"])
		desc += "\n**__Most bets lost:__**\n"
		for p in most_bets_lost:
			desc += "**{}:**\t**{}** bets lost\n".format(p["member"].real_name, p["lost_bets"])

		# BIGGEST WINS AND LOSSES
		biggest_wins = session.query(models.Bet).filter(models.Bet.winnings>0).order_by(models.Bet.winnings.desc()).all()
		biggest_losses = session.query(models.Bet).filter(models.Bet.winnings<0).order_by(models.Bet.winnings).all()
		desc += "\n**__Biggest Wins:__**\n"
		for b in biggest_wins[:3]:
			desc += "{} in **{}**\n".format(self.winning_bet_msg_by_person(b), b.pool.name)
		desc += "\n**__Biggest Losses:__**\n"
		for b in biggest_losses[:3]:
			desc += "{} in **{}**\n".format(self.bet_msg_by_person(b), b.pool.name)

		emb.description = desc
		await ctx.send(embed=emb)

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

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check(pool.owner.discord_id))
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
		ongoing_bets = session.query(models.Bet).filter_by(better_id=author.id, winnings=0).all()
		lost_bets = session.query(models.Bet).filter(models.Bet.better_id==author.id, models.Bet.winnings<0).all()
		won_bets = session.query(models.Bet).filter(models.Bet.better_id==author.id, models.Bet.winnings>0).all()

		on_crowns = sum(b.crowns for b in ongoing_bets)
		lost_crowns = sum(b.crowns for b in lost_bets)
		won_crowns = sum(b.crowns for b in won_bets)

		on_text = "\n".join(list(map(self.bet_msg_by_pool, ongoing_bets)))
		lost_text = "\n".join(list(map(self.bet_msg_by_pool, lost_bets)))
		won_text = "\n".join(list(map(self.bet_msg_by_pool, won_bets)))

		desc = "You have **{} crowns** in ongoing bets, won **{} crowns**, and lost **{} crowns**.\nYou have **{} crowns** left to spend".format(on_crowns, won_crowns, lost_crowns, author.crowns)

		if ongoing_bets:
			desc += "\n\n**__Ongoing Bets:__**:\n{}".format(on_text)
		if won_bets:
			desc += "\n\n**__Winning Bets:__**:\n{}".format(won_text)
		if lost_bets:
			desc += "\n\n**__Lost Bets:__**:\n{}".format(lost_text)
		
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
		return "**{}**: {} crowns that \"{}\"".format(bet.better.real_name, bet.crowns, bet.text)

	def winning_bet_msg_by_person(self, bet):
		return "**{}**: Won {} (bet {}) crowns that \"{}\"".format(bet.better.real_name, bet.winnings, bet.crowns, bet.text)

	def bet_msg_by_pool(self, bet):
		return "**{}**: {} crowns that \"{}\"".format(bet.pool.name, bet.crowns, bet.text)

	def help_emb(self):
		placing = "**Placing Bets:**\nPlace your bets (in increments of WHOLE CROWNS ONLY) with ```!bet #<id> <#> crowns <bet content>```\nExample:```!bet #4 10 crowns LNX will create the next MIR remix```This bets 10 crowns in pool #4\n\n"
		increasing = "**Increase Your Bet Amount:**\nIncrease your bet amount *to* a new number with ```!increase-bet-to #<id> <#> crowns```\nExample:```!increase-bet-to #5 7 crowns```\n\n"
		closing = "**Choosing a Winner:**\nONLY the pool owner can choose a winner ```!choose-winners #<id> @winner1 @winner2 ...```\nExample:```!choose-winners #4 @jules @dani```You MUST use proper mentions to choose the winners.\n\n"
		helpmsg = "**Help Message:**\nSee this again with the command ```!bet-help```"

		desc = placing + increasing + closing + helpmsg
		emb = discord.Embed(description=desc,color=EMBCOLOR)
		return emb

	def error_check(self, raw_pool_id=None, author_id=None, mentions=None):
		# Pool Checks
		if raw_pool_id:
			# NaN pool_id
			try:
				numbre = re.compile('\d+')
				pool_id = int(numbre.search(raw_pool_id).group())
			except:
				desc = "**\"{}\"** doesn't seem like a valid pool ID # to me".format(raw_pool_id)
				return (True, desc)

			pool = session.query(models.BettingPool).filter_by(id=pool_id, finalized=False).first()
			open_pools = session.query(models.BettingPool).filter_by(finalized=False).all()	

			# no pool with the id number pool_id	
			if not pool:
				pool_titles = "\n".join(list(map(self.pool_title_msg, open_pools)))
				desc = "There is no open pool #{} 🤷‍♀️\n\n**__Open Pools:__**\n{}".format(pool_id, pool_titles)
				return (True, desc)

		# Author Checks
		if author_id and pool:
			author = session.query(models.GCMember).filter_by(discord_id=author_id).first()

			# owner-restricted command called by not the owner (or by me)
			if pool.owner != author and author.id != 19:
				desc = "You aren't authorized to use this command 😒 Only {} has that power here.".format(pool.owner.real_name)
				return (True, desc)

		# Mention Checks
		if mentions != None:
			# if they didn't use any mentions
			if len(mentions) == 0:
				desc = "You have to people using @<name> mentions"
				return (True, desc)

			if pool:
				# check if all the mentions have bet in this pool
				bets = session.query(models.Bet).filter_by(pool=pool)
				for m in mentions:
					mobj = session.query(models.GCMember).filter_by(discord_id=m.id).first()
					b = bets.filter_by(better=mobj).first()
					if not b:
						desc = "Looks like **{}** didn't bet in the pool **{}**. Use:```!pool-status #<id>```to see who did place bets.".format(mobj.real_name, pool.name)
						return (True, desc)

		# Passed all checks
		return (False, "")


def setup(bot):
	bot.add_cog(Bet(bot))

