import numpy as np
from PIL import Image
import os
from scipy import signal


class PatternGeneration:
    def __init__(self):
        filepath = os.getcwd()
        filename = "test.png"
        image = Image.open(os.path.join(filepath, filename))

        if image.size > (270, 270):
            raise Exception("Image must have a resolution auf 270x270 or less")

        rgb_array = image_to_rgb_array(image)
        subpixel_list = rgb_array_to_pixel_list(rgb_array)

        # Define the dimensions and parameters for the pixel grid and waveforms
        self.subpixel_width = 576
        self.subpixel_height = 576
        self.slm_width = 1920
        self.slm_height = 1152
        self.x_max_red = 38.91
        self.x_max_green = 32.7
        self.x_max_blue = 30
        self.y_max = 128

        # Initialize the list of subpixels and the main pixel grid
        self.subpixel_list = []
        self.pixel = np.zeros((self.slm_height, self.slm_width))

    # Generate subdivided pixel patterns based on input colors
    def subdivided_pixel(self, rgb_color: list):

        """
        Create subdivided pixels based on the given color list.

        Parameters:
        color (list): A list of 6 rgb colors.

        Returns:
        Image: A PIL image object representing the generated pixel image.
        """

        assert len(rgb_color) == 6, "color list must have 6 entries"

        # Generate time array for the waveforms
        t = np.linspace(0, self.subpixel_width, self.subpixel_width)

        # Define the angular frequencies for the waveforms
        omega_red = 2 * np.pi * 1 / self.x_max_red
        omega_green = 2 * np.pi * 1 / self.x_max_green
        omega_blue = 2 * np.pi * 1 / self.x_max_blue

        # Generate the waveforms for each color channel
        waveform_red = (1 + signal.sawtooth(omega_red * t)) * self.y_max / 2
        waveform_green = (1 + signal.sawtooth(omega_green * t)) * self.y_max / 2
        waveform_blue = (1 + signal.sawtooth(omega_blue * t)) * self.y_max / 2

        # Generate subpixel patterns based on RGB percentages
        for i in range(len(rgb_color)):
            rgb = rgb_color[i]
            subpixel = np.zeros((self.subpixel_width, self.subpixel_height))
            red_width = rgb[0] * self.subpixel_width
            green_width = rgb[1] * self.subpixel_width

            j = 0
            k = 0
            # Assign waveform values to subpixel based on RGB widths
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
            print(f"Subpixel {i} finished")

        # Place the generated subpixels into the main pixel grid
        for i in range(len(self.subpixel_list)):
            self.place_subpixel(i)

        # Convert the pixel grid to an image
        image = Image.fromarray(self.pixel).convert("L")

        return image

    # Place subpixel patterns into the main pixel grid
    def place_subpixel(self, i: int):

        """
        Place the subpixel in the correct position in the final image.

        Parameters:
        i (int): The index of the subpixel to be placed.
        """

        assert 0 <= i <= 5, "i can only be between 0 and 5"

        current_subpixel = self.subpixel_list[i]

        # Define coordinates for each subpixel placement
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

        # Place the current subpixel into the main pixel grid
        for y in range(self.subpixel_height):
            for x in range(self.subpixel_width):
                target_x = x_coordinate + x
                target_y = y_coordinate + y
                self.pixel[target_y][target_x] = current_subpixel[y][x]


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

def rgb_array_to_pixel_list(rgb_array):

    sub_pixel_height = 2
    sub_pixel_width = 3
    pixel_list = []

    for rgb_array_y in range(0, rgb_array.shape[0]-1, 2):
        for rgb_array_x in range(0, rgb_array.shape[1]-1, 3):
            sub_pixel_color = []
            for sub_pixel_y in range(sub_pixel_height):
                for sub_pixel_x in range(sub_pixel_width):
                    target_y = rgb_array_y + sub_pixel_y
                    target_x = rgb_array_x + sub_pixel_x
                    sub_pixel_color.append(rgb_array[target_y][target_x])
            pixel_list.append(sub_pixel_color)

    return pixel_list


if __name__ == "__main__":
    pass
