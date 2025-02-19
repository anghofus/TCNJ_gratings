import numpy as np
from scipy import signal, ndimage
import math
from PIL import Image

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

image = Image.fromarray(generate_rotated_pixel(30, 640, 576))
image.show()