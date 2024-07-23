import numpy as np
import math
import scipy
import os
from PIL import Image


def calculate_angular_speed(time, grating_height, radius):
    return grating_height/(time * radius)


class SinePhasePlateGeneration:
    def __init__(self,
                 radius: float,
                 focal_length: float,
                 wavelength: float,
                 filename: str,
                 filepath: str,
                 slm_width: int,
                 y_min: int,
                 y_peak_to_peak: int):
        self.__radius = radius / 1000
        self.__diameter = radius * 2
        self.__focal_length = focal_length / 1000
        self.__wavelength = wavelength / 10 ** 9
        self.__slm_width = slm_width / 10 ** 6

        self.__filepath = filepath
        self.__filepath_image_folder = os.path.join(filepath, "images")
        self.__filename = filename

        self.__slm_px_width = 1920
        self.__slm_px_height = 1200
        self.__y_min = y_min
        self.__y_peak_to_peak = y_peak_to_peak

        self.__slm_count = int(self.__radius / self.__slm_width)
        self.__slm_count_diameter = self.__slm_count * 2
        self.__linespace_width = int(self.__slm_count * 1920)
        self.__pixel_width = self.__radius / self.__linespace_width

        self.__r_linespace = np.linspace(0, self.__linespace_width, self.__linespace_width)
        self.__waveform = []

    @property
    def wavelength(self):
        return self.__wavelength

    @property
    def y_min(self):
        return self.__y_min

    @y_min.setter
    def y_min(self, value):
        assert value > 0, "y_min must be grater than zero!"
        self.__y_min = value

    @property
    def y_peak_to_peak(self):
        return self.__y_peak_to_peak

    @y_peak_to_peak.setter
    def y_peak_to_peak(self, value):
        assert value > 0, "y_peak_to_peak must be grater than zero!"
        self.__y_peak_to_peak = value

    def generate_images(self):
        if not os.path.exists(self.__filepath_image_folder):
            os.makedirs(self.__filepath_image_folder)

        self.__generate_waveform()
        self.__generate_slm_images()

    def __generate_waveform(self):
        for i in range(self.__linespace_width):
            r = i * self.__pixel_width
            self.__waveform.append(self.__chirp_function(r))

    def __generate_slm_images(self):
        image_array = np.zeros((self.__slm_px_height, self.__slm_px_width), dtype=np.uint8)
        for i in range(self.__slm_count):
            start = self.__slm_px_width * i
            stop = start + self.__slm_px_width
            for j in range(self.__slm_px_height):
                image_array[j] = self.__waveform[start:stop]
            image = Image.fromarray(image_array)
            image.save(os.path.join(self.__filepath_image_folder, f"{self.__filename}_{i}.jpg"))

    def __chirp_function(self, r):
        f = self.__y_min + ((1 + scipy.signal.sawtooth(math.radians((2 * np.pi) / (self.__focal_length * self.__wavelength) * r ** 2))) / 2) * self.__y_peak_to_peak
        return f