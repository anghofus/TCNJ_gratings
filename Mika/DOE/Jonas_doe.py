import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import csv


class JonasDOE:
    def __init__(self):
        self.side_length = 10

        self.output_path = os.path.join(os.getcwd(), "patterns")
        self.image = Image.open(get_file_path())
        self.slm_x = 484
        self.slm_y = 290

        self.added_RGB_values =[]

        for i in range(self.side_length*self.side_length):
            self.image.save(os.path.join(self.output_path, f"pattern_{i+1}.png"))
            self.added_RGB_values.append(765)

        self.create_csv()

    def create_csv(self):
        """
        Create CSV files for the added RGB values and dataset with coordinates.
        """
        # Create a new CSV file and write the added RGB values to it
        filename_added_RGB = "added_RGB_values.csv"
        added_RGB_values_path = os.path.join(self.output_path, filename_added_RGB)

        with open(added_RGB_values_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["addedRGB"])  # Header row

            for value in self.added_RGB_values:
                csv_writer.writerow([value])

        # Specify the input and output file paths
        filename_dataset = "dataset.csv"
        dataset_path = os.path.join(self.output_path, filename_dataset)

        # Calculate new coordinates without relying on added_RGB_values.csv
        coordinates = calculate_coordinates(self.side_length, self.side_length, self.slm_x, self.slm_y)

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
    return file_path[0]

JonasDOE()