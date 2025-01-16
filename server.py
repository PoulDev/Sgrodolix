import aiohttp
import requests
import threading
import json
import os
import logging
import time

from PIL import Image
import lyricsgenius as lg
from flask_cors import CORS
from share import shareLyrics
from io import BytesIO
from extract import getDominantColor, getAllDominantColors
from flask import Flask, Blueprint, request, send_file

from cfg import NOT_FOUND_MSG, TOKEN, BASE_PATH, HOST

genius = lg.Genius(TOKEN)

api = Blueprint('api', __name__, url_prefix='/api')
app = Flask(__name__)
CORS(app)

async def load_remote_song(song_id, full_title, artist, path):
    for _ in range(3):
        try: lyrics = genius.lyrics(song_url=path, remove_section_headers=False).splitlines()
        except: pass
        else: break

    while '' in lyrics: lyrics.remove('')
    data = {
        'lyrics': lyrics,
        'title': full_title,
        'author': artist,
        'song_id': song_id,
    }

    return data

async def load_local_song(song_id: str) -> dict:
    if os.path.exists(f'{BASE_PATH}/cache/metadata/{song_id}.json'):
        logging.info('Metadata found locally!')
        with open(f'{BASE_PATH}/cache/metadata/{song_id}.json', 'r') as f:
            data = json.loads(f.read())
    else:
        data = None #parse_song(song_id, palette)
    return data

def get_remote_cover(song_id, cover_art_url):
    photo = requests.get(cover_art_url).content
    im = Image.open(BytesIO(photo))
    im = im.resize((256, 256))
    im = im.convert('RGB')
    im.save(f'{BASE_PATH}/cache/covers/{song_id}.jpg', 'JPEG', quality=70)
    return im

async def get_local_cover(song_id):
    if not os.path.exists(f'{BASE_PATH}/cache/covers/{song_id}.jpg'):
        return None

    logging.info('Cover found locally!')
    return Image.open(f'{BASE_PATH}/cache/covers/{song_id}.jpg')


@api.route('/share', methods=['POST'])
async def share():
    song_id = request.args['song_id']
    if '/' in song_id or '.' in song_id: 
        return 'poco chill da parte tua'

    for _ in range(10):
        if os.path.exists(f'{BASE_PATH}/cache/metadata/{song_id}.json'): break
        time.sleep(1)
    else:
        return 'Data download failed'

    for _ in range(10):
        if os.path.exists(f'{BASE_PATH}/cache/covers/{song_id}.jpg'): break
        time.sleep(1)
    else:
        return 'Cover download failed'

    res = await load_local_song(song_id)
    im = await get_local_cover(song_id)
    color = '#' + ''.join(hex(c)[2:].zfill(2) for c in getDominantColor(im))

    img_io = BytesIO()
    img = shareLyrics(im, res['author'], res['title'], '\n'.join(request.get_json()), color)
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

async def search(title, artist):
    res = None
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
                res = None
                for result in data['response']['hits']:
                    if result['type'] == 'song':
                        res = result['result']
                        return res
                break
    return res

@api.route('/lyrics')
async def getLyrics():
    title = request.args['t'].replace('..', '').replace('/', '')
    artist = request.args['a'].replace('..', '').replace('/', '')

    res = await search(title, artist)

    if res is None:
        return NOT_FOUND_MSG

    song_id = res['api_path'].split('/')[2]

    data = await load_local_song(song_id)
    if data is None:
        data = await load_remote_song(song_id, res['title'], res['artist_names'], res['path'])

    if not os.path.exists(f'{BASE_PATH}/cache/covers/{song_id}.jpg') or not os.path.exists(f'{BASE_PATH}/cache/metadata/{song_id}.json'):
        thread = threading.Thread(target=download_cover, args=(data,))
        thread.start()

    return data

def download_cover(data):
    song_id = data['song_id']
    
    song = None
    for _ in range(3):
        try:
            song = genius.song(song_id)
        except: pass
        else: break

    if song is None:
        logging.error('!! API ACCESS FAILED !!')
        return

    try:
        url = song['song']['album']['cover_art_url']
    except:
        url = song['song']['header_image_thumbnail_url']

    im =  get_remote_cover(song_id, url)
    palette = getAllDominantColors(im)


    data['cover'] = {'url': url}
    data['palette'] = palette

    with open(f'{BASE_PATH}/cache/metadata/{song_id}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))

@api.route('/')
@app.route('/')
async def home():
    return '<h1>Sgrodolex API</h1>'

app.register_blueprint(api)

if __name__ == '__main__':
    CACHE_PATH = os.path.join(BASE_PATH, 'cache')
    COVERS_PATH = os.path.join(CACHE_PATH, 'covers')
    DATA_PATH = os.path.join(CACHE_PATH, 'metadata')
    if not os.path.exists(CACHE_PATH): os.mkdir(CACHE_PATH)
    if not os.path.exists(COVERS_PATH): os.mkdir(COVERS_PATH)
    if not os.path.exists(DATA_PATH): os.mkdir(DATA_PATH)

    app.run(HOST[0], HOST[1], debug=False)
