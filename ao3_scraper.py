import discord

from bs4 import BeautifulSoup
import requests
import settings

EMBCOLOR=settings.AO3_COLOR

def ao3_embed(msg):
	url = get_url(msg)
	req = requests.get(url)
	soup = BeautifulSoup(req.content, 'html.parser')
	emb = discord.Embed(color=EMBCOLOR)

	# author
	author = soup.find("a", {"rel": "author"})
	try:
		auth_url = "https://archiveofourown.org" + author['href']
		emb.set_author(name=author.string, url=auth_url, icon_url='https://archiveofourown.org/images/ao3_logos/logo_42.png')
	except:
		# if the fic is locked
		emb.set_author(name="Locked fic 🔒", url=url, icon_url='https://archiveofourown.org/images/ao3_logos/logo_42.png')
		return emb

	# fic title
	title = soup.find("h2", class_= "title heading")
	emb.title = title.string
	emb.url = url

	# fandoms
	fandoms = soup.find("dd", {"class": "fandom tags"}).findAll("a")
	fanstr = ""
	for f in fandoms:
		fanstr += "[{}]({}), ".format(f.string, "https://archiveofourown.org"+f['href'])
	emb.add_field(name="__Fandom__", value=fanstr[:-2], inline=True)

	# rating
	rating = soup.find("dd", {"class": "rating tags"})
	emb.add_field(name="__Rating__", value=rating.get_text(), inline=True)

	# archive warnings
	warnings = soup.find("dd", {"class": "warning tags"}).findAll("a")
	warnstr = ""
	for w in warnings:
		warnstr += "{}, ".format(w.string)
	emb.add_field(name="__Archive Warnings__", value=warnstr[:-2], inline=True)

	# words
	words = soup.find("dd", {"class": "words"})
	emb.add_field(name="__Words__", value=words.string, inline=True)

	# chapters
	chapters = soup.find("dd", {"class": "chapters"})
	emb.add_field(name="__Chapters__", value=chapters.string, inline=True)

	# pairings
	try:
		pairings = soup.find("dd", {"class": "relationship tags"}).findAll("a")
		relstr = ""
		for p in pairings:
			relstr += "[{}]({}), ".format(p.string, "https://archiveofourown.org"+p['href'])
	except:
		relstr = "None, "
	emb.add_field(name="__Relationships__", value=relstr[:-2], inline=False)

	# tags
	try:
		tags = soup.find("dd", {"class": "freeform tags"}).findAll("a")
		tagstr = ""
		for i in range(len(tags)):
			t = tags[i]
			if len(tagstr) + len(t.string) > 1000:
				tagstr += "+{}, ".format(len(tags)-i)
				break
			tagstr += "{}, ".format(t.string)
	except:
		tagstr = "None, "
	emb.add_field(name="__Tags__", value=tagstr[:-2], inline=False)

	# summary
	summary = soup.find("blockquote", {"class": "userstuff"}).get_text()
	if len(summary) < 1010:
		emb.add_field(name="__Summary__", value=summary, inline=False)
	else:
		emb.add_field(name="__Summary__", value=summary[:1010]+"...", inline=False)

	return emb

def get_url(msg):
	st = msg.find("archiveofourown.org")
	end = 0
	for x in range(st+26,len(msg)):
		if not msg[x].isdigit():
			end = x
			break
		if x == len(msg) - 1:
			end = x + 1
			break

	return "https://"+msg[st:end]
