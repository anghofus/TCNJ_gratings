import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import math


def chirp_function(r):
    f = 65 + ((1 + signal.sawtooth((180/np.pi)/((2 * np.pi) / (1*10**-3 * 633*10**-9) * r ** 2))) / 2) * 85
    return f

t = np.linspace(0, 1920, 1920)
plt.plot(t, chirp_function(t))
plt.show()