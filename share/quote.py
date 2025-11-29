import textwrap
import requests
import io

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

from wikipedia.search import get_author_image

TEXT_COLOR = '#202020'
CANVAS = (864, 1536)
MIN_FONT_SIZE = 15

FTitleSize = 32*2
FAuthorSize = 20*2
FQuoteSignSize = 40*2

Ftitle = ImageFont.truetype('./fonts/AveriaSerifLibre-Bold.ttf', FTitleSize)
Fauthor = ImageFont.truetype('./fonts/AveriaSerifLibre-Regular.ttf', FAuthorSize)
FQuoteSign = ImageFont.truetype('./fonts/AveriaSerifLibre-BoldItalic.ttf', FQuoteSignSize)

def center(rect, canvas):
    return (canvas[0]/2-rect[0]/2, canvas[1]/2-rect[1]/2)

def round_corners(img, radius):
    w, h = img.size
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle(
        [(0, 0), (w, h)],
        radius=radius,
        fill=255
    )

    rounded = img.copy()
    rounded.putalpha(mask)
    return rounded

def cover_resize(img, target_width, target_height):
    src_width, src_height = img.size

    ratio_w = target_width / src_width
    ratio_h = target_height / src_height

    scale = max(ratio_w, ratio_h)

    new_size = (int(src_width * scale), int(src_height * scale))
    img_resized = img.resize(new_size, Image.LANCZOS)


    left = (new_size[0] - target_width) // 2
    top = 0 #(new_size[1] - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return img_resized.crop((left, top, right, bottom))

def shareQuote(quote: str, author: str, title: str, top_margin = 80, fixed = False) -> Image.Image:
    original = Image.open('./assets/texture.png')
    draw = ImageDraw.Draw(original)
    offset = 0

    maxw = 0
    fontSize = -4/113 * len(quote) + 3620/113
    fontSize = int(fontSize)

    #if fontSize < 4:
    #    raise ValueError('Quote too long!')

    if fontSize < MIN_FONT_SIZE:
        fontSize = MIN_FONT_SIZE

    FQuote = ImageFont.truetype('./fonts/AveriaSerifLibre-Regular.ttf', fontSize*2)

    SPACING = int(fontSize * 2.5)

    lines = []

    maxLineLength = 344 * 2 / FQuote.getbbox('a')[2]
    maxTitleLength = 390 * 2 / Ftitle.getbbox('a')[2]

    for i, line in enumerate(quote.splitlines()):
        for line in textwrap.wrap(line, width=int(maxLineLength)):
            w = FQuote.getbbox(line)[2]
            if w > maxw:
                maxw = w

            lines.append((offset, line))
            offset += SPACING

    left_margin = 40*2
    if not fixed:
        top_margin = (CANVAS[1] - offset) / 2 + top_margin

    for line in lines:
        draw.text(
            (left_margin, top_margin + line[0]), 
            line[1],
            fill=TEXT_COLOR, font=FQuote
        )

    draw.text(
        (left_margin, top_margin - FQuoteSignSize),
        '“',
        fill=TEXT_COLOR, font=FQuoteSign
    )


    draw.text(
        (left_margin, top_margin + offset + FQuoteSignSize * 0.1),
        '”',
        fill=TEXT_COLOR, font=FQuoteSign
    )

    titleLines = textwrap.wrap(title, width=int(maxTitleLength))
    for i, line in enumerate(titleLines):
        draw.text(
            (left_margin, top_margin - FTitleSize - FQuoteSignSize - 24 - (len(titleLines)-i-1) * FTitleSize),
            line,
            fill=TEXT_COLOR, font=Ftitle
        )
    
    if author:
        width = Fauthor.getbbox('~ ' + author)[2]
        draw.text(
            (left_margin + 336*2 - width, top_margin + offset + FQuoteSignSize),
            '~ ' + author,
            fill=TEXT_COLOR, font=Fauthor
        )

    jpg = Image.new("RGB", original.size, (255, 255, 255))
    jpg.paste(original, mask=original.split()[3])

    return jpg

def shareQuoteWithImage(quote: str, author: str, title: str):
    author_image_url = get_author_image(author)
    if author_image_url is None:
        return shareQuote(quote, author, title)

    original = shareQuote(quote, author, title, 800, True)

    target_size = (336*2, 221*2)

    author_image = Image.open(io.BytesIO(requests.get(author_image_url, headers={'User-Agent': 'Sgrodolibrix'}).content))



    author_image = author_image.resize((1024, 1024))
    author_image.thumbnail((390, 256), Image.LANCZOS)

    original.paste(
        round_corners(cover_resize(author_image, *target_size), 42),
        (48*2, 30*2)
    )

    return original

if __name__ == '__main__':
    img = shareQuoteWithImage('''\
Vediamo già a questo punto, che all'essenza delle cose non si potrà mai pervenire dal di fuori: per quanto s'indaghi, non si trova mai altro che immagini e nomi. Si fa come qualcuno, che giri attorno ad un castello, cercando invano l'ingresso, e ne schizzi frattanto le facciate.\
''', 'Arthur Schopenhauer', 'Il mondo come volontà e rappresentazione')
    img.show()
