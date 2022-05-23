from os import getenv
from dotenv import load_dotenv
from datetime import time

# load the variable from .env
load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")
GUILD = getenv("DISCORD_GUILD")
WHEN_STATS = time(11, 30, 0) # summer time - 3hrs
GUILD_ID = getenv("CAT_GUILD_ID")
CHANNEL_ID = getenv("CAT_CHANNEL_ID")

# check every CAT_INSTANT_MINUTES whether new entires were added to the database
CAT_INSTANT_MINUTES = 5

INSTANTS_TABLE = getenv("INSTANTS_TABLE")

# temp files
CAT_COLORS_FILE = getenv("CAT_COLORS_FILE")
CAT_IMG_FILE = getenv("CAT_IMG_FILE")
