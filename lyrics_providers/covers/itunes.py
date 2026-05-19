import aiohttp
import json
import logging
from typing import Optional

from cfg import get_proxy


async def fetch_cover_url(title: str, artist: str) -> Optional[str]:
    query = f'{artist} {title}'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                'https://itunes.apple.com/search',
                params={
                    'term': query,
                    'entity': 'song',
                    'limit': 1,
                },
                timeout=aiohttp.ClientTimeout(total=10),
                proxy=get_proxy(),
            ) as res:
                if res.status != 200:
                    return None
                text = await res.text()
                data = json.loads(text)
        except (aiohttp.ClientError, TimeoutError, json.JSONDecodeError):
            logging.exception('iTunes search failed')
            return None

    results = data.get('results', [])
    if not results:
        return None

    art_url = results[0].get('artworkUrl100')
    if art_url:
        return art_url.replace('100x100', '600x600')
    return None
