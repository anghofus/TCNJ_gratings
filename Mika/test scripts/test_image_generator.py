import numpy as np
from PIL import Image

width = 270
height = 270

bar_height = height / 5

color_list = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

image_array = np.zeros((height, width), dtype=np.uint8)


def generate_color_bar(width, height, start_color, channel, ):
    array = np.zeros((height, width), dtype=np.uint8)
