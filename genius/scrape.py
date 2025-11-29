import aiohttp
import requests
import random
import re
from bs4 import BeautifulSoup
import urllib.parse

from cfg import TOKEN

USER_AGENTS = [{"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3", "pct": 40.98}, {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.1", "pct": 12.7}, {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.1", "pct": 12.43}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.", "pct": 8.74}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.", "pct": 6.01}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.", "pct": 6.01}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.", "pct": 2.73}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.", "pct": 2.19}, {"ua": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.", "pct": 2.19}, {"ua": "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.", "pct": 1.09}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.", "pct": 1.09}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.", "pct": 1.09}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3", "pct": 1.09}, {"ua": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.", "pct": 0.55}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.", "pct": 0.55}, {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3", "pct": 0.55}]

def getHeaders():
    return {
        "Host": "genius.com",
        "User-Agent": random.choice(USER_AGENTS)['ua'],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://genius.com/",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "DNT": "1",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }

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
            br.replace_with('<br>')

        text = tag.get_text(strip=True).splitlines()
        for line in text:
            lyrics += line.split('<br>')

    for exclude in soup.find_all('div', attrs={"data-exclude-from-selection": "true"}):
        values = exclude.get_text(strip=True, separator='\n').splitlines()
        for value in values:
            if value in lyrics:
                lyrics.remove(value)

    return lyrics

def parseTitle(content):
    # SongHeader-desktop__HiddenMask-sc-ffb24f94-11 dHpSmS
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.find('span', class_=re.compile('SongHeader.{0,5}-desktop'))
    if title is None:
        title = 'Unknown'
    else:
        title = title.get_text()

    return title

def parseTitleFromLyrics(lyrics):
    try:
        first_line = lyrics[0]
        start = first_line.index('"')+1
        return first_line[start:-2]
    except ValueError as e:
        print(e)
        print('first 3 lines', lyrics[:3])
        return 'Unknown'

def parseAuthor(content):
    soup = BeautifulSoup(content, 'html.parser')
    author = soup.find('a', class_=lambda x: x and 'StyledLink' in x, attrs={"href": re.compile(r'^https://genius.com/artists/\w+')})
    if author is None:
        author = 'Unknown'
    else:
        author = author.get_text()

    return author

def parseImg(content, song_id):
    # Genius keeps changing where they put their fucking cover image, so
    # I'll just keep adding the new methods without removing the old ones,
    # because I don't know which one are deprecated and which one are not.
    # Let's maximise the success rate i guess

    soup = BeautifulSoup(content, 'html.parser')
    img_url = None
    
    # Method N. 1 - Big album cover on the page
    img = soup.find('img', class_=re.compile(r'SizedImage.*'), attrs={"src": re.compile(r'https:\/\/.*')})
    if not img is None:
        img_url = img['src']

    if img_url: return img_url

    # Method N. 2 - Album cover in the <meta> tag
    meta = soup.find('meta', attrs={"property": "og:image"})
    if not meta is None:
        img_url = meta['content']

    if img_url: return img_url

    # Method N. 3 - Album cover in another <meta> tag...
    meta = soup.find('meta', attrs={"property": "twitter:image"})
    if not meta is None:
        img_url = meta['content']

    if img_url: return img_url

    # Method N. 4 - Album cover in some stupid json metadata
    # This could be useful but it doesn't work in the current state
    '''
    substr = '\\"imageUrl\\":'
    try:
        index = content.index(substr) + len(substr)
        section = content[index:]
        start = section.index('"') + 1
        end = section.index('"', start)
        img_url = section[start:end]
    except:
        img_url = None

    if img_url: return img_url
    '''

    # Method N. 5 - I don't really remember how this works
    for im in soup.find_all('img', attrs={'class': re.compile(r'SizedImage-.*SongHeader-desktop-.*')}):
        if im.get('src') is None: continue
        img = im
        break

    if not img is None: 
        img_url = img['src']

    if img_url: return img_url

    # Method N. 6 - Get the image from apple music :/
    img_url = appleMusicImage(song_id)

    return img_url


async def search(title, artist) -> dict | None:
    for _ in range(3):
        # Sorry for the nesting hell
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://api.genius.com/search?q=' + urllib.parse.quote_plus(title) + '%20' + urllib.parse.quote_plus(artist),
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

