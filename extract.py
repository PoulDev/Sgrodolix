from PIL import Image
import sys


NUM_CLUSTERS = 5

def getAllDominantColors(pil_img, palette_size=16, num_colors=10):
    img = pil_img.copy()
    img.thumbnail((100, 100))

    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)

    dominant_colors = []
    for i in range(num_colors):
        palette_index = color_counts[i][1]
        dominant_colors.append(palette[palette_index*3:palette_index*3+3])

    return dominant_colors

def getDominantColor(img):
    return getAllDominantColors(img)[0]

if __name__ == '__main__':
    r = getAllDominantColors(Image.open(sys.argv[1]))
    print(r)
