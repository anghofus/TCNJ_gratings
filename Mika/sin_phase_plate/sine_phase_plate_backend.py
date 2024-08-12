import numpy as np
import math
import scipy
from PIL import Image
from shutter_controller import *
from esp_controller import *
from laser_controller import *


def calculate_angular_speed(time, grating_height, radius):
    return grating_height/(time * radius)


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

        self.__slm_count = int(self.__radius / self.__grating_width)
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
        self.__generate_waveform()
        images = self.__generate_slm_images()
        return images

    def __generate_waveform(self):
        for i in range(self.__linespace_width):
            r = i * self.__pixel_width
            self.__waveform.append(self.__chirp_function(r))

    def __generate_slm_images(self):
        images = []
        image_array = np.zeros((self.__slm_px_height, self.__slm_px_width), dtype=np.uint8)
        for i in range(self.__slm_count):
            start = self.__slm_px_width * i
            stop = start + self.__slm_px_width
            for j in range(self.__slm_px_height):
                image_array[j] = self.__waveform[start:stop]
            image = Image.fromarray(image_array)
            images.append(image)
        return images

    def __chirp_function(self, r):
        f = self.__y_min + ((1 + scipy.signal.sawtooth(math.radians((2 * np.pi) / (self.__focal_length * self.__wavelength) * r ** 2))) / 2) * self.__y_peak_to_peak
        return f


class InstrumentController:
    def __init__(self, port_laser, port_esp, port_shutter):
        self.laser = LaserController(port_laser)
        self.esp = ESPController(port_esp)
        self.shutter = ShutterController(port_shutter)

        if not self.laser.connection_check():
            raise Exception('Laser not connected')
        if not self.esp.connection_check():
            raise Exception('ESP not connected')
        if not self.shutter.connection_check():
            raise Exception('Shutter not connected')


