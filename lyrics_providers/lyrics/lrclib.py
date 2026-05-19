import aiohttp
import logging
import re
import urllib.parse
from typing import Optional

from cfg import TOKEN, PROXIES, get_proxy
from lyrics_providers.base import LyricsProvider


def strip_timestamps(lyrics: str) -> list[str]:
    lines = []
    for line in lyrics.split('\n'):
        cleaned = re.sub(r'^\[\d{2}:\d{2}\.\d{2,3}\]\s*', '', line).strip()
        if not cleaned:
            continue
        if re.match(r'^\[[a-z]+:', cleaned, re.IGNORECASE):
            continue
        lines.append(cleaned)
    return lines


class LRCLibProvider(LyricsProvider):
    async def search(self, title: str, artist: str) -> Optional[dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f'https://lrclib.net/api/search?track_name={urllib.parse.quote(title)}&artist_name={urllib.parse.quote(artist)}'
                async with session.get(url,
                                       timeout=aiohttp.ClientTimeout(total=10),
                                       proxy=get_proxy()) as res:
                    if res.status != 200:
                        return None
                    data = await res.json()
            except (aiohttp.ClientError, TimeoutError):
                logging.exception('LRCLib search failed')
                return None

        if not data:
            return None

        best = data[0]
        lyrics_text = best.get('plainLyrics') or best.get('syncedLyrics', '')
        if not lyrics_text:
            return None

        if best.get('syncedLyrics'):
            lyrics_lines = strip_timestamps(best['syncedLyrics'])
        else:
            lyrics_lines = lyrics_text.split('\n')

        song_id = f"lrclib_{best['id']}"

        return {
            'song_id': song_id,
            'title': best.get('trackName', 'Unknown'),
            'author': best.get('artistName', 'Unknown'),
            'lyrics': lyrics_lines,
            'cover': {'url': None},
            'provider': 'lrclib',
            'album_name': best.get('albumName'),
            'duration': best.get('duration'),
        }

    async def get_lyrics(self, song_data: dict) -> dict:
        return song_data
