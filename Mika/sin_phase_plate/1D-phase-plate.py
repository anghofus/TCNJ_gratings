import numpy as np
import math
import scipy
import os
from PIL import Image


class PhasePlate1D:
    def __init__(self, radius: float, focal_length: float, wavelength: float, filename: str, filepath: str, slm_width=200):
        self.radius = radius / 1000
        self.focal_length = focal_length / 1000
        self.wavelength = wavelength / 10**9
        self.slm_width = slm_width / 10**6

        self.filepath = filepath
        self.filepath_image_folder = os.path.join(filepath, "images")
        self.filename = filename

        self.slm_px_width = 1920
        self.slm_px_height = 1152
        self.y_min = 0
        self.y_peak_to_peak = 128

        self.slm_count = int(self.radius / self.slm_width)
        self.linespace_width = int(self.slm_count * 1920)
        self.pixel_width = self.radius / self.linespace_width

        self.r_linespace = np.linspace(0, self.linespace_width, self.linespace_width)
        self.waveform = []

        if os.path.exists(self.filepath_image_folder):
            i = 1
            self.filepath_image_folder = os.path.join(self.filepath, f"images{i}")
            while os.path.exists(os.path.join(self.filepath, f"images{i}")):
                i += 1
                self.filepath_image_folder = os.path.join(self.filepath, f"images{i}")
            os.makedirs(self.filepath_image_folder)
        else:
            os.makedirs(self.filepath_image_folder)

        self.generate_waveform()
        self.generate_slm_images()

    def generate_waveform(self):
        for i in range(self.linespace_width):
            r = i * self.pixel_width
            self.waveform.append(self.chirp_function(r))

    def generate_slm_images(self):
        image_array = np.zeros((self.slm_px_height, self.slm_px_width), dtype=np.uint8)
        for i in range(self.slm_count):
            start = self.slm_px_width * i
            stop = start + self.slm_px_width
            for j in range(self.slm_px_height):
                image_array[j] = self.waveform[start:stop]
            image = Image.fromarray(image_array)
            image.save(os.path.join(self.filepath_image_folder, f"{self.filename}_{i}.jpg"))

    def chirp_function(self, r):
        f = self.y_min + ((1 + scipy.signal.sawtooth(math.radians((2 * np.pi) / (self.focal_length * self.wavelength) * r ** 2))) / 2) * self.y_peak_to_peak
        return f


if __name__ == "__main__":
    cwd_flag = int(input("Use current working directory? (0: No, 1: Yes):"))
    if cwd_flag == 0:
        ui_file_path = input("Enter filepath:")
    if cwd_flag == 1:
        ui_file_path = os.getcwd()
    else:
        ui_file_path = os.getcwd()

    ui_filename = input("Enter filename:")
    ui_radius = float(input("radius in mm:"))
    ui_focal_length = float(input("focal length in mm:"))
    ui_wavelength = float(input("wavelength in nm:"))

    PhasePlate1D(ui_radius, ui_focal_length, ui_wavelength, ui_filename, ui_file_path)
