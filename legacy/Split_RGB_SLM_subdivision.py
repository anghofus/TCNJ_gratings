# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 12:37:49 2024

@author: Julian Honecker
"""
import numpy as np
from PIL import Image as im
from scipy import signal 
import csv
import os


class PrepSLM:
    def __init__(self):

        filepath = os.getcwd()
        filename = "../test.png"
        img = im.open(os.path.join(filepath, filename))
        imgsplit = img.split()
        
        self.redarray = np.asarray(imgsplit[0])
        self.greenarray = np.asarray(imgsplit[1])
        self.bluearray = np.asarray(imgsplit[2])
        
        self.height, self.width = img.size
        
        self.columns = self.width
        self.rows = self.height
        self.slm = 484
        
        self.added_RGB_values = []
        
        self.t = np.linspace(0, 1920, 1920)
    
        self.f1 = 1 / 30  # blue
        self.f2 = 1 / 32.7  # green
        self.f3 = 1 / 38.91  # red
        # f1=1/15#blue
        # f2=1/16.35#green
        # f3=1/19.455#red
    
        self.st = (1 + signal.sawtooth(2 * np.pi * self.f1 * self.t)) * 64
        self.st1 = (1 + signal.sawtooth(2 * np.pi * self.f2 * self.t)) * 64
        self.st2 = (1 + signal.sawtooth(2 * np.pi * self.f3 * self.t)) * 64
        
        # We start at Pixel 1
        self.counter = 1
    
    def make_SLM_pattern(self, red,green,blue):
        array= np.zeros((1152,1920))
        i=0
        j=0
        regionblue=1920*blue
        regiongreen=1920*green
        regionred=1920*red
        while i<regionblue:
            array[0][i]=(self.st[i])
            i=i+1
    
        while i<regionblue+regiongreen-1:
            array[0][i]=(self.st1[i])
            i=i+1
    
        while i<1920:
            array[0][i]=(self.st2[i])
            i=i+1
    
        while j<1152:
            array[j]=array[0]
            j=j+1
        
        
        data=im.fromarray(array)
        image=data.convert("RGB")
        return image
    
    
    # Function to calculate coordinates in the snake pattern
    def calculate_coordinates(self, rows, columns, slm):
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
            start_y += slm
    
        return points
    
    def image_creator(self):
        
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
                    # Process the pixel values as needed
                    # For example, print the coordinates and RGB values
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
                    # Process the pixel values as needed
                    # For example, print the coordinates and RGB values
                    print(
                        f"Pixel at (Row {row}, Column {col}): (R:{round(red, 2)}, G:{round(green, 2)}, B:{round(blue, 2)}), Brightness: {round(total / 765 * 100)}%")
                    self.counter += 1
    
            if row > 0:
                row -= 1
            else:
                break
        print(f"Read pixels and total created Images: {len(self.added_RGB_values)}")
    
    
    def create_csv(self):
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


if __name__ == "__main__":
    prep_slm = PrepSLM()
    P=    prep_slm.image_creator()
    prep_slm.create_csv()

