import discord
import requests
import random
import json
import os
import asyncio
from discord.ext import commands
from discord import Game

loop = asyncio.get_event_loop()
bot = commands.Bot(command_prefix='!')

#console outputs for monitoring
@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name="type !help for command list"))
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	
#shiba command sends random shibas
@bot.command(description = 'Sends a picture of a shiba.', brief = 'Sends a picture of a shiba.', usage = '', help = 'Uses shibe.online to send you some shibas.')
async def shiba(ctx):
	rImage = requests.get('http://shibe.online/api/shibes?count=1&urls=true&httpsUrls=false')
	if (rImage.status_code == 200):
		loop.create_task(sendImage(ctx, rImage.text[rImage.text.find('["') + 2:rImage.text.rfind('"]')]))
	else:
		await ctx.send('The Server is currently experiencing some issues. Please try again later')

#cat command sends random cats
@bot.command(description = 'Sends a picture of a cat.', brief = 'Sends a picture of a cat.', usage = '', help = 'Uses shibe.online to send you some cats.')
async def cat(ctx):
	rImage = requests.get('http://shibe.online/api/cats?count=1&urls=true&httpsUrls=false')
	if (rImage.status_code == 200):
		loop.create_task(sendImage(ctx, rImage.text[rImage.text.find('["') + 2:rImage.text.rfind('"]')]))
	else:
		await ctx.send('The Server is currently experiencing some issues. Please try again later')

#bird command sends random birds		
@bot.command(description = 'Sends a random image of a bird.', brief = 'Sends a random image of a bird.', usage = '', help = 'Uses shibe.online to send you some birds.')
async def bird(ctx):
	rImage = requests.get('http://shibe.online/api/birds?count=1&urls=true&httpsUrls=false')
	if (rImage.status_code == 200):
		loop.create_task(sendImage(ctx, rImage.text[rImage.text.find('["') + 2:rImage.text.rfind('"]')]))
	else:
		await ctx.send('The Server is currently experiencing some issues. Please try again later')
	
#dog command sends random or specified dogs	
@bot.command(description = 'Sends a picture of a dog.\nUse the optional -breed parameter to search for breeds or the optional breed parameter to get a picture of a specified breed.', brief = 'Sends a picture of a dog.', usage = '[-breed/breed]', help = 'Uses dog.ceo to send you some dogs.')
async def dog(ctx, param = None):
	if (param == None):
		rImage = requests.get('http://dog.ceo/api/breeds/image/random')
		link = json.loads(rImage.text)
		if (link["message"].startswith('http') and rImage.status_code == 200):
			loop.create_task(sendImage(ctx, link["message"]))
		else:
			await ctx.send('The Server is currently experiencing some issues. Please try again later')
	if (param == "-breeds"):
		rBreeds = requests.get('https://dog.ceo/api/breeds/list')
		link = json.loads(rBreeds.text)
		if (rBreeds.status_code == 200):
			await ctx.send('```Available breeds:\n%s```' % (", ".join(link["message"])))
		else:
			await ctx.send('The Server is currently experiencing some issues. Please try again later')
	else:
		rImage = requests.get('http://dog.ceo/api/breed/%s/images/random' % (param.lower()))
		link = json.loads(rImage.text)
		if (rImage.status_code == 200):
			if (link["message"].startswith('http')):
				loop.create_task(sendImage(ctx, link["message"]))
		else:
			if (rImage.status_code == 404):
				await ctx.send("Breed not found")
			else:
				await ctx.send('The Server is currently experiencing some issues. Please try again later')

#catgirl command sends random catgirls
@bot.command(description = 'Sends a picture of a catgirl. Use the optional -nsfw parameter to get lewd pictures (only works in nsfw-channels)', brief = 'Sends a picture of a catgirl.', usage = '[-nsfw]', help = 'Uses Danbooru to send you some catgirls.')
async def catgirl(ctx, param = None):
	if (param == None):
		score = 0
		while(score < 5 and requests.get('https://danbooru.donmai.us').status_code == 200):
			rPost = requests.get('https://danbooru.donmai.us/posts/random.json?tags=cat_ears+rating:s+filesize:200kb..8M')
			post = json.loads(rPost.text)
			score = post['score']
		if (requests.get('https://danbooru.donmai.us').status_code == 200 and len(rPost.text) > 2):
			if (post['pixiv_id'] != 'null'):
				if (post['source'] is not 'None' and post['source'] is not None):
					loop.create_task(sendImage(ctx, post['large_file_url'], 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s' % (post['pixiv_id'])))
			else:
				if (post['source'] is not 'None' and post['source'] is not None):
					loop.create_task(sendImage(ctx, post['large_file_url'], post['source']))
		else:
			await ctx.send('The Server is currently experiencing some issues. Please try again later')
	if (param == "-nsfw"):
		if (ctx.channel.is_nsfw()):
			score = 0
			while(score < 5 and requests.get('https://danbooru.donmai.us').status_code == 200):
				rPost = requests.get('https://danbooru.donmai.us/posts/random.json?tags=cat_ears+rating:e')
				post = json.loads(rPost.text)
				score = post['score']
			if (requests.get('https://danbooru.donmai.us').status_code == 200 and len(rPost.text) > 2):
				if (post['pixiv_id'] != 'null'):
					if (post['source'] is not 'None' and post['source'] is not None):
						loop.create_task(sendImage(ctx, post['large_file_url'], 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s' % (post['pixiv_id'])))
				else:
					if (post['source'] is not 'None' and post['source'] is not None):
						loop.create_task(sendImage(ctx, post['large_file_url'], post['source']))
			else:
				await ctx.send('The Server is currently experiencing some issues. Please try again later')
		else:
			await ctx.send("You can't use this command outside of nsfw-channels")

#danbooru command sends random images from danbooru, specified by tag
@bot.command(description = 'Sends a picture from Danbooru with a specified tag. Use the tag parameter to search for the picture, the optional -nsfw parameter (which only works in nsfw-channels) gives you lewd pictures, or the -search parameter to search for tags', brief = 'Sends a specified picture from Danbooru.', usage = "tag/'-search tag' [-nsfw]", help = 'Uses shibe.online to send you some shibas.')
async def danbooru(ctx, param1, param2 = None):
	if (param1 == "-search"):
		if (param2 != None):
			r = requests.get('https://danbooru.donmai.us/tags.json?search[name_matches]=*%s*&search[order]=count&limit=50' % (param2))
			link = json.loads(r.text)
			if (r.status_code == 200):
				tags = ''
				for x in link:
					tags += ('%s\n' % (x["name"]))
				await ctx.send('```Available tags:\n%s```' % (tags))
			else:
				await ctx.send('The Server is currently experiencing some issues or your searchword was incorrect')
		else:
			await ctx.send('Please specify a searchword')
	if (param1 != "-search" and param2 == None):
		score = 0
		while(score < 5 and requests.get('https://danbooru.donmai.us').status_code == 200):
			rPost = requests.get('https://danbooru.donmai.us/posts/random.json?tags=%s+rating:s+filesize:200kb..8M' % (param1))
			post = json.loads(rPost.text)
			score = post['score']
		if (requests.get('https://danbooru.donmai.us').status_code == 200 and len(rPost.text) > 2):
			if (post['pixiv_id'] != 'null'):
				if (post['source'] is not 'None' and post['source'] is not None):
					loop.create_task(sendImage(ctx, post['large_file_url'], 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s' % (post['pixiv_id'])))
			else:
				if (post['source'] is not 'None' and post['source'] is not None):
					loop.create_task(sendImage(ctx, post['large_file_url'], post['source']))
		else:
			await ctx.send('The Server is currently experiencing some issues or your tag was not found')
	if (param1 != "-search" and param2 == '-nsfw'):
		if (ctx.channel.is_nsfw()):
			score = 0
			while(score < 5 and requests.get('https://danbooru.donmai.us').status_code == 200):
				rPost = requests.get('https://danbooru.donmai.us/posts/random.json?tags=%s+rating:e' % (param1))
				post = json.loads(rPost.text)
				score = post['score']
			if (requests.get('https://danbooru.donmai.us').status_code == 200 and len(rPost.text) > 2):
				post = json.loads(rPost.text)
				if (post['pixiv_id'] != 'null'):
					if (post['source'] is not 'None' and post['source'] is not None):
						loop.create_task(sendImage(ctx, post['large_file_url'], 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s' % (post['pixiv_id'])))
				else:
					if (post['source'] is not 'None' and post['source'] is not None):
						loop.create_task(sendImage(ctx, post['large_file_url'], post['source']))
			else:
				await ctx.send('The Server is currently experiencing some issues or your searchword was not found')
		else:
			await ctx.send("You can't use the -nsfw parameter here")

#method downloads and sends image with source
async def sendImage(ctx, link, source = None):
	if(source == None):
		source = link
	if(link.endswith('.jpg')):
		filename = 'temp.jpg'
	if(link.endswith('.png')):
		filename = 'temp.png'
	if ('filename' in locals()):
		rPic = requests.get(link, stream=True)
		with open(filename, 'wb') as image:
			for chunk in rPic:
				image.write(chunk)
		try:
			await ctx.send('Source: <%s>' % (source), file=discord.File(filename, filename))
		except:
			await ctx.send('Something went wrong. Try again and contact www.twitter.com/pistonfish if this error continues to show up')
		os.remove(filename)

bot.run(os.environ['TOKEN'])