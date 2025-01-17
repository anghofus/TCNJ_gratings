import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import math

fl = 1000
wl = 0.635
y_min = 65
y_peak_to_peak = 85
slm_count = 35
waveform_length = 67200
pixel_width = 3.7202380952380956e-08

def chirp_function(r, fl, wl, y_min, y_peak_to_peak):
    f = y_min + ((1 + signal.sawtooth(math.radians((2 * np.pi) / (fl * wl) * r ** 2))) / 2) * y_peak_to_peak
    return f

func = []
radius =[]

for i in range(waveform_length):
    r = i * pixel_width
    radius.append(r)
    func.append(chirp_function(r, fl, wl, y_min, y_peak_to_peak))



plt.plot(radius, func)
plt.show()