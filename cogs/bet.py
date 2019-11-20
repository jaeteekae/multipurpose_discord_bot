import discord
from discord.ext import commands

from data import data
import settings, helpers
from datetime import datetime
import re

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

    	bets = data.bets
    	new_pool = {}

    	new_pool["name"] = " ".join(args)
    	new_pool["created_at"] = datetime.now()
    	new_pool["owner"] = ctx.author.id

    	if len(bets["previous_pools"])==0 and len(bets["open_pools"])==0:
    		pool_id = 1
    	else:
    		if len(bets["previous_pools"])==0:
    			id1 = 0
    		else:
    			id1 = int(bets["previous_pools"][-1]["id"])

    		if len(bets["open_pools"])==0:
    			id2 = 0
    		else:
    			id2 = int(bets["open_pools"][-1]["id"])

    		pool_id = max(id1,id2) + 1
    	new_pool["id"] = pool_id
    	new_pool["betters"] = {}
    	new_pool["open"] = True

    	bets["open_pools"].append(new_pool)

    	emb = self.help_msg()
    	emb.set_author(name="The betting pool for \"{}\" has been opened".format(new_pool["name"]), icon_url="http://www.pokerfanatics.net/wp-content/uploads/2016/05/casino_chips.jpg")
    	emb.set_footer(text="This pool has the id #{} and is owned by {}".format(new_pool["id"], ctx.author.display_name))
    	await ctx.send(embed=emb)


    @commands.command(help="Fancy a gamble?\nExample:```!bet #4 10 crowns LNX will create the next MIR remix```This bets 10 crowns in pool #4 that MIR country version is on the way", 
                	  usage="#<id> <#> crowns <bet content>")
    async def bet(self, ctx, *args):
    	if len(data.bets["open_pools"]) == 0:
    		msg = "There aren't any open pools to bet on 😔 Use ```!open-pool``` to start a betting pool."
    		await ctx.send(msg)
    		return
    	if len(args) < 3:
    		msg = "You seem to be missing something there 🤔\n\n**Usage:**\n```!bet #<id number> <#> crowns <bet content>```"
    		await ctx.send(msg)
    		return

    	if not self.is_betting_member(ctx.author.id):
    		self.init_member(ctx.author)

		numbre = re.compile('\d+')
		pool_id = int(numbre.search(args[0]).group())
        crowns = int(numbre.search(args[1]).group())

        if args[2]=="crown" or args[2]=="crowns":
        	bet_text = args[3:]
        else:
        	bet_text = args[2:]

    @commands.command(help="End a pool and choose the winner(s)\nExample:```!choose-winners #4 @Dani @Jules```", 
                	  usage="#<id> [@winner1] [@winner2] [...]",
                	  name="choose-winner",
                	  aliases=["choose-winners"])
    async def choose_winner(self, ctx, *args):
    	try:
    		numbre = re.compile('\d+')
    		pool_id = int(numbre.search(args[0]).group())
    	except:
    		pool_id = None

    	# pool_id optional if there's only one ongoing pool
    	if not pool_id:
    		if len(data.bets["open_pools"]) != 1:
    			msg = "I don't know what pool you're talking about"
    			await ctx.send(msg)
    			return
    		pool_id = int(data.bets["open_pools"][0]["id"])

    	pool = None
    	for p in data.bets["open_pools"]:
    		if int(p["id"]) == pool_id:
    			pool = p
    			break

    	if not pool:
    		msg = "That doesn't seem to be the ID# of an active betting pool\bUse ```!pool-status``` to see the active pools"
    		await ctx.send(msg)
    		return

    	betters = pool["betters"]
    	# for bid, x

    	# confirm with thumbs up emoji?


    @commands.command(help="See the commands for betting", 
    				  name="bet-help",
    				  aliases=["help-bet"])
    async def bet_help(self, ctx, *args):
        await ctx.send(embed=self.help_msg())

    def pool_msg(self, pool):
    	now = datetime.now()
    	then = pool["created_at"]
    	elapsed = helpers.generate_timestring(now-then)

    	emb = discord.Embed(color=EMBCOLOR)
    	emb.set_author(name=pool["name"], icon_url="http://www.pokerfanatics.net/wp-content/uploads/2016/05/casino_chips.jpg")
    	emb.set_footer(text="This pool has the id #{}, is owned by {}, and was created {} ago".format(pool["id"], pool["owner"], elapsed))

    	return emb

    def help_msg(self):
    	placing = "**Placing Bets:**\nPlace your bets in increments of WHOLE CROWNS ONLY with ```!bet #<id> <#> crowns <bet content>```\nExample:```!bet #4 10 crowns LNX will create the next MIR remix```This bets 10 crowns in pool #4 that MIR country version is on the way\n\n"
    	closing = "**Closing the Pool:**\nOnly the pool owner can close the pool to new bets with ```!close-pool #<id>```\nExample:```!close-pool #4```\n\n"
    	helpmsg = "**Help Message:**\nSee this again with the command ```!bet-help```"

    	desc = placing + closing + helpmsg
    	emb = discord.Embed(description=desc,color=EMBCOLOR)
    	return emb

    def is_betting_member(self, memid):
    	members = data.bets["members"]
    	for m in members:
    		if int(m["id"]) == int(memid):
    			return True
    	return False

    def init_member(self, mem):
    	new_mem = {"id": mem.id, 
    			   "crowns": 100,
    			   "previous_bets": []}
    	data.bets["members"].append(new_mem)

def setup(bot):
	bot.add_cog(Bet(bot))

