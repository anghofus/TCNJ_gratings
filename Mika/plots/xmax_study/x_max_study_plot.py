import matplotlib.pyplot as plt
import scipy.optimize as opt
import csv
import numpy as np


def fit_func(x, a, b):
    return a*x+b


x_max, period, depth = [], [], []

with open('data') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        x_max.append(float(row[0]))
        period.append(float(row[1]))
        depth.append(float(row[2]))

i = 0
while i < len(period):
    if period[i] > 11 or depth[i] > 200:
        x_max.pop(i)
        period.pop(i)
        depth.pop(i)
    else:
        i += 1

x_max = np.array(x_max)
period = np.array(period)

constants = opt.curve_fit(fit_func, x_max, period)
a, b = constants[0]

# Calculate the fitted values
fit = fit_func(x_max, a, b)

# Calculate the residuals
residuals = period - fit

# Plot the data and the fit
plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
plt.plot(x_max, period, 'b.', label='data')
plt.plot(x_max, fit, 'r-', label=f'fit: a={a:.2f}, b={b:.2f}')
plt.xlabel("x_max value")
plt.ylabel("period in µm")
plt.title("x_max study")
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(x_max, residuals, 'g.', label='residuals')
plt.xlabel("x_max value")
plt.ylabel("Residuals")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("x_max_study_linear_fit.png")
plt.show()
