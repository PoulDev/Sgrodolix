import json
import os
import threading
import time
from io import BytesIO

import aiohttp
import lyricsgenius as lg
import redis
from flask import Blueprint, Flask, request, send_file
from flask_cors import CORS

from cfg import (BASE_PATH, HOST, NOT_FOUND_MSG, PROMETHEUS_ENABLED,
                 REDIS_CACHE_TIME, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT,
                 TOKEN)
from genius import (download_cover, get_local_cover, getHeaders,
                    load_local_song, parseAuthor, parseImg, parseLyrics,
                    parseTitle, parseTitleFromLyrics, search, update_data)
from share import getDominantColor, shareLyrics
from stats.stats import Prometheus, stats

genius = lg.Genius(TOKEN)

redis_conn: redis.StrictRedis

api = Blueprint("api", __name__, url_prefix="/api")
app = Flask(__name__)

prometheus: Prometheus | None = None
if PROMETHEUS_ENABLED:
    app.register_blueprint(stats)
    prometheus = Prometheus(app)

CORS(app)


def check_value(s: str, max_length: int = 200) -> bool:
    return (
        "/" in s
        or "%" in s
        or "\\" in s
        or "?" in s
        or "&" in s
        or len(s) > max_length
    )

def cache_query(artist, title):
    return artist.lower().replace(" ", "") + title.lower().replace(" ", "")

@api.route("/share", methods=["POST"])
async def share():
    song_id = request.args["song_id"]
    color = request.args.get("color", "")
    if check_value(song_id, 50):
        return {"err": True, "msg": "poco chill da parte tua"}, 400

    if not os.path.exists(f"{BASE_PATH}/cache/metadata/{song_id}.json"):
        return {"err": True, "msg": "Local song data not found!"}, 500

    for _ in range(10):
        if os.path.exists(f"{BASE_PATH}/cache/covers/{song_id}.jpg"):
            break
        time.sleep(1)
    else:
        return {"err": True, "msg": "Cover download failed"}, 500

    res = await load_local_song(song_id)
    im = await get_local_cover(song_id)

    if res == {} or im is None:
        return {"err": True, "msg": "No image found :("}, 500

    # Check if the color is valid ( accepted: #fff, #ffffff, #ffffffff (RGB & RGBA) )
    if len(color) not in (8, 6, 3):
        color = None
    else:
        try:
            int(color, 16)
        except:
            color = None

    if color is None:
        color = "#" + "".join(hex(c)[2:].zfill(2) for c in getDominantColor(im))
    else:
        color = "#" + color

    img_io = BytesIO()
    img = shareLyrics(
        im, res["author"], res["title"], "\n".join(request.get_json()), color
    )
    img.save(img_io, "JPEG", quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype="image/jpeg")


@api.route("/lyrics")
async def getLyrics():
    if len(request.args["t"]) > 120 or len(request.args["a"]) > 120:
        return "poco chill da parte tua"

    title = request.args["t"]
    artist = request.args["a"]

    cached_result = redis_conn.get(cache_query(artist, title))
    if not cached_result is None:
        data = json.loads(str(cached_result))
        if not prometheus is None:
            prometheus.searched_artists.labels(artist=data["author"]).inc()
        return cached_result

    search_res = await search(title, artist)

    if search_res is None:
        return NOT_FOUND_MSG

    song_id = search_res["api_path"].split("/")[2]

    data = await load_local_song(song_id)
    mustCorrect = (
        data.get("title") == "Unkown"
        or data.get("author") == "Unknown"
        or data.get("cover", {}).get("url") is None
    )

    # Update song data
    if not data or mustCorrect:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://genius.com" + search_res["path"], headers=getHeaders()
            ) as res:
                res_data = await res.text()

        lyrics = parseLyrics(res_data)
        title = parseTitle(res_data)
        if title == "Unknown":
            title = parseTitleFromLyrics(lyrics)

        data.update(
            {
                "lyrics": lyrics,
                "title": title,
                "author": parseAuthor(res_data),
                "cover": {"url": parseImg(res_data, song_id)},
                "song_id": song_id,
            }
        )

        update_data(song_id, data)

    # Update song cover
    if (
        mustCorrect
        or not os.path.exists(f"{BASE_PATH}/cache/covers/{song_id}.jpg")
        or not os.path.exists(f"{BASE_PATH}/cache/metadata/{song_id}.json")
    ):
        thread = threading.Thread(target=download_cover, args=(data,))
        thread.start()

    # Collect analytics
    if not prometheus is None:
        prometheus.searched_artists.labels(artist=data["author"]).inc()

    redis_conn.set(cache_query(artist, title), json.dumps(data), ex=REDIS_CACHE_TIME)

    return data


@api.errorhandler(500)
def internal(error):
    return {"err": True, "msg": "Buttata di fuori"}


@api.route("/")
@app.route("/")
async def home():
    return "<h1>Sgrodolix API</h1>"


app.register_blueprint(api)

if __name__ == "__main__":
    CACHE_PATH = os.path.join(BASE_PATH, "cache")
    COVERS_PATH = os.path.join(CACHE_PATH, "covers")
    DATA_PATH = os.path.join(CACHE_PATH, "metadata")
    if not os.path.exists(CACHE_PATH):
        os.mkdir(CACHE_PATH)
    if not os.path.exists(COVERS_PATH):
        os.mkdir(COVERS_PATH)
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)

    redis_conn = redis.StrictRedis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
    )

    try:
        redis_conn.ping()
    except redis.ConnectionError:
        print("Unable to connect to Redis.")
        exit(1)

    app.run(HOST[0], HOST[1], debug=False)
