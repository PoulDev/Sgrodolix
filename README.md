# Sgrodolix
Share song lyrics easily

## What is this?
> Sgrodolix is a free and open-source service that allows you to share your favorite song lyrics!

You can access an hosted instance at https://sgrodolix.website 

## Setup
> Please keep in mind that this is **NOT** a full tutorial on how to host a complete Sgrodolix instance.
> Using this repo you can get the API running on your machine, but you'll also need the [frontend](https://github.com/loricso/sgrodolix).


Before doing anything, fill cfg.py with your genius API token.

```sh
# Create a python virtual environment
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

#### And now you can run it.
```
python3 main.py
```