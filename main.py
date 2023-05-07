import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from twitch import check_stream_status

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    check_stream_status.start(channel)

bot.run(DISCORD_TOKEN)
