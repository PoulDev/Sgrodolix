import os
import json
import logging

from cfg import BASE_PATH

async def load_local_song(song_id: str) -> dict:
    if os.path.exists(f'{BASE_PATH}/cache/metadata/{song_id}.json'):
        logging.info('Metadata found locally!')
        with open(f'{BASE_PATH}/cache/metadata/{song_id}.json', 'r') as f:
            data = json.loads(f.read())
    else:
        return {}
    return data
