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
        self.filename = filename

        self.slm_px_width = 1920
        self.slm_px_height = 1152
        self.x_max = 128

        self.slm_count = int(self.radius / self.slm_width)
        self.linespace_width = int(self.slm_count * 1920)
        self.pixel_width = self.radius / self.linespace_width

        self.r_linespace = np.linspace(0, self.linespace_width, self.linespace_width)
        self.waveform = []

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        self.generate_waveform()
        self.generate_slm_images()

    def generate_waveform(self):
        for i in range(self.linespace_width):
            r = i * self.pixel_width
            self.waveform.append(self.chirp_function(r))

    def generate_slm_images(self):
        image_array = np.zeros((self.slm_px_height, self.slm_px_width))
        for i in range(self.slm_count):
            start = self.slm_px_width * i
            stop = start + self.slm_px_width
            for j in range(self.slm_px_height):
                image_array[j] = self.waveform[start:stop]
            image = Image.fromarray(image_array)
            image.save(os.path.join(self.filepath, f"{self.filename}_{i}.jpg")).convert('L')

    def chirp_function(self, r):
        f = ((1 + scipy.signal.sawtooth(math.radians((2 * np.pi) / (self.focal_length * self.wavelength) * r ** 2)))/2) * self.x_max
        return f


if __name__ == "__main__":
    filepath = os.getcwd()
    PhasePlate1D(5, 10, 633, "test", filepath)
