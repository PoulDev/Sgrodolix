import aiohttp
import requests
import re
from bs4 import BeautifulSoup

from cfg import TOKEN

def appleMusicImage(song_id):
    apple_mess = requests.get(f'https://genius.com/songs/{song_id}/apple_music_player?react=1&x-ab-test-tonefuse_interstitial=undefined').text
    image_links = re.findall(r'https:\/\/images.genius.com\/.*\.png', apple_mess)

    if len(image_links) >= 1:
        return image_links[0]
    
    return None


def parseLyrics(content) -> list[str]:
    soup = BeautifulSoup(content, 'html.parser')
    lyrics = []

    for tag in soup.find_all('div', attrs={"data-lyrics-container": "true"}):
        for br in tag.find_all('br'):
            br.replace_with('\n')

        lyrics += tag.get_text(strip=True, separator='\n').splitlines()

    return lyrics

def parseTitle(content):
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.find('span', class_=re.compile(r'^SongHeader-desktop-\w+'))
    if title is None:
        title = 'Unknown'
    else:
        title = title.get_text()

    return title

def parseTitleFromLyrics(lyrics):
    first_line = lyrics[0]
    start = first_line.index('"')
    return first_line[start:-2]

def parseAuthor(content):
    soup = BeautifulSoup(content, 'html.parser')
    author = soup.find('a', class_=re.compile(r'^StyledLink-\w+'), attrs={"href": re.compile(r'^https://genius.com/artists/\w+')})
    if author is None:
        author = 'Unknown'
    else:
        author = author.get_text()

    return author

def parseImg(content, song_id):
    soup = BeautifulSoup(content, 'html.parser')
    img = soup.find('img', class_=re.compile(r'SizedImage-sc-\w+'), attrs={"src": re.compile(r'https://images.genius.com/\w+')})
    if img is None:
        for im in soup.find_all('img', attrs={'class': re.compile(r'SizedImage-.*SongHeader-desktop-.*')}):
            if im.get('src') is None: continue
            img = im['src']
            break
    else:
        img = img['src']

    if img is None: 
        # Get the image from apple music :|
        return appleMusicImage(song_id)

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
            except (aiohttp.ClientError, TimeoutError): pass
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

if __name__ == '__main__':
    res = requests.get('https://genius.com/Salmo-a-te-e-famiglia-lyrics').text
    print(parseImg(res, '9857491'))

