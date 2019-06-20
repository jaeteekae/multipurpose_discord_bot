import discord
from discord.ext import commands

import time

from data import data
from settings import *
from helpers import *


class Out_of_Office(commands.Cog, name="Out of Office"):
    @commands.command(help="Set yourself away for when people mention you in chat", 
                	  usage="<message_here>")
    async def away(self, ctx, *args):
        if not args:
            response = '{}: plz supply a message so we know why you are away'.format(ctx.author.mention)
            await ctx.send(response)
            return
        else:
            args = " ".join(args)

        emoji = get_emoji(ctx.guild, "jin_kiss")
        response = ''
        memid = str(ctx.author.id)
        now = time.time()
        msg = str(args)

        obj = {"time": now, "message": msg}
        data.away[memid] = obj

        response = 'Marking you away, {}, with the message *"{}"*\nWe will miss you {}'.format(ctx.author.mention, msg, emoji)
        await ctx.send(response)

    @commands.command(help="Use to stop being away")
    async def back(self, ctx, *args):
        memid = str(ctx.author.id)

        if memid not in data.away:
            emoji = get_emoji(ctx.guild, "v_derp")
            response = "You weren't away, {} {}".format(ctx.author.mention, emoji)
            await ctx.send(response)
            return
        else:
            obj = data.away.pop(memid)
            now = time.time()
            # elapsed in seconds
            elapsed = now - obj["time"]
            timestring = generate_timestring(elapsed)

            msg = "Welcome back, {}!".format(ctx.author.mention)
            desc = "__You were away for__: {}\n __You are no longer__: {}\n👋".format(timestring,obj["message"])
            emb = discord.Embed(description=desc,color=AWAY_COLOR)
            await ctx.send(msg,embed=emb)


def setup(bot):
	bot.add_cog(Out_of_Office(bot))

