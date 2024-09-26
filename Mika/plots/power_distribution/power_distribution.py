import matplotlib.pyplot as plt
import scipy.optimize as opt
import csv
import numpy as np


z, power = [], []

with open('data') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        z.append(float(row[0]))
        power.append(float(row[1]))


x_max = np.array(z)
period = np.array(power)

# Plot the data and the fit
plt.figure(figsize=(10, 3))
plt.plot(z, power, 'b.', label='data')

plt.xlabel("distance to lens [mm]")
plt.ylabel("power [µW]")
plt.title("Power distribution behind sine phase plate")
plt.grid(True)

plt.savefig("power_distribution_1.png")
plt.show()
