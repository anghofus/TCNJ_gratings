import matplotlib.pyplot as plt
import scipy.optimize as opt
import csv
import numpy as np


def fit_func(x, a, b, c, d):
    return a * np.sin(b * x + c) + d


y_max, depth = [], []

# Read data
with open('data') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        y_max.append(float(row[0]))
        depth.append(float(row[1]))

# Convert to numpy arrays
y_max = np.array(y_max)
depth = np.array(depth)

initial_guesses = [
    (np.max(depth) - np.min(depth)) / 2,  # Amplitude guess
    400,  # Frequency guess (period guess: 2*pi)
    0,  # Phase shift guess
    np.mean(depth)  # Vertical shift guess
]

# Fit the curve
constants = opt.curve_fit(fit_func, y_max, depth, p0=initial_guesses)
a, b, c, d = constants[0]

# Calculate the fitted values
fit = fit_func(y_max, a, b, c, d)

# Calculate the residuals
residuals = depth - fit

# Plot the data and the fit
plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
plt.plot(y_max, depth, 'b.', label='data')
plt.plot(y_max, fit, 'r-', label=f'fit: a={a:.2f}, b={b:.2f}, c={c:.2f}')
plt.xlabel("y_max value")
plt.ylabel("depth in nm")
plt.title("y_max study")
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(y_max, residuals, 'g.', label='residuals')
plt.xlabel("y_max value")
plt.ylabel("Residuals")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("y_max_study_sine_fit_improved.png")
plt.show()
