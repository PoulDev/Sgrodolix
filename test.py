import requests
from genius.scrape import parseAuthor, parseTitle, getHeaders

content = requests.get('https://genius.com/Eminem-rap-god-lyrics', headers=getHeaders()).text

print(parseAuthor(content))
print(parseTitle(content))
