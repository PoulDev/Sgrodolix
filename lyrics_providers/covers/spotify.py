import aiohttp
import base64
import logging
from typing import Optional

from cfg import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

_spotify_token: Optional[str] = None
_spotify_configured = SPOTIFY_CLIENT_ID != 'CHANGE ME' and SPOTIFY_CLIENT_SECRET != 'CHANGE ME'


async def _get_spotify_token() -> Optional[str]:
    global _spotify_token
    if _spotify_token:
        return _spotify_token
    if not _spotify_configured:
        return None

    credentials = base64.b64encode(f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'.encode()).decode()
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                'https://accounts.spotify.com/api/token',
                headers={
                    'Authorization': f'Basic {credentials}',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                data={'grant_type': 'client_credentials'},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as res:
                if res.status != 200:
                    return None
                data = await res.json()
                _spotify_token = data['access_token']
                return _spotify_token
        except (aiohttp.ClientError, TimeoutError):
            logging.exception('Spotify token fetch failed')
            return None
    return None


async def fetch_cover_url(title: str, artist: str) -> Optional[str]:
    token = await _get_spotify_token()
    if not token:
        return None

    query = f'track:{title} artist:{artist}'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                'https://api.spotify.com/v1/search',
                headers={'Authorization': f'Bearer {token}'},
                params={'q': query, 'type': 'track', 'limit': 1},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as res:
                if res.status != 200:
                    return None
                data = await res.json()
        except (aiohttp.ClientError, TimeoutError):
            logging.exception('Spotify search failed')
            return None

    tracks = data.get('tracks', {}).get('items', [])
    if not tracks:
        return None

    images = tracks[0].get('album', {}).get('images', [])
    if images:
        return images[0]['url']
    return None
