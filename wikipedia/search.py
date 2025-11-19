import requests
from bs4 import BeautifulSoup

def get_author_image(author):
    res = requests.get(f'https://en.wikipedia.org/wiki/{author}', headers={
        'User-Agent': 'Sgrodolibrix'
    })

    soup = BeautifulSoup(res.text, 'html.parser')
    td = soup.find('td', class_='infobox-image')
    if td is None:
        return None

    img = td.find('img')
    if img is None:
        return None

    url = img['src']
    if url.startswith('//'):
        url = 'https:' + url

    return url


if __name__ == '__main__':
    print(get_author_image("John Von Neumann"))
