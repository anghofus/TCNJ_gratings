import numpy as np
from scipy import signal
from PIL import Image
import os
import time


def hex_to_rgb_percentage(hex_color: str):
    assert len(hex_color) == 6, "Invalid hex color"
    assert all(char <= 'f' for char in hex_color if char.isalpha()), "Invalid hex color"

    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:], 16)
    total = red + green + blue

    rgb_percentage = (red/total, green/total, blue/total)
    return rgb_percentage


class PixelGeneration:
    def __init__(self):
        self.subpixel_width = 576
        self.subpixel_height = 576
        self.slm_width = 1920
        self.slm_height = 1152
        self.x_max_red = 38.91
        self.x_max_green = 32.7
        self.x_max_blue = 30
        self.y_max = 128

        self.subpixel_list = []
        self.pixel = np.zeros((self.slm_height, self.slm_width))

    def subdivided_pixel(self, color: list):
        assert len(color) == 6, "color list must have 6 entries"

        rgb_color = []
        t = np.linspace(0, self.subpixel_width, self.subpixel_width)
        omega_red = 2 * np.pi * 1 / self.x_max_red
        omega_green = 2 * np.pi * 1 / self.x_max_green
        omega_blue = 2 * np.pi * 1 / self.x_max_blue
        waveform_red = (1 + signal.sawtooth(omega_red * t)) * self.y_max / 2
        waveform_green = (1 + signal.sawtooth(omega_green * t)) * self.y_max / 2
        waveform_blue = (1 + signal.sawtooth(omega_blue * t)) * self.y_max / 2

        for i in range(len(color)):
            rgb_color.append(hex_to_rgb_percentage(color[i]))

        for i in range(len(rgb_color)):
            rgb = rgb_color[i]
            subpixel = np.zeros((self.subpixel_width, self.subpixel_height))
            red_width = rgb[0] * self.subpixel_width
            green_width = rgb[1] * self.subpixel_width

            j = 0
            k = 0
            while j < red_width:
                subpixel[0][j] = waveform_red[j]
                j += 1
            while j < red_width + green_width - 1:
                subpixel[0][j] = waveform_green[j]
                j += 1
            while j < self.subpixel_width:
                subpixel[0][j] = waveform_blue[j]
                j += 1
            while k < self.subpixel_height:
                subpixel[k] = subpixel[0]
                k += 1

            self.subpixel_list.append(subpixel)
            # print(subpixel_list)
            print(f"Subpixel {i} finished")

        for i in range(len(self.subpixel_list)):
            self.place_subpixel(i)

        image = Image.fromarray(self.pixel).convert("L")

        return image

    def place_subpixel(self, i: int):
        assert 0 <= i <= 5, "i can only be between 0 and 5"

        current_subpixel = self.subpixel_list[i]

        coordinates = [
            (32, 0),  # for i == 0
            (672, 0),  # for i == 1
            (1312, 0),  # for i == 2
            (32, 576),  # for i == 3
            (672, 576),  # for i == 4
            (1312, 576)  # for i == 5
        ]

        # Get the starting coordinates
        x_coordinate, y_coordinate = coordinates[i]

        for y in range(self.subpixel_height):
            for x in range(self.subpixel_width):
                target_x = x_coordinate + x
                target_y = y_coordinate + y
                self.pixel[target_y][target_x] = current_subpixel[y][x]


if __name__ == "__main__":

    color_list = ["7F3A97", "D4E157", "4E9A06", "FFA500", "3498DB", "C71585"]

    pixel = PixelGeneration()
    image = pixel.subdivided_pixel(color_list)

    save_or_show = int(input("Do you want to save (0) or show (1) the image?"))
    if save_or_show == 0:
        directory = os.getcwd()
        timestamp = {time.strftime("%Y%m%d-%H%M%S")}
        filename = f"{timestamp}.png"
        filepath = os.path.join(directory, filename)
        image.save(filepath)
    elif save_or_show == 1:
        image.show()
