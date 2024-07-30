import math
import numpy as np
from scipy import signal
from PIL import Image as im
import time
import os


def generate_image(x_max, y_max):
    image = np.zeros((1152, 1920), dtype=np.uint8)
    t = np.linspace(0, 1920, 1920)
    omega = 2 * np.pi * 1/x_max

    waveform = (1 + signal.sawtooth(omega * t)) * y_max / 2

    for i in range(1920):
        image[0][i] = waveform[i]

    for j in range(1152):
        image[j] = image[0]

    return image


y_max = 180

for i in range(90):
    image = generate_image(20, y_max)
    im.fromarray(image).save(f"./y_max_study/pattern_{i+1}.png")
    y_max = y_max - 2
