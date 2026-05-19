import aiohttp
import logging
from typing import Optional

from cfg import get_proxy


async def fetch_cover_url(title: str, artist: str) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                'https://musicbrainz.org/ws2/recording',
                params={
                    'query': f'recording:"{title}" AND artist:"{artist}"',
                    'fmt': 'json',
                    'limit': 5,
                },
                headers={'User-Agent': 'Sgrodolix/1.0 ( https://github.com/loricso/sgrodolix )'},
                timeout=aiohttp.ClientTimeout(total=10),
                proxy=get_proxy(),
            ) as res:
                if res.status != 200:
                    return None
                mb_data = await res.json()
        except (aiohttp.ClientError, TimeoutError):
            logging.exception('MusicBrainz search failed')
            return None

    recordings = mb_data.get('recordings', [])
    if not recordings:
        return None

    for recording in recordings:
        releases = recording.get('releases', [])
        for release in releases:
            mbid = release.get('id')
            if not mbid:
                continue
            try:
                async with session.get(
                    f'https://coverartarchive.org/release/{mbid}',
                    headers={'Accept': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=10),
                    proxy=get_proxy(),
                    allow_redirects=False,
                ) as caa_res:
                    if caa_res.status == 200:
                        caa_data = await caa_res.json()
                        for img in caa_data.get('images', []):
                            if img.get('front'):
                                thumbs = img.get('thumbnails', {})
                                return thumbs.get('1200') or thumbs.get('500') or img.get('image')
                    elif caa_res.status == 404:
                        continue
            except (aiohttp.ClientError, TimeoutError):
                continue

    return None
