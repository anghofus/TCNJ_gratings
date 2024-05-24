import numpy as np
from PIL import Image
import os


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

    rgb_array = test_array(10,  10)
    print(rgb_array)

    rgb_list = rgb_array_to_pixel_list(rgb_array)
    print(rgb_list)


