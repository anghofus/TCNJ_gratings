import numpy as np
from PIL import Image
import os
from scipy import signal
import csv


class PatternGeneration:
    def __init__(self):
        """
        Initialize the PatternGeneration class with default parameters,
        load the image, and start the pixel processing and CSV creation.
        """
        # Set the file path and image filename
        self.filepath_output = os.getcwd()
        self.filepath_input = os.getcwd()
        filename_image = "test4.png"

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
        self.y_max_modifier = 80

        # Initialize subpixel list and main pixel grid
        self.subpixel_list = []
        self.pixel = np.zeros((self.slm_height, self.slm_width))

        # Load and validate the image
        image = Image.open(os.path.join(self.filepath_input, filename_image))
        if image.size > (270, 270):
            raise Exception("Image must have a resolution of 270x270 or less")

        # Set dimensions of the image in terms of subpixels
        self.image_width, self.image_height = image.size[0] // 3, image.size[1] // 2

        # Convert image to an RGB array
        self.rgb_array = image_to_rgb_array(image)
        self.pixel_list = self.rgb_array_to_pixel_list(self.rgb_array)
        self.added_RGB_values = []

        # Generate and save subdivided pixel patterns for each pixel
        for i, pixel in enumerate(self.pixel_list):
            slm_image = self.subdivided_pixel(pixel)
            slm_image_filename = f"pattern_{i+1}.png"
            slm_image_filepath = os.path.join(self.filepath_output, slm_image_filename)
            slm_image.save(slm_image_filepath)
            print(f"image {i+1} of {len(self.pixel_list)} saved")

        self.create_csv()

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

        self.added_RGB_values.append(max_value)

        # Generate subpixel patterns based on RGB percentages
        for i, rgb in enumerate(rgb_color):
            total = total_values[i]
            subpixel = np.zeros((self.subpixel_height, self.subpixel_width))

            if total != 0:
                # Calculate widths for each color band within the subpixel
                red_width = int(rgb[0]) / total * self.subpixel_width
                green_width = int(rgb[1]) / total * self.subpixel_width

                normalized_value = total / max_value
                if normalized_value == 1:
                    waveform_red = self.generate_waveform(128, 'red')
                    waveform_green = self.generate_waveform(128, 'green')
                    waveform_blue = self.generate_waveform(128, 'blue')
                else:
                    y_max = normalized_value * self.y_max_modifier
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
            (0, 0),         # for i == 0
            (640, 0),       # for i == 1
            (1280, 0),      # for i == 2
            (0, 576),       # for i == 3
            (640, 576),     # for i == 4
            (1280, 576)     # for i == 5
        ]

        # Get the starting coordinates for the subpixel
        x_coordinate, y_coordinate = coordinates[i]

        # Place the entire subpixel matrix into the main pixel grid at once
        self.pixel[y_coordinate:y_coordinate + self.subpixel_height, x_coordinate:x_coordinate + self.subpixel_width] = current_subpixel

    def rgb_array_to_pixel_list(self, rgb_array):
        """
        Convert the RGB array to a list of pixels.

        Parameters:
        rgb_array (ndarray): The RGB array of the image.

        Returns:
        list: A list of pixels.
        """
        pixel_list = []

        # Iterate over the RGB array in steps of pixel_height and pixel_width
        for i, rgb_array_y in enumerate(range(rgb_array.shape[0], 0, - self.pixel_height)):
            if i % 2 == 0:
                for rgb_array_x in range(rgb_array.shape[1] - 1, 0, -self.pixel_width):
                    sub_pixel_color = self.get_subpixel_color(rgb_array, rgb_array_x, rgb_array_y, 0)
                    pixel_list.append(sub_pixel_color)
            else:
                for rgb_array_x in range(0, rgb_array.shape[1] - 1, self.pixel_width):
                    sub_pixel_color = self.get_subpixel_color(rgb_array, rgb_array_x, rgb_array_y, 1)
                    pixel_list.append(sub_pixel_color)

        return pixel_list

    def get_subpixel_color(self, rgb_array, rgb_array_x, rgb_array_y, i):

        sub_pixel_color = []
        # Collect the colors for each subpixel
        for sub_pixel_y in range(self.pixel_height, 0, -1):
            for sub_pixel_x in range(self.pixel_width, 0, -1):
                target_y = rgb_array_y - sub_pixel_y
                if i == 1:
                    target_x = 3 + rgb_array_x - sub_pixel_x
                elif i == 0:
                    target_x = 1 + rgb_array_x - sub_pixel_x
                else:
                    raise ValueError
                sub_pixel_color.append(rgb_array[target_y][target_x])
        return sub_pixel_color

    def create_csv(self):
        """
        Create CSV files for the added RGB values and dataset with coordinates.
        """
        # Create a new CSV file and write the added RGB values to it
        filename_added_RGB = "added_RGB_values.csv"
        added_RGB_values_path = os.path.join(self.filepath_output, filename_added_RGB)

        with open(added_RGB_values_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["addedRGB"])  # Header row

            for value in self.added_RGB_values:
                csv_writer.writerow([value])

        # Specify the input and output file paths
        filename_dataset = "dataset.csv"
        dataset_path = os.path.join(self.filepath_output, filename_dataset)

        # Calculate new coordinates without relying on added_RGB_values.csv
        coordinates = calculate_coordinates(self.image_height, self.image_width, self.slm_x, self.slm_y)

        # Create a new list to store the modified data
        modified_data = []

        # Ensure that only the second and third columns are extended with the calculated coordinates
        for i in range(len(coordinates)):
            # Include exp_times in the first column and update the second and third columns
            modified_data.append([self.added_RGB_values[i]] + [int(coord) for coord in coordinates[i]])

        # Open the CSV file for writing
        with open(dataset_path, 'w', newline='') as output_file:
            # Write the header row
            writer = csv.writer(output_file)
            writer.writerow(["addedRGB", "X", "Z"])
            # Write the modified data
            writer.writerows(modified_data)

        print("Both CSV-Sheets have been created")


def image_to_rgb_array(image):
    """
    Convert an image to an RGB array.

    Parameters:
    image (PIL.Image): The input image.

    Returns:
    ndarray: An array representation of the image in RGB format.
    """
    # Split the image into its RGB components
    image_split = image.split()

    # Convert each component to a numpy array
    red_array = np.asarray(image_split[0])
    green_array = np.asarray(image_split[1])
    blue_array = np.asarray(image_split[2])

    height, width = red_array.shape[:2]

    # Initialize an empty array to hold the RGB tuples
    rgb_array = np.zeros((height, width), dtype=object)

    # Combine the RGB components into tuples
    for y in range(height):
        for x in range(width):
            rgb_array[y][x] = (red_array[y][x], green_array[y][x], blue_array[y][x])

    return rgb_array


def calculate_coordinates(rows, columns, slm_x, slm_y):
    """
    Calculate coordinates in a snake pattern.

    Parameters:
    rows (int): Number of rows.
    columns (int): Number of columns.
    slm (int): Spatial light modulator value.

    Returns:
    list: A list of coordinate tuples.
    """
    points = []
    # Initialize starting coordinates
    start_x = ((columns / 2) - 1) * slm_x + slm_x / 2
    start_y = -(((rows / 2) - 1) * slm_y + slm_y / 2)

    for row in range(rows):
        for col in range(columns):
            points.append((start_x, start_y))

            # Update x-coordinate based on row parity and not at the end of the row
            if col < columns - 1:
                start_x -= slm_x if (row % 2 == 0) else 0
                start_x += slm_x if (row % 2 != 0) else 0

        # Update y-coordinate at the end of each row
        start_y += slm_y

    return points


if __name__ == "__main__":
    PatternGeneration()
    print("Process completed")
