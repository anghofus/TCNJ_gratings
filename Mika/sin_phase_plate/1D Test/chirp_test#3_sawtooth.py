import numpy as np
import math
import scipy
import matplotlib.pyplot as plt

radius = 5 * 10 ** -3  # in m
focal_length = 10 * 10 ** -3  # in m
wavelength = 633 * 10 ** -9  # in m
slm_width = 200 * 10 ** -6  # in m

x_peak_to_peak = 128
x_min = 20

slm_count = int(radius / slm_width)
linespace_width = int(slm_count * 1920)
pixel_width = radius / linespace_width

r_linespace = np.linspace(0, linespace_width, linespace_width)
waveform = []


def transmission_function(r):
    f = x_min + (1+scipy.signal.sawtooth(math.radians((2*np.pi)/(focal_length*wavelength)*r**2)))/2 * x_max
    return f


for i in range(linespace_width):
    r = i * pixel_width
    # print(f"Index: {i}, r: {r}, transmission function: {transmission_function(r)}")
    waveform.append(transmission_function(r))

plt.plot(r_linespace, waveform)
plt.show()
