import numpy as np
from PIL import Image
import os

filename = "color_chart.jpg"
filepath = os.path.join(os.getcwd(), filename)

linespace = np.linspace(1, 0, 270)

colors = [
    (255, 255, 255),  # color1: White
    (255, 0, 0),      # color2: Red
    (0, 255, 0),      # color3: Green
    (0, 0, 255),      # color4: Blue
    (0, 255, 255),    # color5: Cyan
    (255, 0, 255),    # color6: Magenta
    (255, 255, 0)     # color7: Yellow
]

height = int(270/len(colors))


def generate_color_array(color_tuple, linespace, height):
    image_array = np.zeros((height, len(linespace), 3), dtype=np.uint8)

    red_line = linespace * color_tuple[0]
    green_line = linespace * color_tuple[1]
    blue_line = linespace * color_tuple[2]

    image_array[:, :, 0] = red_line
    image_array[:, :, 1] = green_line
    image_array[:, :, 2] = blue_line

    return image_array


def generate_images(colors):
    color_arrays = []

    for color in colors:
        color_array = generate_color_array(color, linespace, height)
        color_arrays.append(color_array)

    image_array = np.vstack(color_arrays)
    image = Image.fromarray(image_array)
    image.save(filepath)


generate_images(colors)
