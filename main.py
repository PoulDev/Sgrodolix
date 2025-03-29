import aiohttp
import threading
import os
import time
import random

import lyricsgenius as lg
from flask_cors import CORS
from io import BytesIO
from flask import Flask, Blueprint, request, send_file

from share import shareLyrics
from share import getDominantColor
from genius import search, parseTitle, parseImg, parseLyrics, parseAuthor, parseTitleFromLyrics
from genius import download_cover, get_local_cover, load_local_song, update_data, getHeaders

from cfg import NOT_FOUND_MSG, TOKEN, BASE_PATH, HOST, PROMETHEUS_ENABLED

from stats.stats import stats, Prometheus

genius = lg.Genius(TOKEN)

api = Blueprint('api', __name__, url_prefix='/api')
app = Flask(__name__)

prometheus = None
if (PROMETHEUS_ENABLED):
    app.register_blueprint(stats)
    prometheus = Prometheus(app)

CORS(app)

@api.route('/share', methods=['POST'])
async def share():
    song_id = request.args['song_id']
    color = request.args.get('color', '')
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
    
    if res == {} or im is None:
        return 'No image found :/'

    # Check if the color is valid ( accepted: #fff, #ffffff, #ffffffff (RGB & RGBA) )
    if len(color) not in (8, 6, 3): color = None
    else:
        try: int(color, 16)
        except: color = None

    if color is None:
        color = '#' + ''.join(hex(c)[2:].zfill(2) for c in getDominantColor(im))
    else:
        color = '#' + color

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
    mustCorrect = data.get('title') == 'Unkown' or data.get('author') == 'Unknown' or data.get('cover', {}).get('url') is None
    if data == {} or mustCorrect:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://genius.com' + search_res['path'], headers=getHeaders()) as res:
                res_data = await res.text()

        lyrics = parseLyrics(res_data)
        title = parseTitle(res_data)
        if title == 'Unknown':
            title = parseTitleFromLyrics(lyrics)
        data.update({
            'lyrics': lyrics,
            'title':  title,
            'author': parseAuthor(res_data),
            'cover': {'url': parseImg(res_data, song_id)},
            'song_id': song_id,
        })

        update_data(song_id, data)

    if mustCorrect or not os.path.exists(f'{BASE_PATH}/cache/covers/{song_id}.jpg') or not os.path.exists(f'{BASE_PATH}/cache/metadata/{song_id}.json'):
        thread = threading.Thread(target=download_cover, args=(data,))
        thread.start()

    if PROMETHEUS_ENABLED:
        prometheus.searched_artists.labels(artist=data['author']).inc()

    return data

@api.errorhandler(500)
def internal(error):
    return {'err': True, 'msg': random.choice([
        'riprova piu\' tardi king',
        'non c\'e cosa che odio piu\' degli errori (dopo i ceci)',
        'ipotizziamo che ocane abbia un cane...',
    ])}

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
