import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import numpy as np


class DoeGeneration:
    def __init__(self):
        self.doe_height = 2 #max 18
        self.doe_width = 2 #max 18

        self.height = self.doe_height//0.1 * 1152
        self.width = self.doe_width//0.2 * 1920
        self.slm_x = 484
        self.slm_y = 290

        self.filepath_image = get_file_path()
        self.filepath_output = os.path.join(os.getcwd(), "output")
        self.image = Image.open(self.filepath_image)
        self.added_RGB_values = []


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


def gs(image, max_iter=1000):
    image_array = np.array(image)
    height, width = image_array.shape
    far_field_phase = np.zeros((height, width))
    far_field = image_array * np.exp(1j * far_field_phase)

    for i in range(max_iter):
        near_field = np.fft.ifft2(far_field)
        near_field_phase = np.angle(near_field)
        new_near_field = np.ones((height, width)) * np.exp(1j * near_field_phase)
        far_field = np.fft.fft2(new_near_field)
        far_field_phase = np.angle(far_field)
        far_field = image_array * np.exp(1j * far_field_phase)

        print(f"Iteration {i}")

    phase = np.angle(new_near_field)
    phase_normalized_scaled = (((phase + np.pi) / (2 * np.pi)) * 255).astype(np.uint8)

    return Image.fromarray(phase_normalized_scaled)

def get_file_path():
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilenames(title="Select exactly 1 images")

        if file_path == ():
            raise KeyboardInterrupt
        elif len(file_path) != 1:
            messagebox.showerror("Error", "Select exactly 1 images")
            continue
        else:
            break
    return str(file_path)

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