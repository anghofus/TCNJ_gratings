import numpy as np
from scipy import signal, ndimage
import math
from PIL import Image

def center_crop_numpy(matrix, target_height, target_width):
    h, w = matrix.shape  # Get original height and width

    # Compute the starting row and column
    start_row = (h - target_height) // 2
    start_col = (w - target_width) // 2

    # Crop using slicing
    return matrix[start_row : start_row + target_height, start_col : start_col + target_width]


x_max = 20
y_max = 128
phi = 0


pixel = np.zeros((141, 141))

t = np.linspace(0, 141, 141)
omega = 2 * np.pi * 1 / x_max

waveform = (1 + signal.sawtooth(omega * t + math.radians(phi))) * y_max / 2

for i in range(pixel.shape[0]):
    pixel[i, :] = waveform

pixel_rotated = ndimage.rotate(pixel, 20, reshape=True)
pixel_cropped = center_crop_numpy(pixel_rotated, 100, 100)

image = Image.fromarray(pixel)
image_rotated = Image.fromarray(pixel_rotated)
image_crop = Image.fromarray(pixel_cropped)

print(image.size)
print(image_rotated.size)
print(image_crop.size)

image.show()
image_rotated.show()
image_crop.show()