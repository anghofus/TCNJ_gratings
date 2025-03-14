import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
from scipy import ndimage, signal
import math
import os


class ImageProcessing:
    def __init__(self):

        self.filepath_output = "/home/anghofus/PycharmProjects/TCNJ_gratings/Mika/flying bird/output"

        self.subpixel_width = 640
        self.subpixel_height = 576
        self.slm_width = 1920
        self.slm_height = 1152
        self.pixel = np.zeros((self.slm_height, self.slm_width))

        self.threshold = 150
        self.x_max = [20, 20, 20, 20, 20, 20]
        self.y_max = [128, 128, 128, 128, 128, 128]
        self.angles = [0, 60, 120, 210, 270, 330]

        self.file_path = get_file_path()
        self.images = []
        self.matrix_pixel_list = []

        for path in self.file_path:
            image = Image.open(path).convert('L')
            if image.size != (90, 90):
                raise Exception("Image must have a resolution of 90x90")
            self.images.append(image)

        self.binary_pixel_list = self.generate_binary_pixel_list(self.images)

        for i, pixel in enumerate(self.binary_pixel_list):
            slm_image = self.assemble_pixel(pixel)
            slm_image_filename = f"pattern_{i+1}.png"
            slm_image_filepath = os.path.join(self.filepath_output, slm_image_filename)
            slm_image.save(slm_image_filepath)
            print(f"{i} of {len(self.binary_pixel_list)} images generated")



    def generate_binary_pixel_list(self, image_list):
        matrices =[]
        binary_pixel_list = []
        for image in image_list:
            matrix = np.asarray(image).copy()
            matrix[matrix < self.threshold] = 0
            matrix[matrix > self.threshold] = 1
            matrices.append(matrix)

        for y in range(89, -1, -1):
            for x in range(89, -1, -1):
                pixel = []
                for i in range(len(matrices)):
                    pixel.append(matrices[i][y][x])

                binary_pixel_list.append(pixel)

        return binary_pixel_list

    def assemble_pixel(self, pixel: list):
        assert len(pixel) == 6, "pixel must be of length 6"
        assert len(self.x_max) == 6, "x_max array must be of length 6"
        assert len(self.angles) == 6, "angles array must be of length 6"

        for i, binary in enumerate(pixel):
            if int(binary) == 0:
                self.matrix_pixel_list.append(np.zeros((self.subpixel_height, self.subpixel_width)))
            elif int(binary) == 1:
                self.matrix_pixel_list.append(generate_rotated_pixel(self.angles[i], self.subpixel_width, self.subpixel_height, self.x_max[i], self.y_max[i]))
            else:
                raise ValueError
            
        for i in range(len(self.matrix_pixel_list)):
            self.place_subpixel(i)

        image = Image.fromarray(self.pixel).convert("L")
        self.matrix_pixel_list = []

        return image

    def place_subpixel(self, i: int):
        """
        Place the subpixel in the correct position in the final image.

        Parameters:
        i (int): The index of the subpixel to be placed.
        """
        assert 0 <= i <= 5, "i can only be between 0 and 5"

        # Define coordinates for each subpixel placement based on index
        current_subpixel = self.matrix_pixel_list[i]

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


def get_file_path():
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

def center_crop(matrix, target_height, target_width):
    h, w = matrix.shape  # Get original height and width

    # Compute the starting row and column
    start_row = (h - target_height) // 2
    start_col = (w - target_width) // 2

    # Crop using slicing
    return matrix[start_row : start_row + target_height, start_col : start_col + target_width]

def generate_rotated_pixel(angle, width, height, x_max=20, y_max=128, phi=0):
    long_side = max(width, height)

    uncropped_width = int(long_side * 1.414213)

    pixel = np.zeros((uncropped_width, uncropped_width))

    t = np.linspace(0, uncropped_width, uncropped_width)
    omega = 2 * np.pi * 1 / x_max

    waveform = (1 + signal.sawtooth(omega * t + math.radians(phi))) * y_max / 2

    for i in range(pixel.shape[0]):
        pixel[i, :] = waveform

    pixel_rotated = ndimage.rotate(pixel, angle, reshape=True)
    pixel_cropped = center_crop(pixel_rotated,height, width)

    return pixel_cropped

ImageProcessing()