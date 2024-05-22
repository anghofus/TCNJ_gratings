from PIL import Image
import numpy as np

red = 255
green = 0
blue = 0

height = 10
width = 10

image_array = np.zeros((height, width, 3), dtype=np.uint8)

for y in range(height):
    for x in range(width):
        image_array[x][y][0] = red
        image_array[x][y][1] = green
        image_array[x][y][2] = blue

image = Image.fromarray(image_array, "RGB")
image.save('test.png')
