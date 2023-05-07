# spotify.py
import os
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import tasks

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_USERNAME = os.getenv('SPOTIFY_USERNAME')
SPOTIFY_FOLLOWED_ARTISTS = os.getenv('SPOTIFY_FOLLOWED_ARTISTS').split(',')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope="user-library-read user-follow-read",
                                               username=SPOTIFY_USERNAME))

artist_new_release_timestamps = {artist_id: None for artist_id in SPOTIFY_FOLLOWED_ARTISTS}


def calculate_time_until_midnight():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
    return (midnight - now).seconds


async def check_artist_new_releases(channel):
    for artist_id in SPOTIFY_FOLLOWED_ARTISTS:
        albums = sp.artist_albums(artist_id, limit=10)
        latest_album = None

        for album in albums['items']:
            release_date = datetime.strptime(album['release_date'], '%Y-%m-%d')
            if latest_album is None or release_date > datetime.strptime(latest_album['release_date'], '%Y-%m-%d'):
                latest_album = album

        if latest_album:
            latest_release_timestamp = artist_new_release_timestamps[artist_id]
            latest_release_date = datetime.strptime(latest_album['release_date'], '%Y-%m-%d')

            if latest_release_timestamp is None or latest_release_date > latest_release_timestamp:
                artist_new_release_timestamps[artist_id] = latest_release_date
                album_name = latest_album['name']
                album_url = latest_album['external_urls']['spotify']
                artist_name = latest_album['artists'][0]['name']
                await channel.send(f'Nowy album od {artist_name}: {album_name}. Link: {album_url}')


@tasks.loop(seconds=calculate_time_until_midnight())
async def check_new_releases_at_midnight(channel):
    await check_artist_new_releases(channel)


def start_checking_new_releases(channel):
    check_new_releases_at_midnight.start(channel)
