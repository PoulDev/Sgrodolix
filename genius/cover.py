import os
import json
import logging
import requests
from PIL import Image
from io import BytesIO

from cfg import BASE_PATH
from share import getAllDominantColors

def get_remote_cover(song_id, cover_art_url):
    photo = requests.get(cover_art_url).content
    im = Image.open(BytesIO(photo))
    im = im.resize((256, 256))
    im = im.convert('RGB')
    im.save(f'{BASE_PATH}/cache/covers/{song_id}.jpg', 'JPEG', quality=70)
    return im

def update_data(song_id, data):
    with open(f'{BASE_PATH}/cache/metadata/{song_id}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))

def download_cover(data):
    song_id = data['song_id']

    url = data['cover']['url']

    im =  get_remote_cover(song_id, url)
    palette = getAllDominantColors(im)

    data['palette'] = palette

    update_data(song_id, data)

async def get_local_cover(song_id):
    if not os.path.exists(f'{BASE_PATH}/cache/covers/{song_id}.jpg'):
        return None

    logging.info('Cover found locally!')
    return Image.open(f'{BASE_PATH}/cache/covers/{song_id}.jpg')
