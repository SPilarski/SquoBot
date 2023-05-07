import os
import aiohttp

from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TWITCH_USERNAMES = os.getenv('TWITCH_USERNAMES').split(',')

streamer_statuses = {username: False for username in TWITCH_USERNAMES}

async def get_twitch_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            token_data = await response.json()
            return token_data['access_token']

async def get_streamer_status(username, client_id, token):
    url = f'https://api.twitch.tv/helix/streams'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    params = {
        'user_login': username
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            return data['data'][0] if data['data'] else None

@tasks.loop(minutes=5)
async def check_stream_status(channel):
    twitch_token = await get_twitch_token(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)

    for username in TWITCH_USERNAMES:
        stream_data = await get_streamer_status(username, TWITCH_CLIENT_ID, twitch_token)

        if stream_data and not streamer_statuses[username]:
            await channel.send(f'{username} jest online https://www.twitch.tv/{username}')
            streamer_statuses[username] = True
        elif not stream_data:
            streamer_statuses[username] = False
