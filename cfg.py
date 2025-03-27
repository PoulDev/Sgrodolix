### Hosting Options

# IMPORTANT: GENIUS API TOKEN.
TOKEN = 'CHANGE ME'

# PROMETHEUS STATS
PROMETHEUS_ENABLED = False
PROMETHEUS_TOKEN = "CHANGE-ME"

# The server will save song covers & data here
BASE_PATH = '.' 

# Hosting binding address
HOST = ('0.0.0.0', 2000)

# The text displayed at the bottom of the image can be an empty string, 
# a message of your choice, or your domain name, as I have done.
BOTTOM_TEXT = 'www.sgrodolix.website'

# The generated image canvas size: please note that larger sizes will make the
# generation algorithm more resource-intensive and consume more internet bandwidth.
# I suggest to use a 9:16 resolution. Just grab one resolution from this list
# https://pacoup.com/2011/06/12/list-of-true-169-resolutions/ 
# and invert the width with the height.
CANVAS = (864, 1536)

# Song not found error message: you can leave this at it is.
NOT_FOUND_MSG = {
    'lyrics': [],
    'title': 'Not Found',
    'author': 'D:'
}
