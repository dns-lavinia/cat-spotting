import asyncio
import discord
from datetime import datetime, time, timedelta
from discord.ext import commands

import bot_constants

# consider the prefix for the commands to be '!'
bot = commands.Bot(command_prefix='!')

################################################################################
##### BOT EVENTS

# This function is going to be called once a day
# For every daily message, send some statistics
async def send_stats():
	print("Sending statistics to server")

	message = f"[{datetime.now().date()}]\n" +\
				"- Total 🐈 spotted: 0\n" +\
				"- 🐈 spotted in the last 24 hours: 0\n" +\
				"- Temperature today: 25℃"

	await bot.wait_until_ready()
	channel = bot.get_guild(int(bot_constants.GUILD_ID)).get_channel(int(bot_constants.CHANNEL_ID))

	await channel.send(message)


async def cat_instant_stats():
	message = f"[{datetime.now()}]\n" +\
				"- Temperature: 30℃"

	await bot.wait_until_ready()
	channel = bot.get_guild(int(bot_constants.GUILD_ID)).get_channel(int(bot_constants.CHANNEL_ID))

	await channel.send(message)


async def background_task():
	now = datetime.utcnow()

	# If the first loop is going to start after the set time
	# make sure that the stats are not sent right away
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
		await once_a_day_stats()

		tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))

		# number of seconds until tomorrow
		seconds = (tomorrow - now).total_seconds()

		# sleep until tomorrow
		await asyncio.sleep(seconds)


async def background_task_instants():
	"""Check for new cat instants (new snaphsots of cats during the day) and
	send a message with an image and some additional information"""

	while True:
		now = datetime.utcnow()
		target_time = now + timedelta(minutes=bot_constants.CAT_INSTANT_MINUTES)
		seconds_until_target = (target_time - now).total_seconds()

		# sleep until the target is met
		await asyncio.sleep(seconds_until_target)

		# call the function that sends the stats to the channel
		await cat_instant_stats()


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
	bot.loop.create_task(background_task())
	bot.loop.create_task(background_task_instants())
	bot.run(bot_constants.DISCORD_TOKEN)
