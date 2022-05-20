import asyncio
import discord
import sys
import cv2

from datetime import datetime, time, timedelta
from discord.ext import commands

# maybe delete these later
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import bot_constants

sys.path.append('../firebase-api/')

import catbase


# consider the prefix for the commands to be '!'
bot = commands.Bot(command_prefix='!')

def hex_to_rgb(color_hex):
	return tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))

def generate_color_grid(colors):
	whiteblankimage = 255 * np.ones(shape=[100, 300, 3], dtype=np.uint8)

	for i in range(3):
		r, g, b = hex_to_rgb(colors[i])
		square = 255 * np.ones(shape=[100, 300, 3], dtype=np.uint8)
		cv2.rectangle(whiteblankimage, pt1=(i*100,0), pt2=((i+1)*100,100), color=(r,g,b), thickness=-1)
	plt.imshow(whiteblankimage, aspect='auto')

	# convert np array to image and save it
	im = Image.fromarray(whiteblankimage)
	im.save(bot_constants.CAT_COLORS_FILE)


################################################################################
##### BOT EVENTS

async def once_a_day_stats(fb, target_time):
	"""once_a_day_stats is going to be called once a day, and send some statistics

	Parameters
	----------
	fb
		Catbase object used to manipulate firebase data"""

	# uncomment for debugging
	# print("Sending statistics to server")
	yesterday = datetime.combine(target_time.date() - timedelta(days=1), time(0))
	tb_name = bot_constants.INSTANTS_TABLE

	total_cats_nb = fb.len_for_table(tb_name)
	partial_cats_nb = fb.len_for_table(tb_name, yesterday, target_time)
	peak_hours = fb.get_peak_hours(bot_constants.INSTANTS_TABLE)

	message = f"[{datetime.now().date()}]\n" +\
				f"- Total 🐈 spotted: {total_cats_nb}\n" +\
				f"- 🐈 spotted in the last 24 hours: {partial_cats_nb}\n" +\
				f"- Cat peak hours: {peak_hours}"

	await bot.wait_until_ready()
	channel = bot.get_guild(int(bot_constants.GUILD_ID)).get_channel(int(bot_constants.CHANNEL_ID))

	await channel.send(message)


async def cat_instant_stats(fb):
	"""cat_instant_stats is going to be called every few minutes, and send some
	data, along a picture with the detected cat

	Parameters
	----------
	fb
		Catbase object used to manipulate firebase data"""
	tb_name = bot_constants.INSTANTS_TABLE

	end_time = datetime.utcnow()
	start_time = end_time - timedelta(minutes=bot_constants.CAT_INSTANT_MINUTES)

	docs = fb.query_interval(tb_name, start_time, end_time)

	for key, doc in docs.items():
		files_to_send = []
		message = f"[{datetime.now()}]\n" +\
					f"- Temperature: {doc['temperature']}℃"

		# download picture from the cloud
		# print('Downloading file')
		fb.download_file(doc['img_filename'], bot_constants.CAT_IMG_FILE)
		files_to_send.append(discord.File(bot_constants.CAT_IMG_FILE))
		# print('Finished downloading file')

		# generate cat color palette
		generate_color_grid(doc['cat_colors'])
		files_to_send.append(discord.File(bot_constants.CAT_COLORS_FILE))

		# upload to discord
		await bot.wait_until_ready()
		channel = bot.get_guild(int(bot_constants.GUILD_ID)).get_channel(int(bot_constants.CHANNEL_ID))

		await channel.send(message, files=files_to_send)


async def background_task(fb):
	now = datetime.utcnow()

	# If the first loop is going to start after the set time
	# make sure that the stats are nott sent right away
	if now.time() > bot_constants.WHEN_STATS:
		tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))

		# number of seconds until midnight
		seconds = (tomorrow - now).total_seconds()

		# sleep until tomorrow
		await asyncio.sleep(seconds)

	while True:
		now = datetime.utcnow()
		target_time = datetime.combine(now.date(), bot_constants.WHEN_STATS)
		seconds_until_target = (target_time - now).total_seconds()

		# sleep until the target is met
		await asyncio.sleep(seconds_until_target)

		# call the function that sends the stats to the channel
		await once_a_day_stats(fb, target_time)

		tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))

		# number of seconds until tomorrow
		seconds = (tomorrow - now).total_seconds()

		# sleep until tomorrow
		await asyncio.sleep(seconds)


async def background_task_instants(fb):
	"""Check for new cat instants (new snaphsots of cats during the day) and
	send a message with an image and some additional information"""

	while True:
		# call the function that sends the stats to the channel
		await cat_instant_stats(fb)

		now = datetime.utcnow()
		target_time = now + timedelta(minutes=bot_constants.CAT_INSTANT_MINUTES)
		seconds_until_target = (target_time - now).total_seconds()

		# sleep until the target is met
		await asyncio.sleep(seconds_until_target)


@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

	for guild in bot.guilds:
		print(f"- {guild.id} (name: {guild.name})")


################################################################################
##### BOT COMMANDS

@bot.command(name='alive', help='Returns a message if the bot is connected')
async def alive_check(ctx):
	response = 'I am alive!'

	await ctx.send(response)

@bot.command(name='set_location', help='Set the location to get weather from')
async def set_location(ctx, city):
	response = 'Setting location as: ' + city

	# TODO: add a check that the city name given is a valid city and only make
	# 		changes if it is valid, otherwise, send an appropriate message to
	# 		the server
	await ctx.send(response)


################################################################################
##### RUN THE BOT
if __name__ == "__main__":
	fb = catbase.Catbase()

	bot.loop.create_task(background_task(fb))
	bot.loop.create_task(background_task_instants(fb))
	bot.run(bot_constants.DISCORD_TOKEN)
