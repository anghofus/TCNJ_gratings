import scipy
import numpy as np
import math
import matplotlib.pyplot as plt

radius = 5 # in mm
focal_length = 10 # in mm
wavelength = 633 * 10 ** -9 # in m

viewing_distance = 1920

theta_max = np.arcsin(radius / math.sqrt(radius ** 2 + focal_length ** 2))

max_frequency = 2 * math.pi * np.sin(math.radians(theta_max)) / wavelength

linespace_length = int(radius / 0.2 * 1920)

r = np.linspace(0, linespace_length, linespace_length)
linespace_pixel = np.linspace(0, viewing_distance, viewing_distance)

print(2*np.pi /max_frequency)

waveform = (1 + scipy.signal.chirp(r, f0=1, f1=max_frequency, t1=linespace_length, method='logarithmic')) / 2
slm_pixel_1 = waveform[0:viewing_distance]

plt.plot(linespace_pixel, slm_pixel_1)
plt.show()


