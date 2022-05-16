from os import getenv
from dotenv import load_dotenv
from datetime import time

# load the variable from .env
load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")
GUILD = getenv("DISCORD_GUILD")
WHEN_STATS = time(14, 38, 0) # summer time - 3hrs
GUILD_ID = getenv("CAT_GUILD_ID")
CHANNEL_ID = getenv("CAT_CHANNEL_ID")

# check every CAT_INSTANT_MINUTES whether new entires were added to the database
CAT_INSTANT_MINUTES = 5

INSTANTS_TABLE = getenv("INSTANTS_TABLE")
