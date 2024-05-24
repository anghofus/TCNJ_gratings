import numpy as np
from PIL import Image
import os


def image_to_rgb_array(image):
    image_split = image.split()

    red_array = np.asarray(image_split[0])
    green_array = np.asarray(image_split[1])
    blue_array = np.asarray(image_split[2])

    height, width = red_array.shape[:2]

    rgb_array = np.zeros((height, width), dtype=object)

    for y in range(height):
        for x in range(width):
            rgb_array[y][x] = (red_array[y][x], green_array[y][x], blue_array[y][x])

    return rgb_array


if __name__ == "__main__":
    current_path = os.getcwd()
    filename = "../test.png"
    image = Image.open(os.path.join(current_path, filename))

    rgb_array = image_to_rgb_array(image)
