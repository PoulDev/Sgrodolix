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

from share.quote import shareQuote

img = shareQuote('''\
Di che reggimento siete
fratelli?

Parola tremante
nella notte

Foglia appena nata\
''', 'Giuseppe Ungaretti', 'Fratelli')
img.show()
