from PIL import Image
import numpy as np

red = 255
green = 255
blue = 0

height = 2
width = 3

image_array = np.zeros((height, width, 3), dtype=np.uint8)
print(image_array.shape)

for y in range(height):
    for x in range(width):
        image_array[y][x][0] = red
        image_array[y][x][1] = green
        image_array[y][x][2] = blue

image = Image.fromarray(image_array, "RGB")
image.save('test.png')
