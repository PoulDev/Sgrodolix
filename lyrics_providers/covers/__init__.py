import logging
from typing import Optional

from lyrics_providers.covers.spotify import fetch_cover_url as spotify_cover
from lyrics_providers.covers.itunes import fetch_cover_url as itunes_cover
from lyrics_providers.covers.coverartarchive import fetch_cover_url as caa_cover

COVER_PROVIDERS = [
    ('spotify', spotify_cover),
    ('itunes', itunes_cover),
    ('coverartarchive', caa_cover),
]


async def fetch_cover(title: str, artist: str) -> Optional[str]:
    for name, fn in COVER_PROVIDERS:
        try:
            url = await fn(title, artist)
            if url:
                logging.info(f'Cover found via {name}')
                return url
        except Exception as e:
            logging.exception(f'Cover provider {name} failed')
            continue
    return None
