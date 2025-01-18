import aiohttp
import threading
import os
import time

import lyricsgenius as lg
from flask_cors import CORS
from io import BytesIO
from flask import Flask, Blueprint, request, send_file

from share import shareLyrics
from share import getDominantColor
from genius import search, parseTitle, parseImg, parseLyrics, parseAuthor
from genius import download_cover, get_local_cover, load_local_song

from cfg import NOT_FOUND_MSG, TOKEN, BASE_PATH, HOST

genius = lg.Genius(TOKEN)

api = Blueprint('api', __name__, url_prefix='/api')
app = Flask(__name__)
CORS(app)


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
    
    if res is None or im is None:
        return 'No image found :/'

    color = '#' + ''.join(hex(c)[2:].zfill(2) for c in getDominantColor(im))

    img_io = BytesIO()
    img = shareLyrics(im, res['author'], res['title'], '\n'.join(request.get_json()), color)
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@api.route('/lyrics')
async def getLyrics():
    title = request.args['t'].replace('..', '').replace('/', '')
    artist = request.args['a'].replace('..', '').replace('/', '')

    search_res = await search(title, artist)

    if search_res is None:
        return NOT_FOUND_MSG

    song_id = search_res['api_path'].split('/')[2]

    print(search_res['path'])

    data = await load_local_song(song_id)
    if data is None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://genius.com' + search_res['path']) as res:
                data = await res.text()

        data = {
            'lyrics': parseLyrics(data),
            'title': parseTitle(data),
            'author': parseAuthor(data),
            'cover': {'url': parseImg(data)},
            'song_id': song_id,
        }

    if not os.path.exists(f'{BASE_PATH}/cache/covers/{song_id}.jpg') or not os.path.exists(f'{BASE_PATH}/cache/metadata/{song_id}.json'):
        thread = threading.Thread(target=download_cover, args=(data,))
        thread.start()

    return data

@api.route('/')
@app.route('/')
async def home():
    return '<h1>Sgrodolix API</h1>'

app.register_blueprint(api)

if __name__ == '__main__':
    CACHE_PATH = os.path.join(BASE_PATH, 'cache')
    COVERS_PATH = os.path.join(CACHE_PATH, 'covers')
    DATA_PATH = os.path.join(CACHE_PATH, 'metadata')
    if not os.path.exists(CACHE_PATH): os.mkdir(CACHE_PATH)
    if not os.path.exists(COVERS_PATH): os.mkdir(COVERS_PATH)
    if not os.path.exists(DATA_PATH): os.mkdir(DATA_PATH)

    app.run(HOST[0], HOST[1], debug=False)
