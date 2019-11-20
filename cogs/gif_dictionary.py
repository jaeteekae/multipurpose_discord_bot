import discord
from discord.ext import commands
import os
import requests
import validators

import settings
from data import data
from helpers import *


class Gif_Dictionary(commands.Cog, name="Gif Dictionary"):

    def __init__(self, bot):
        self.bot = bot
        if not os.path.isdir(settings.STATIC_FOLDER):
            os.makedirs(settings.STATIC_FOLDER)
        if not os.path.isdir(settings.GIF_FOLDER):
            os.makedirs(settings.GIF_FOLDER)

    @commands.command(name="gif-add",
                     help="Add a gif (or image) to the gif dictionary", 
                     usage="<shortcut> <uploaded file OR URL>")
    async def gif_add(self, ctx, *args):
        if not args:
            await ctx.send("{}, plz resend & let me know what I should call this gif".format(ctx.author.mention))
            return

        shortcut = args[0].lower()
        url = ''

        if len(shortcut)>20:
            await ctx.send("{}, the shortcut `{}` is too long. Plz resend with shortcut under 20 characters".format(ctx.author.mention, shortcut))
            return

        # check if shortcut already exists
        if shortcut in data.gifs:
            await ctx.send("{}, the shortcut `{}` is already in use. Plz resend with a different one".format(ctx.author.mention, shortcut))
            return
            
        # img is attached
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        # img is a link
        else:
            if len(args)<2 or not validators.url(args[1]):
                await ctx.send("{}, it looks like you didnt send me a gif to save :(".format(ctx.author.mention))
                return
            url = args[1]
            _, ext = os.path.splitext(url)
            if not ext:
                await ctx.send("{}, it looks like you didnt send me a gif to save :( (the url needs to end in .gif/.png/etc)".format(ctx.author.mention))
                return

        # download img
        img_data = requests.get(url).content
        path = os.path.join(settings.GIF_FOLDER,shortcut+'.gif')
        with open(path, 'wb') as f:
            f.write(img_data)

        # add img to dictionary
        data.gifs[shortcut] = path
        await ctx.send("Success! Added `{}` to the Gif Dictionary".format(shortcut))


    @commands.command(name="gif-list",
                     help="See the gifs already in the gif dictionary", 
                     usage="[optional filter]")
    async def gif_list(self, ctx, *args):
        if args:
            pref = args[0].lower()
            msg = 'All gifs that contain `{}`:'.format(pref)
        else:
            pref = ''
            msg = 'All gifs in the dictionary:'

        shortcuts = data.gifs.keys()
        filtered = list(filter(lambda x: (pref in x), shortcuts))
        filtered.sort()

        desc = []
        for s in filtered:
            desc.append('✿ '+s)

        if len(filtered)==0:
            if pref:
                await ctx.send("There are no gifs that contain `{}` {}".format(pref,get_emoji(ctx.guild,'nj_cry')))
                return
            else:
                await ctx.send("There are no gifs in the dictionary {}".format(get_emoji(ctx.guild,'nj_cry')))
                return        

        emb = discord.Embed(description='\n'.join(desc),color=GIF_COLOR)
        if len(desc) > 10:
            await ctx.send("There were a lot of gifs, so I DMed you 😘".format(ctx.author.mention))
            await ctx.author.send(msg,embed=emb)
        else:
            await ctx.send(msg,embed=emb)


    @commands.command(name="gif-remove",
                     help="Remove a gif from the gif dictionary", 
                     usage="<shortcut>")
    async def gif_remove(self, ctx, *args):
        if len(args)<1:
            await ctx.send("You didn't give me anything to remove, {}... {}".format(ctx.author.mention,get_emoji(ctx.guild,'hs_nope')))
            return

        shortcut = args[0].lower()
        if shortcut not in data.gifs:
            await ctx.send("That shortcut doesn't match any gifs, {} 🤔".format(ctx.author.mention))
            return

        path = data.gifs.pop(shortcut)
        os.remove(path)
        await ctx.send("Successfully removed `{}` from the dictionary".format(shortcut))


    @commands.command(help="Use a gif from the dictionary", 
                     usage="<shortcut>")
    async def gif(self, ctx, *args):
        # don't interact if no arguments are sent
        if len(args)<1:
            return
        shortcut = args[0].lower()
        if shortcut not in data.gifs:
            await ctx.send("That shortcut doesn't match any gifs, {} 🤔".format(ctx.author.mention))
            return
        path = data.gifs[shortcut]
        _, fname = os.path.split(path)
        file = discord.File(path,filename=fname)
        await ctx.send(file=file)


    @commands.command(name="gif-rename",
                     help="Rename a gif in the gif dictionary", 
                     usage="<old shortcut> <new shortcut>")
    async def gif_rename(self, ctx, *args):
        if len(args)<2:
            await ctx.send("Seems like you're missing some arguments there, {} {}".format(ctx.author.mention,get_emoji(ctx.guild,'v_tea')))
            return

        old = args[0].lower()
        new = args[1].lower()

        if old not in data.gifs:
            await ctx.send("`{}` doesn't match anything in the dictionary, {} 🤔".format(old,ctx.author.mention))
            return
        if new in data.gifs:
            await ctx.send("{}, the shortcut `{}` is already in use. Plz resend with a different one".format(ctx.author.mention, new))
            return

        old_path = data.gifs.pop(old)        
        new_path = os.path.join(settings.GIF_FOLDER,new+'.gif')

        os.rename(old_path,new_path)
        data.gifs[new] = new_path
        await ctx.send("Success! `{}` is now called `{}`".format(old, new))


def setup(bot):
	bot.add_cog(Gif_Dictionary(bot))
