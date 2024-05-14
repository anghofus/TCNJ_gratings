import numpy as np
from PIL import Image as im
import os


def hex_to_rgb(hex_color: str):
    assert len(hex_color) == 6, "Invalid hex color"
    assert all(char <= 'f' for char in hex_color if char.isalpha()), "Invalid hex color"

    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:], 16)

    rgb = (red, green, blue)
    return rgb


def subdivided_pixel(color: list):
    assert len(color) == 6, "color list must have 6 entries"
    rgb_color = []

    for i in range(len(color)):
        rgb_color.append(hex_to_rgb(color[i]))

    pixel = np.zeros((1200, 1920))
    subpixel_list = []

    for i in range(len(rgb_color)):



if "__main__" == __name__:
    colorlist = ["7F3A97", "D4E157", "4E9A06", "FFA500", "3498DB", "C71585"]
    subdivided_pixel(colorlist)
