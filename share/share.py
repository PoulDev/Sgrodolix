import textwrap

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageFilter

from cfg import BOTTOM_TEXT, CANVAS

COVER_OFFSET = 50
TEXT_OFFSET = 50
BOTTOM_MARGIN = 75

F_TITLE_SIZE = 25
F_AUTHOR_SIZE = 20
F_LYRICS_SIZE = 45

TRIGGER = 170

LINE_SPACING = int(F_LYRICS_SIZE * 1.25)
VERSE_SPACING = 30

Ftitle = ImageFont.truetype('./fonts/Poppins-SemiBold.ttf', F_TITLE_SIZE)
Fauthor = ImageFont.truetype('./fonts/Poppins-SemiBold.ttf', F_AUTHOR_SIZE)
Flyrics = ImageFont.truetype('./fonts/Poppins-SemiBold.ttf', F_LYRICS_SIZE)

def center(rect, canvas):
    return (canvas[0]/2-rect[0]/2, canvas[1]/2-rect[1]/2)

def getLyricsImg(lyrics, color, text_color):
    original = Image.new('RGB', CANVAS, color=color)
    draw = ImageDraw.Draw(original)
    offset = 0

    maxw = 0

    for i, line in enumerate(lyrics.splitlines()):
        for line in textwrap.wrap(line, width=20):
            w = Flyrics.getbbox(line)[2]
            if w > maxw:
                maxw = w

            draw.text(
                (0, (offset)), 
                line,
                fill=text_color, font=Flyrics
            )
            offset += LINE_SPACING
        offset += VERSE_SPACING

    original = original.crop((0, 0, int(maxw), offset))
    return original
    

def isDark(color):
    R, G, B = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    luminance = 0.2126 * R + 0.7152 * G + 0.0722 * B
    return luminance <= TRIGGER


def shareLyrics(cover: Image, artist: str, title: str, lyrics: str, color):
    print(color)
    text_color = '#030303' if not isDark(color) else '#EAEAEA'
    subtitle_color = '#1D1D1D' if not isDark(color) else '#AAAAAA'
    if len(title) > 28:
        title = title[:25] + '...'
    if len(artist) > 33:
        artist = artist[:30] + '...'
    original = Image.new('RGB', CANVAS, color=color)

    lyricsImage = getLyricsImg(lyrics, color, text_color)
    #lyricsImage.show()
    size = (625, 53 + 128 + TEXT_OFFSET + lyricsImage.size[1] + BOTTOM_MARGIN)
    pos = center(size, CANVAS)

    # blur
    blurred = Image.new('RGB', original.size, color=color)
    draw = ImageDraw.Draw(blurred)
    draw.rounded_rectangle([pos, (pos[0]+size[0], pos[1]+size[1])], fill='#0A0A0A',
                           width=3, radius=15)
    
    blurred = blurred.filter(ImageFilter.GaussianBlur(30))
    original.paste(blurred)

    # rectangle
    draw = ImageDraw.Draw(original)
    draw.rounded_rectangle([pos, (pos[0]+size[0], pos[1]+size[1])], fill=color,
                        width=3, radius=15)

    
    # Cover, Title & Author
    cover = cover.resize((128, 128))
    original.paste(cover, (int(pos[0])+COVER_OFFSET, int(pos[1])+COVER_OFFSET))
    draw.text((pos[0]+COVER_OFFSET+128+37, pos[1]+COVER_OFFSET+30), title, text_color, Ftitle)
    draw.text((pos[0]+COVER_OFFSET+128+37, pos[1]+COVER_OFFSET+30+F_TITLE_SIZE+12), artist, subtitle_color, Fauthor)
    draw.text((pos[0]+COVER_OFFSET, pos[1]+size[1]-F_TITLE_SIZE-40), BOTTOM_TEXT, subtitle_color, Ftitle)

    # Lyrics
    original.paste(lyricsImage, (int(pos[0])+COVER_OFFSET, int(pos[1])+53+128+TEXT_OFFSET))


    #margin = offset = pos[0]+COVER_OFFSET
    #for line in textwrap.wrap(lyrics, width=size[0]):
    #    draw.text((margin, offset), line, font=Flyrics, fill="#aa0000")
    #    offset += Flyrics.getbbox(line)[0]
    original = original.convert('RGB')
    return original
