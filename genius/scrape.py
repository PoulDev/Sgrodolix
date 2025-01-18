import aiohttp
import re
from bs4 import BeautifulSoup

from cfg import TOKEN

def parseLyrics(lyrics) -> list[str]:
    soup = BeautifulSoup(lyrics, 'html.parser')
    lyrics = []

    for tag in soup.find_all('div', attrs={"data-lyrics-container": "true"}):
        for br in tag.find_all('br'):
            br.replace_with('\n')

        lyrics += tag.get_text(strip=True, separator='\n').splitlines()

    return lyrics

def parseTitle(lyrics):
    soup = BeautifulSoup(lyrics, 'html.parser')
    title = soup.find('span', class_=re.compile(r'^SongHeader-desktop-\w+'))
    if title is None:
        title = 'Unknown'
    else:
        title = title.get_text()

    return title

def parseAuthor(lyrics):
    soup = BeautifulSoup(lyrics, 'html.parser')
    author = soup.find('a', class_=re.compile(r'^StyledLink-\w+'), attrs={"href": re.compile(r'^https://genius.com/artists/\w+')})
    if author is None:
        author = 'Unknown'
    else:
        author = author.get_text()

    return author

def parseImg(lyrics):
    soup = BeautifulSoup(lyrics, 'html.parser')
    img = soup.find('img', class_=re.compile(r'SizedImage-sc-\w+'), attrs={"src": re.compile(r'https://images.genius.com/\w+')})
    if img is None:
        for img in soup.find_all('img', class_=re.compile(r'^SizedImage-sc-\w+')):
            if 'SongHeader-desktop-' in img['class']:
                img = img['src']
                break
    else:
        img = img['src']

    return img


async def search(title, artist) -> dict | None:
    for _ in range(3):
        # Sorry for the nesting hell
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://api.genius.com/search?q=' + title + '%20' + artist,
                                        headers={'Authorization': f'Bearer {TOKEN}'},
                                        timeout=aiohttp.ClientTimeout(total=5)) as res:
                    data = await res.json()
            except (aiohttp.ClientError, TimeoutError):
                pass
            else:
                break
    else: # Data not set 
        return None

    res = None
    for result in data['response']['hits']:
        if result['type'] == 'song':
            res = result['result']
            return res
    return res

