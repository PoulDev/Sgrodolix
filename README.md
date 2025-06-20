# 📜 Sgrodolix
Share song lyrics easily

## What is it?
Sgrodolix is a free and open-source service that allows you to share your favorite song lyrics!

<img src="./assets/example.jpg" width="350rem">

You can access a hosted instance at https://sgrodolix.website

## Setup
> Please keep in mind that this is **NOT** a full tutorial on how to host a complete Sgrodolix instance.
> Using this repo, you can get the API running on your machine, but you'll also need the [frontend](https://github.com/loricso/sgrodolix).

Before doing anything, fill `cfg.py` with your Genius API token.

```sh
# Create a Python virtual environment
python3 -m venv .venv
```

```sh
# Enter the environment (Linux):
source .venv/bin/activate

# Windows:
.\.venv\Scripts\activate.bat
```

```sh
# Install the requirements
pip install -r requirements.txt
```

**And now you can run it 🎉**
```
python3 main.py
```

## Configuration
In `cfg.py`, you can find the default configuration for the Sgrodolix server.
Aside from the `TOKEN` variable, you can leave the default configuration, and it will work fine.

#### Analytics
If you want, you can enable analytics collection by setting `PROMETHEUS_ENABLED` to `True`. You'll also need to set `PROMETHEUS_TOKEN`.

#### Search result caching
To make Sgrodolix faster, you can enable search result caching using Redis.
- `REDIS_CACHING_ENABLED`: Enable caching by setting this variable to `True`
- `REDIS_HOST`: Redis host, if you have redis on your machine you can leave `localhost` as the value
- `REDIS_PORT`: The redis database port, change this if you don't use the default redis port
- `REDIS_PASSWORD`: Useful if your database has a password, otherwise, leave it `None`.
- `REDIS_CACHE_TIME`: Caching time, the default value is `60 * 60` (60 seconds * 60 = 1 hour).

#### Other values
- `BOTTOM_TEXT`: Change the bottom text in the shared image
- `CANVAS`: Canvas size — the lower it is, the faster the API will be, but obviously the quality will be worse.
- `NOT_FOUND_MSG`: If you want to change the "404 song not found" error message

## Special thanks to
- [Lorix ❤️](https://github.com/loricso) - he made the frontend
