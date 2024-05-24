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


def generate_added_RGB_values(pixel_list):
    added_RGB_values = []
    for i, pixel in enumerate(pixel_list):
        added_color = []
        for subpixel in pixel:
            sum_subpixel = int(subpixel[0]) + int(subpixel[1]) + int(subpixel[2])
            added_color.append(sum_subpixel)
        average = sum(added_color) / len(added_color)
        added_RGB_values.append(average)

    return added_RGB_values


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


if __name__ == "__main__":
    current_path = os.getcwd()
    filename = "test.png"
    image = Image.open(os.path.join(current_path, filename))

    rgb_array = image_to_rgb_array(image)
    pixel_list = rgb_array_to_pixel_list(rgb_array)

    added_RGB_values = generate_added_RGB_values(pixel_list)

    print(len(pixel_list))
    print(len(added_RGB_values))



