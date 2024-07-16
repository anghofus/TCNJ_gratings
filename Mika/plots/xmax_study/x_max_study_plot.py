import matplotlib.pyplot as plt
import scipy.optimize as opt
import csv


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

constants = opt.curve_fit(fit_func, x_max, period)
a, b = constants[0]

fit = []
for i in x_max:
    fit.append(fit_func(i, a, b))


plt.figure(figsize=(6, 4))
plt.plot(x_max, fit, label=f'fit (y={a:2f}*x{b:2f})')
plt.xlabel("x_max value")
plt.ylabel("period in µm")
plt.title("x_max study")
plt.grid(linestyle='--')
plt.plot(x_max, period, '.', label='data')

plt.legend()

plt.savefig("x_max_study.png")
