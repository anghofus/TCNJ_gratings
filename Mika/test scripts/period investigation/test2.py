import numpy as np
import matplotlib.pyplot as plt
import scipy
import math
from PIL import Image
import csv

class SinePhasePlateGeneration:
    def __init__(self,
                 radius: float,
                 focal_length: float,
                 wavelength: float,
                 grating_width: int,
                 y_min: int,
                 y_peak_to_peak: int):

        self.__radius = radius / 1000
        self.__focal_length = focal_length / 1000
        self.__wavelength = wavelength / 10 ** 9
        self.__grating_width = grating_width / 10 ** 6

        self.__slm_px_width = 1920
        self.__slm_px_height = 1200
        self.__y_min = y_min
        self.__y_peak_to_peak = y_peak_to_peak

        self.slm_count = int(self.__radius / self.__grating_width)
        self.__waveform_length = int(self.slm_count * 1920)
        self.pixel_width = self.__radius / self.__waveform_length

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
        self.generate_waveform()
        images = self.__generate_slm_images()
        return images

    def generate_waveform(self):

        for i in range(self.__waveform_length):
            r = i * self.pixel_width
            self.__waveform.append(self.__chirp_function(r))

        return self.__waveform


    def __generate_slm_images(self):
        images = []
        for i in range(self.slm_count):
            image_array = np.zeros((self.__slm_px_height, self.__slm_px_width), dtype=np.uint8)
            start = self.__slm_px_width * i
            stop = start + self.__slm_px_width
            for j in range(self.__slm_px_height):
                image_array[j] = self.__waveform[start:stop]
            image = Image.fromarray(image_array)
            images.append(image)

        return images

    def __chirp_function(self, r):
        x = np.pi / (self.__focal_length * self.__wavelength) * r ** 2
        f = self.__y_min + ((1 + scipy.signal.sawtooth(x)) / 2) * self.__y_peak_to_peak
        return f

def find_period(numbers):
    n = len(numbers)

    # Find the first, second, and third local minima
    local_minima_indices = []
    for i in range(1, n - 1):
        if numbers[i] < numbers[i - 1] and numbers[i] < numbers[i + 1]:
            local_minima_indices.append(i)
            if len(local_minima_indices) == 3:
                break

    # Ensure we have at least three local minima
    if len(local_minima_indices) >= 3:
        second_local_minimum_index = local_minima_indices[1]
        third_local_minimum_index = local_minima_indices[2]
        distance = third_local_minimum_index - second_local_minimum_index
        return distance
    else:
        return None  # Return None if fewer than three minima are found


foo = SinePhasePlateGeneration(2.5, 30, 633, 70, 65, 85)

waveform = foo.generate_waveform()

csv_content = []

for i in range(foo.slm_count):
    start = 1920 * i
    stop = start + 1920

    waveform_analyze = waveform[start:stop]

    distance = find_period(waveform_analyze)
    period = None
    radius = i * 70
    if distance is not None:
        period = distance * foo.pixel_width
        row = [radius, period]
    else:
        row = [radius, "NaN"]

    print(f"{radius}: distance: {distance}, period: {period}")

    csv_content.append(row)

with open("period_test.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(csv_content)

plt.plot(waveform[-1920:])
plt.show()

images = foo.generate_images()
for i, image in enumerate(images):
    image.save(f"z_image{i}.png")
