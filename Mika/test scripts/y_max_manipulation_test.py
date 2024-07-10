import numpy as np
from PIL import Image
from scipy import signal


class YMaxManipulation:
    def __init__(self):
        # Define dimensions for subpixels and SLM (spatial light modulator)
        self.subpixel_width = 640
        self.subpixel_height = 576

        self.pixel_height = 2
        self.pixel_width = 3

        self.slm_width = 1920
        self.slm_height = 1152
        self.slm_x = 484
        self.slm_y = 323

        # Define maximum values for RGB waveforms
        self.x_max_red = 38.91
        self.x_max_green = 32.7
        self.x_max_blue = 30
        self.y_max = 128

        self.subpixel_list = []
        self.pixel = np.zeros((self.slm_height, self.slm_width))
    def subdivided_pixel(self, rgb_color: list):
        """
        Create subdivided pixels based on the given color list.

        Parameters:
        rgb_color (list): A list of 6 RGB colors.

        Returns:
        Image: A PIL image object representing the generated pixel image.
        """
        assert len(rgb_color) == 6, "color list must have 6 entries"

        total_values = []
        for subpixel in rgb_color:
            total_value = int(subpixel[0]) + int(subpixel[1]) + int(subpixel[2])
            total_values.append(total_value)

        max_value = max(total_values)


        # Generate subpixel patterns based on RGB percentages
        for i, rgb in enumerate(rgb_color):
            total = total_values[i]
            subpixel = np.zeros((self.subpixel_height, self.subpixel_width))

            # Calculate widths for each color band within the subpixel
            red_width = int(rgb[0]) / total * self.subpixel_width
            green_width = int(rgb[1]) / total * self.subpixel_width

            normalized_value = total / max_value
            if normalized_value == 1:
                waveform_red = self.generate_waveform(128, 'red')
                waveform_green = self.generate_waveform(128, 'green')
                waveform_blue = self.generate_waveform(128, 'blue')
            else:
                y_max = normalized_value * 80
                waveform_red = self.generate_waveform(y_max, 'red')
                waveform_green = self.generate_waveform(y_max, 'green')
                waveform_blue = self.generate_waveform(y_max, 'blue')

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

        # Place the generated subpixels into the main pixel grid
        for i in range(len(self.subpixel_list)):
            self.place_subpixel(i)

        # Convert the pixel grid to an image and return it
        image = Image.fromarray(self.pixel).convert("L")
        self.subpixel_list = []

        return image

    def generate_waveform(self, y_max: float, color: str):
        # Generate time array for the waveforms
        t = np.linspace(0, self.subpixel_width, self.subpixel_width)

        if color == "red":
            omega_red = 2 * np.pi * 1 / self.x_max_red
            waveform = (1 + signal.sawtooth(omega_red * t)) * y_max / 2
        elif color == "green":
            omega_green = 2 * np.pi * 1 / self.x_max_green
            waveform = (1 + signal.sawtooth(omega_green * t)) * y_max / 2
        elif color == "blue":
            omega_blue = 2 * np.pi * 1 / self.x_max_blue
            waveform = (1 + signal.sawtooth(omega_blue * t)) * y_max / 2
        else:
            raise ValueError("color can only be 'red', 'green' or 'blue'")

        return waveform

    def place_subpixel(self, i: int):
        """
        Place the subpixel in the correct position in the final image.

        Parameters:
        i (int): The index of the subpixel to be placed.
        """
        assert 0 <= i <= 5, "i can only be between 0 and 5"

        # Define coordinates for each subpixel placement based on index
        current_subpixel = self.subpixel_list[i]

        # Define coordinates for each subpixel placement based on index
        coordinates = [
            (0, 0),  # for i == 0
            (640, 0),  # for i == 1
            (1280, 0),  # for i == 2
            (0, 576),  # for i == 3
            (640, 576),  # for i == 4
            (1280, 576)  # for i == 5
        ]

        # Get the starting coordinates for the subpixel
        x_coordinate, y_coordinate = coordinates[i]

        # Place the entire subpixel matrix into the main pixel grid at once
        self.pixel[y_coordinate:y_coordinate + self.subpixel_height,
        x_coordinate:x_coordinate + self.subpixel_width] = current_subpixel

if __name__ == "__main__":
