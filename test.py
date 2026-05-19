'''
import requests
from genius.scrape import parseAuthor, parseTitle, parseImg, parseLyrics, getHeaders

content = requests.get('https://genius.com/Tonypitony-culo-lyrics', headers=getHeaders()).text

with open('out.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n'.join(parseLyrics(content)))
print(parseAuthor(content))
print(parseTitle(content))
print(parseImg(content, None))
'''

import requests
from genius.cover import get_remote_cover
from share.share import shareLyrics
from genius.scrape import parseAuthor, parseTitle, parseImg, parseLyrics, getHeaders

content = requests.get('https://genius.com/Caparezza-ti-sorrido-mentre-affogo-lyrics', headers=getHeaders()).text

with open('out.html', 'w', encoding='utf-8') as f:
    f.write(content)

img = shareLyrics(get_remote_cover('123', parseImg(content, '123')), parseAuthor(content), parseTitle(content), 'Se la sala è piena, il film fa schifo', '#b63236')
img.show()
