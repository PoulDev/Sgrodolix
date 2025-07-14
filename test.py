import requests
from genius.scrape import parseAuthor, parseTitle, parseImg, getHeaders

content = requests.get('https://genius.com/The-blake-robinson-synthetic-orchestra-an-unhealthy-obsession-annotated', headers=getHeaders()).text

with open('out.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(parseAuthor(content))
print(parseTitle(content))
print(parseImg(content, None))

