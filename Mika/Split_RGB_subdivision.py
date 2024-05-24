import numpy as np
from PIL import Image
import os
from scipy import signal
import csv


class PatternGeneration:
    def __init__(self):
        # Define the dimensions and parameters for the pixel grid and waveforms
        self.filepath = os.getcwd()
        filename_image = "test.png"

        self.subpixel_width = 576
        self.subpixel_height = 576

        self.pixel_height = 2
        self.pixel_width = 3

        self.slm_width = 1920
        self.slm_height = 1152
        self.slm = 484

        self.x_max_red = 38.91
        self.x_max_green = 32.7
        self.x_max_blue = 30
        self.y_max = 128

        # Initialize the list of subpixels and the main pixel grid
        self.subpixel_list = []
        self.pixel = np.zeros((self.slm_height, self.slm_width))

        image = Image.open(os.path.join(self.filepath, filename_image))

        if image.size > (270, 270):
            raise Exception("Image must have a resolution auf 270x270 or less")

        self.image_width, self.image_height = image.size[0] // 3, image.size[1] // 2

        self.rgb_array = image_to_rgb_array(image)
        self.pixel_list = self.rgb_array_to_pixel_list(self.rgb_array)
        self.added_RGB_values = self.generate_added_RGB_values()
        self.create_csv()

        for i, pixel in enumerate(self.pixel_list):
            slm_image = self.subdivided_pixel(pixel)
            slm_image_filename = f"pattern_{i+1}.png"
            slm_image_filepath = os.path.join(self.filepath, slm_image_filename)
            slm_image.save(slm_image_filepath)
            print(f"image {i} saved")

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
        for i, rgb in enumerate(rgb_color):
            total = int(rgb[0]) + int(rgb[1]) + int(rgb[2])
            subpixel = np.zeros((self.subpixel_width, self.subpixel_height))
            red_width = int(rgb[0]) / total * self.subpixel_width
            green_width = int(rgb[1]) / total * self.subpixel_width

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

        # Convert the pixel grid to an image
        image = Image.fromarray(self.pixel).convert("L")

        self.subpixel_list = []

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

    def rgb_array_to_pixel_list(self, rgb_array):

        pixel_list = []

        for rgb_array_y in range(0, rgb_array.shape[0] - 1, self.pixel_height):
            for rgb_array_x in range(0, rgb_array.shape[1] - 1, self.pixel_width):
                sub_pixel_color = []
                for sub_pixel_y in range(self.pixel_height):
                    for sub_pixel_x in range(self.pixel_width):
                        target_y = rgb_array_y + sub_pixel_y
                        target_x = rgb_array_x + sub_pixel_x
                        sub_pixel_color.append(rgb_array[target_y][target_x])
                pixel_list.append(sub_pixel_color)

        return pixel_list

    def generate_added_RGB_values(self):
        added_RGB_values = []
        for i, pixel in enumerate(self.pixel_list):
            added_color = []
            for subpixel in pixel:
                sum_subpixel = int(subpixel[0]) + int(subpixel[1]) + int(subpixel[2])
                added_color.append(sum_subpixel)
            average = sum(added_color) / len(added_color)
            added_RGB_values.append(average)

        return added_RGB_values

    # Function to calculate coordinates in the snake pattern

    def create_csv(self):
        # Create a new CSV file and write the added_rgb_values to it
        filename_added_RGB = "added_RGB_values.csv"
        added_RGB_values_path = os.path.join(self.filepath, filename_added_RGB)
        # added_RGB_values_path = "C:/Users/mcgeelab/Desktop/SLMImages/added_RGB_values.csv"

        with open(added_RGB_values_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["addedRGB"])  # Header row

            for value in self.added_RGB_values:
                csv_writer.writerow([value])

        # Specify the input and output file paths
        filename_dataset = "dataset.csv"
        dataset_path = os.path.join(self.filepath, filename_dataset)
        # dataset_path = 'C:/Users/mcgeelab/Desktop/SLMImages/dataset.csv'

        # Calculate new coordinates without relying on added_RGB_values.csv
        coordinates = calculate_coordinates(self.image_height, self.image_width, self.slm)

        # Create a new list to store the modified data
        modified_data = []

        # Ensure that only the second and third columns are extended with the calculated coordinates
        for i in range(len(coordinates)):
            # Include exp_times in the first column and update the second and third columns
            modified_data.append([self.added_RGB_values[i]] + [int(coord) for coord in coordinates[i]])
            # + list(coordinates[i]))

        # Open the CSV file for writing
        with open(dataset_path, 'w', newline='') as output_file:
            # Write the header row
            writer = csv.writer(output_file)
            writer.writerow(["addedRGB", "X", "Z"])
            # Write the modified data
            writer.writerows(modified_data)

        print("Both CSV-Sheets have been created")


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


def calculate_coordinates(rows, columns, slm):
    points = []
    start_x = ((columns / 2) - 1) * slm + slm / 2
    start_y = -(((rows / 2) - 1) * slm + slm / 2)

    for row in range(rows):
        for col in range(columns):
            points.append((start_x, start_y))

            # Update x-coordinate based on row parity and not at the end of the row
            if col < columns - 1:
                start_x -= slm if (row % 2 == 0) else 0
                start_x += slm if (row % 2 != 0) else 0

        # Update y-coordinate at the end of each row
        start_y += slm * (145 / 242)

    return points


if __name__ == "__main__":
    PatternGeneration()
    print("Process completed")
