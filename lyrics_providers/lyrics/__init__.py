import logging
from lyrics_providers.base import LyricsProvider
from lyrics_providers.lyrics.lrclib import LRCLibProvider
from lyrics_providers.lyrics.genius import GeniusProvider

PROVIDERS: list[LyricsProvider] = [
    LRCLibProvider(),
    GeniusProvider(),
]


async def search_lyrics(title: str, artist: str) -> dict | None:
    for provider in PROVIDERS:
        try:
            result = await provider.search(title, artist)
            logging.warning(f'Provider {provider.__class__.__name__} returned {result}')
            if result is not None:
                if result.get('lyrics') is None or len(result.get('lyrics', [])) == 0:
                    result = await provider.get_lyrics(result)
                return result
        except Exception as e:
            logging.exception(f'Provider {provider.__class__.__name__} failed')
            continue
    return None
