```python
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 12:37:49 2024

@author: Julian Honecker

This script prepares images for an SLM (Spatial Light Modulator) by 
splitting the image into RGB channels, creating patterns based on 
sawtooth waveforms, and saving the processed patterns. 
It also generates CSV files with the added RGB values and coordinates.
"""

import numpy as np
from PIL import Image as im
from scipy import signal
import csv


class PrepSLM:
    def __init__(self):
        """
        Initialize the PrepSLM class by loading the image, splitting it into
        RGB channels, and setting up various parameters for processing.
        """
        # Load the image
        img = im.open("C:/Users/mcgeelab/Desktop/PreparedImages/DALL-E_Irises_Vincent_van_Gogh.png")
        # Split the image into red, green, and blue channels
        imgsplit = img.split()

        # Convert the image channels to numpy arrays
        self.redarray = np.asarray(imgsplit[0])
        self.greenarray = np.asarray(imgsplit[1])
        self.bluearray = np.asarray(imgsplit[2])

        # Get the dimensions of the image
        self.height, self.width = self.redarray.shape[:2]

        # Set up the SLM parameters
        self.columns = self.width
        self.rows = self.height
        self.slm = 484  # SLM pixel pitch in micrometers

        # Initialize the list to store added RGB values
        self.added_RGB_values = []

        # Set up the time array for the sawtooth waveforms
        self.t = np.linspace(0, 1920, 1920)
        # Define frequencies for the sawtooth waveforms
        self.f1 = 1 / 30  # blue
        self.f2 = 1 / 32.7  # green
        self.f3 = 1 / 38.91  # red

        # Generate the sawtooth waveforms for each color channel
        self.st = (1 + signal.sawtooth(2 * np.pi * self.f1 * self.t)) * 64
        self.st1 = (1 + signal.sawtooth(2 * np.pi * self.f2 * self.t)) * 64
        self.st2 = (1 + signal.sawtooth(2 * np.pi * self.f3 * self.t)) * 64

        # Initialize the counter for the pixel processing
        self.counter = 1

    def make_SLM_pattern(self, red, green, blue):
        """
        Create the SLM pattern based on the red, green, and blue values.

        Args:
        red (float): The red component of the pixel.
        green (float): The green component of the pixel.
        blue (float): The blue component of the pixel.

        Returns:
        Image: The generated SLM pattern as an image.
        """
        # Initialize the array for the SLM pattern
        array = np.zeros((1152, 1920))
        i = 0
        j = 0

        # Determine the regions for each color based on the pixel values
        regionblue = 1920 * blue
        regiongreen = 1920 * green
        regionred = 1920 * red

        # Fill the array with the sawtooth waveforms for the blue region
        while i < regionblue:
            array[0][i] = self.st[i]
            i += 1

        # Fill the array with the sawtooth waveforms for the green region
        while i < regionblue + regiongreen - 1:
            array[0][i] = self.st1[i]
            i += 1

        # Fill the array with the sawtooth waveforms for the red region
        while i < 1920:
            array[0][i] = self.st2[i]
            i += 1

        # Copy the first row to all other rows to create a uniform pattern
        while j < 1152:
            array[j] = array[0]
            j += 1

        # Convert the array to an image
        data = im.fromarray(array)
        image = data.convert("RGB")
        return image

    def calculate_coordinates(self, rows, columns, slm):
        """
        Calculate the coordinates in a snake pattern for the SLM.

        Args:
        rows (int): The number of rows in the image.
        columns (int): The number of columns in the image.
        slm (int): The SLM pixel pitch in micrometers.

        Returns:
        list: A list of coordinates for the snake pattern.
        """
        points = []
        # Start coordinates for the snake pattern
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
            start_y += slm

        return points

    def image_creator(self):
        """
        Create images for the SLM based on the RGB values of each pixel.
        """
        for row in range(self.height - 1, -1, -1):
            if (self.height - 1 - row) % 2 == 0:
                for col in range(self.width - 1, -1, -1):
                    red = self.redarray[row, col]
                    green = self.greenarray[row, col]
                    blue = self.bluearray[row, col]
                    total = int(red) + int(green) + int(blue)
                    self.added_RGB_values.append(total)
                    if total == 0:
                        total = 1
                    blue = blue / (total)
                    green = green / (total)
                    red = red / (total)
                    SLM = self.make_SLM_pattern(red, green, blue)
                    SLM.save(f"C:/Users/mcgeelab/Desktop/SLMImages/pattern_{self.counter}.png")
                    # Print the coordinates and RGB values
                    print(
                        f"Pixel at (Row {row}, Column {col}): (R:{round(red, 2)}, G:{round(green, 2)}, B:{round(blue, 2)}), Brightness: {round(total / 765 * 100)}%")
                    self.counter += 1
            else:
                for col in range(self.width):
                    red = self.redarray[row, col]
                    green = self.greenarray[row, col]
                    blue = self.bluearray[row, col]
                    total = int(red) + int(green) + int(blue)
                    self.added_RGB_values.append(total)
                    if total == 0:
                        total = 1
                    blue = blue / (total)
                    green = green / (total)
                    red = red / (total)
                    SLM = self.make_SLM_pattern(red, green, blue)
                    SLM.save(f"C:/Users/mcgeelab/Desktop/SLMImages/pattern_{self.counter}.png")
                    # Print the coordinates and RGB values
                    print(
                        f"Pixel at (Row {row}, Column {col}): (R:{round(red, 2)}, G:{round(green, 2)}, B:{round(blue, 2)}), Brightness: {round(total / 765 * 100)}%")
                    self.counter += 1

            if row > 0:
                row -= 1
            else:
                break
        print(f"Read pixels and total created Images: {len(self.added_RGB_values)}")

    def create_csv(self):
        """
        Create CSV files with the added RGB values and the coordinates for the SLM.
        """
        # Create a new CSV file and write the added_rgb_values to it
        added_RGB_values_path = "C:/Users/mcgeelab/Desktop/SLMImages/added_RGB_values.csv"

        with open(added_RGB_values_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["addedRGB"])  # Header row

            for value in self.added_RGB_values:
                csv_writer.writerow([value])

        # Specify the input and output file paths
        dataset_path = 'C:/Users/mcgeelab/Desktop/SLMImages/dataset.csv'

        # Calculate new coordinates without relying on added_RGB_values.csv
        coordinates = self.calculate_coordinates(self.rows, self.columns, self.slm)

        # Create a new list to store the modified data
        modified_data = []

        # Ensure that only the second and third columns are extended with the calculated coordinates
        for i in range(len(coordinates)):
            # Include exp_times in the first column and update the second and third columns
            modified_data.append([self.added_RGB_values[i]] + [int(coord) for coord in coordinates[i]])

        # Open the CSV file for writing
        with open(dataset_path, 'w', newline='') as output


_file:
# Write the header row
writer = csv.writer(output_file)
writer.writerow(["addedRGB", "X", "Z"])
# Write the modified data
writer.writerows(modified_data)

print("Both CSV-Sheets have been created")

if __name__ == "__main__":
    prep_slm = PrepSLM()
    prep_slm.image_creator()
    prep_slm.create_csv()
```