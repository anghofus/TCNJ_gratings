import numpy as np


class Test:
    def __init__(self):
        self.pixel_height = 2
        self.pixel_width = 3

    def rgb_array_to_pixel_list(self, rgb_array):
        """
        Convert the RGB array to a list of pixels.

        Parameters:
        rgb_array (ndarray): The RGB array of the image.

        Returns:
        list: A list of pixels.
        """
        pixel_list = []

        # Iterate over the RGB array in steps of pixel_height and pixel_width
        for i, rgb_array_y in enumerate(range(rgb_array.shape[0], 0, - self.pixel_height)):
            if i % 2 == 0:
                for rgb_array_x in range(rgb_array.shape[1] - 1, 0, -self.pixel_width):
                    sub_pixel_color = self.get_subpixel_color(rgb_array, rgb_array_x, rgb_array_y)
                    pixel_list.append(sub_pixel_color)
            else:
                for rgb_array_x in range(0, rgb_array.shape[1] - 1, self.pixel_width):
                    sub_pixel_color = self.get_subpixel_color(rgb_array, rgb_array_x, rgb_array_y)
                    pixel_list.append(sub_pixel_color)

        return pixel_list

    def get_subpixel_color(self, rgb_array, rgb_array_x, rgb_array_y):
        sub_pixel_color = []
        # Collect the colors for each subpixel
        for sub_pixel_y in range(self.pixel_height, 0, -1):
            for sub_pixel_x in range(self.pixel_width, 0, -1):
                target_y = rgb_array_y - sub_pixel_y
                target_x = rgb_array_x - sub_pixel_x
                sub_pixel_color.append(rgb_array[target_y][target_x])
        return sub_pixel_color


if __name__ == '__main__':
    test = Test()

    rgb_array = np.zeros((10, 10))
    i = 0
    for y in range(10):
        for x in range(10):
            rgb_array[y][x] = i
            i += 1
    print(rgb_array)

    pixel_list = test.rgb_array_to_pixel_list(rgb_array)

    print(pixel_list)