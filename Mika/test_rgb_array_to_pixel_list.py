import numpy as np
from PIL import Image
import os


def image_to_rgb_array(image):
    image_split = image.split()

    red_array = np.asarray(image_split[0])
    green_array = np.asarray(image_split[1])
    blue_array = np.asarray(image_split[2])

    height, width = red_array.shape[:2]

    rgb_array = np.zeros((height, width), dtype=object)

    for y in range(height):
        for x in range(width):
            rgb_array[y][x] = (red_array[y][x], green_array[y][x], blue_array[y][x])

    return rgb_array


def rgb_array_to_pixel_list(rgb_array):

    sub_pixel_height = 2
    sub_pixel_width = 3
    pixel_list = []

    for rgb_array_y in range(0, rgb_array.shape[0]-1, 2):
        for rgb_array_x in range(0, rgb_array.shape[1]-1, 3):
            sub_pixel_color = []
            for sub_pixel_y in range(sub_pixel_height):
                for sub_pixel_x in range(sub_pixel_width):
                    target_y = rgb_array_y + sub_pixel_y
                    target_x = rgb_array_x + sub_pixel_x
                    print(target_x, target_y)

                    sub_pixel_color.append(rgb_array[target_y][target_x])
            pixel_list.append(sub_pixel_color)

    return pixel_list


def test_array(height, width):

    array = np.zeros((height, width))
    k = 1

    for i in range(height):
        for j in range(width):
            array[i][j] = k
            k += 1
    return array


if __name__ == "__main__":
    # current_path = os.getcwd()
 #   filename = "test.png"
  #  image = Image.open(os.path.join(current_path, filename))
#
    rgb_array = test_array(9,  9)
    print(rgb_array)

    rgb_list = rgb_array_to_pixel_list(rgb_array)
    print(rgb_list)


