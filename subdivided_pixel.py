import numpy as np
from scipy import signal


class Parameter:
    def __init__(self):
        self.width = 576
        self.height = 576
        self.x_max_red = 38.91
        self.x_max_green = 32.7
        self.x_max_blue = 30
        self.y_max = 128


parameter = Parameter()


def hex_to_rgb_percentage(hex_color: str):
    assert len(hex_color) == 6, "Invalid hex color"
    assert all(char <= 'f' for char in hex_color if char.isalpha()), "Invalid hex color"

    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:], 16)
    total = red + green + blue

    rgb_percentage = (red/total, green/total, blue/total)
    print("Color converted")
    return rgb_percentage


def subdivided_pixel(color: list):
    assert len(color) == 6, "color list must have 6 entries"

    rgb_color = []
    subpixel_list = []
    pixel = np.zeros((1200, 1920))

    t = np.linspace(0, 1920, 1920)
    omega_red = 2 * np.pi * 1 / parameter.x_max_red
    omega_green = 2 * np.pi * 1 / parameter.x_max_green
    omega_blue = 2 * np.pi * 1 / parameter.x_max_blue
    waveform_red = (1 + signal.sawtooth(omega_red * t)) * parameter.y_max / 2
    waveform_green = (1 + signal.sawtooth(omega_green * t)) * parameter.y_max / 2
    waveform_blue = (1 + signal.sawtooth(omega_blue * t)) * parameter.y_max / 2

    for i in range(len(color)):
        rgb_color.append(hex_to_rgb_percentage(color[i]))
        print("Color appended")

    for i in range(len(rgb_color)):
        print(f"Subpixel {i} started")
        rgb = rgb_color[i]
        subpixel = np.zeros((parameter.width, parameter.height))
        red_width = rgb[0] * parameter.width
        green_width = rgb[1] * parameter.width
        blue_width = rgb[2] * parameter.width

        j = 0
        k = 0
        while j < red_width:
            print("red")
            subpixel[0][j] = waveform_red[j]
            j += 1
        while j < red_width + green_width - 1:
            print("green")
            subpixel[0][j] = waveform_green[j]
            j += 1
        while j < 1920:
            print("blue")
            subpixel[0][j] = waveform_blue[j]
            j += 1
        while k < 1200:
            subpixel[k] = subpixel[0]

        subpixel_list.append(subpixel)
        # print(subpixel_list)
        print(f"Subpixel {i} finished")


if "__main__" == __name__:
    colorlist = ["7F3A97", "D4E157", "4E9A06", "FFA500", "3498DB", "C71585"]
    subdivided_pixel(colorlist)
