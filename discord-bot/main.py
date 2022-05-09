import asyncio
import os 
from dotenv import load_dotenv
from datetime import datetime, time, timedelta
from discord.ext import commands

# consider the prefix for the commands to be '!'
bot = commands.Bot(command_prefix='!')

# load the variable from .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
WHEN_STATS = time(13, 41, 0) # 12:30 This will send a message at 15:30 Romanian summer time
GUILD_ID = os.getenv("CAT_GUILD_ID")
CHANNEL_ID = os.getenv("CAT_CHANNEL_ID")

# This function is going to be called once a day
# For every daily message, send some statistics 
async def once_a_day_stats():
	print("Sending statistics to server")

	message = f"[{datetime.now().date()}]\n" +\
				"- Total 🐈 spotted: 0\n" +\
				"- 🐈 spotted in the last 24hrs: 0\n" +\
				"- Temperature today: 25℃"

	await bot.wait_until_ready()
	channel = bot.get_guild(int(GUILD_ID)).get_channel(int(CHANNEL_ID))

	await channel.send(message)


async def background_task():
	now = datetime.utcnow()

	# If the first loop is going to start after the set time
	# make sure that the stats are not sent right away
	if now.time() > WHEN_STATS:
		tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))

		# number of seconds until midnight
		seconds = (tomorrow - now).total_seconds()

		# sleep until tomorrow
		await asyncio.sleep(seconds)

	while True:
		now = datetime.utcnow()
		target_time = datetime.combine(now.date(), WHEN_STATS)
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


@bot.event 
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

	for guild in bot.guilds:
		print(f"- {guild.id} (name: {guild.name})")


@bot.event 
async def on_message(message):
	if message.content == "hello":
		await message.channel.send("Hello there")


if __name__ == "__main__":
	bot.loop.create_task(background_task())
	bot.run(DISCORD_TOKEN)