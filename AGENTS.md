# AGENTS.md

## Project Overview
Sgrodolix — Flask API that fetches song lyrics via Genius, renders them as shareable images, and serves a separate quote-image endpoint. Frontend lives in a separate repo ([loricso/sgrodolix](https://github.com/loricso/sgrodolix)).

## Setup & Run
```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 main.py          # Flask dev server on 0.0.0.0:2000
```

## Configuration (cfg.py)
- **TOKEN** — Genius API token (required, must be set before running).
- **HOST** — bind address, default `('0.0.0.0', 2000)`.
- **REDIS_*** — optional Redis caching (disabled by default). Redis must be running or startup fails with `exit(1)`.
- **PROMETHEUS_*** — optional Prometheus metrics.
- **BASE_PATH** — where `cache/` is written (default `.`).
- **CANVAS** — image resolution `(864, 1536)`. Higher = slower.
- `cfg.py` is **gitignored** — each developer maintains their own copy.

## Architecture
```
main.py              — Flask app entry, registers Blueprint "api" at /api
genius/              — Genius API integration
  scrape.py          — HTTP scraping / HTML parsing (lyrics, title, author, cover URL)
  cover.py           — cover image download & local cache
  song.py            — load_local_song(), search(), update_data()
share/               — image generation (Pillow)
  share.py           — shareLyrics() — renders lyric images
  quote.py           — shareQuote() — renders quote images
  extract.py         — dominant color extraction
stats/stats.py       — Prometheus metrics Blueprint at /api/metrics
cache/               — runtime artifact (gitignored)
  covers/            — downloaded cover images
  metadata/          — per-song JSON (title, author, lyrics, cover URL, song_id)
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/lyrics?t=<title>&a=<artist>` | Search Genius, return JSON |
| POST | `/api/share?song_id=<id>` | Generate lyric image (body = JSON array of lyric lines) |
| POST | `/api/quote` | Generate quote image (body = `{quote, author, title}`) |
| GET | `/api/metrics` | Prometheus metrics (Bearer token auth) |
| GET | `/` | Simple HTML home page |

## Key Behaviors
- **Redis cache** — `main.py` creates `redis_conn` at import time. If `REDIS_CACHING_ENABLED=True` and Redis is unreachable, the process **exits immediately**.
- **Cover download** — happens asynchronously in a `threading.Thread`. The `/share` endpoint polls for up to 10 seconds waiting for the cover file.
- **Input validation** — `check_value()` rejects paths containing `/`, `%`, `\`, `?`, `&` in song_id.
- **Error handler** — 500 handler returns `{"err": true, "msg": "Buttata di fuori"}`.

## Testing
No formal test framework. `test.py` is a manual scratch script (partially commented out). Run it directly with `python3 test.py` after setting up the venv.

## Conventions
- Python 3.13+ (pycache dirs show `cpython-313`/`cpython-314`).
- No linter, formatter, or type checker configured.
- `pyproject.toml` is empty — requirements pinned in `requirements.txt`.
- `__init__.py` files use `from .module import *` — wildcard re-exports.
