from abc import ABC, abstractmethod
from typing import Optional


class LyricsProvider(ABC):
    @abstractmethod
    async def search(self, title: str, artist: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_lyrics(self, song_data: dict) -> dict:
        pass


class CoverProvider(ABC):
    @abstractmethod
    async def fetch(self, title: str, artist: str) -> Optional[str]:
        pass
