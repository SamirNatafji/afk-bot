import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
AFK_CHANNEL_ID = int(os.getenv('AFK_CHANNEL_ID', '0'))
