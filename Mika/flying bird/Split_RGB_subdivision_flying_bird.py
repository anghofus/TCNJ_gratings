import numpy as np
from PIL import Image
import os
from scipy import signal
import csv
import tkinter as tk
from tkinter import filedialog, messagebox


class PatternGeneration:
    def __init__(self):
        """
        Initialize the PatternGeneration class with default parameters,
        load the image, and start the pixel processing and CSV creation.
        """
        # Set the file path and image filename
        self.filepath_output = os.getcwd()

        self.img_paths = select_images()

        # Define dimensions for subpixels and SLM (spatial light modulator)
        self.subpixel_width = 640
        self.subpixel_height = 576

        self.slm_width = 1920
        self.slm_height = 1152
        self.slm_x = 484
        self.slm_y = 323

        # Define maximum values for RGB waveforms
        self.x_max = 20
        self.y_max = 128

        # Initialize subpixel list and main pixel grid
        self.subpixel_list = []
        self.pixel = np.zeros((self.slm_height, self.slm_width))


        # Generate and save subdivided pixel patterns for each pixel
        for i, pixel in enumerate(self.pixel_list):
            slm_image = self.subdivided_pixel(pixel)
            slm_image_filename = f"pattern_{i+1}.png"
            slm_image_filepath = os.path.join(self.filepath_output, slm_image_filename)
            slm_image.save(slm_image_filepath)
            print(f"image {i+1} of {len(self.pixel_list)} saved")

        self.added_RGB_values = self.generate_added_RGB_values()
        self.create_csv()

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

def select_images():
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilenames(title="Select exactly 6 images")

        if file_path == ():
            raise KeyboardInterrupt
        elif len(file_path) != 6:
            messagebox.showerror("Error", "Select exactly 6 images")
            continue
        else:
            break
    return file_path


if __name__ == "__main__":
    PatternGeneration()
    print("Process completed")
