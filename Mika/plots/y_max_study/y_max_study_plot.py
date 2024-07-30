import matplotlib.pyplot as plt
import scipy.optimize as opt
import csv


def fit_func(x, a, b, c):
    return a*x**2+b*x+c


y_max, depth = [], []

with open('data') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        y_max.append(float(row[0]))
        depth.append(float(row[1]))


constants = opt.curve_fit(fit_func, y_max, depth)
a, b, c = constants[0]

fit = []
for i in y_max:
    fit.append(fit_func(i, a, b, c))


plt.figure(figsize=(6, 4))
plt.plot(y_max, fit, label=f'fit: y=({a:.2f})*x^2+({b:.2f})*x+({c:.2f})')
plt.xlabel("y_max value")
plt.ylabel("depth in nm")
plt.title("y_max study")
plt.grid(linestyle='--')
plt.plot(y_max, depth, '.', label='data')

plt.legend()

plt.savefig("x_max_study.png")