import requests
from genius.scrape import parseAuthor, parseTitle, getHeaders

content = requests.get('https://genius.com/Eminem-rap-god-lyrics', headers=getHeaders()).text

with open('out.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(parseAuthor(content))
print(parseTitle(content))
