import lyrics_providers.lyrics as lyrics
import lyrics_providers.covers as covers

async def search_lyrics(title: str, artist: str) -> dict | None:
    song = await lyrics.search_lyrics(title, artist)
    if song is None:
        return None

    if song.get('cover', {}).get('url') is None:
        cover = await covers.fetch_cover(title, artist)
        if cover:
            song['cover']['url'] = cover
    return song
