import math
import numpy as np
from scipy import signal
from PIL import Image as im
import time
import os


def generate_image(x_max, y_max, phi):
    assert 0 <= x_max <= 1920, "x_max must be between 0 and 1920"
    assert 0 <= y_max <= 128, "y_max must be between 0 and 128"
    assert 0 <= phi <= 360, "phi must be between 0 and 360"

    image = np.uint8(np.zeros((1152, 1920)))
    t = np.linspace(0, 1920, 1920)
    omega = 2 * np.pi * 1/x_max

    waveform = (1 + signal.sawtooth(omega * t + math.radians(phi))) * y_max / 2

    for i in range(1920):
        image[0][i] = waveform[i]

    for j in range(1152):
        image[j] = image[0]

    return image


if __name__ == '__main__':
    default_flag = int(input("Use default parameters? (yes:1, no:0): "))

    if default_flag == 1:
        x_max = 30
        y_max = 128
        shift = True
    if default_flag == 0:
        x_max = int(input("Enter x_max:"))
        y_max = int(input("Enter y_max:"))
        shift = int(input("generate shift image?:"))

    save_or_show = int(input("save (0) or show (1)?:"))

    path = os.getcwd()
    if shift == 1:
        image = im.fromarray(generate_image(x_max=x_max, y_max=y_max, phi=0))
        image_shifted = im.fromarray(generate_image(x_max=x_max, y_max=y_max, phi=180))
        if save_or_show == 1:
            image.show()
            image_shifted.show()
        if save_or_show == 0:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image.save(f"{timestamp}.jpg")
            image_shifted.save(f"{path}/{timestamp}_shifted.jpg")

    if shift == 0:
        image = im.fromarray(generate_image(x_max=x_max, y_max=y_max, phi=0))
        if save_or_show == 1:
            image.show()
        if save_or_show == 0:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image.save(f"{path}/{timestamp}.jpg")
