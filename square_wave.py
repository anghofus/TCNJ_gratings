import numpy as np
from PIL import Image


y_max = 64
y_min = 0

array = np.uint8(np.zeros((1152, 1920)))

for i in range(1920):
    if i % 2 == 0:
        array[0][i] = y_max
    else:
        array[0][i] = y_min

for j in range(1152):
    array[j] = array[0]

image = Image.fromarray(array)
image.show()
