from PIL import Image, ImageDraw
from mandelbrot import mandelbrot, MAX_ITER
from collections import defaultdict
from math import floor, ceil

def linear_interpolation(color1, color2, t):
    return color1 * (1 - t) + color2 * t

# Image size (pixels)
WIDTH = 270
HEIGHT = 180

# Initial plot window (highly zoomed-in section)
zoom = 0.006276
RE_START = -0.748
RE_END = RE_START + zoom
IM_START = 0.11669
IM_END = IM_START + zoom

def create_image(re_start, re_end, im_start, im_end):
    histogram = [0] * MAX_ITER
    values = [[0] * HEIGHT for _ in range(WIDTH)]
    total = 0

    for x in range(WIDTH):
        for y in range(HEIGHT):
            # Convert pixel coordinate to complex number
            c = complex(re_start + (x / WIDTH) * (re_end - re_start),
                        im_start + (y / HEIGHT) * (im_end - im_start))
            # Compute the number of iterations
            m = mandelbrot(c)

            values[x][y] = m
            if m < MAX_ITER:
                histogram[floor(m)] += 1
                total += 1

    if total == 0:
        return False

    hues = [0] * (MAX_ITER + 1)
    h = 0
    for i in range(MAX_ITER):
        h += histogram[i] / total
        hues[i] = h
    hues[MAX_ITER] = h

    im = Image.new('HSV', (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(im)

    for x in range(WIDTH):
        for y in range(HEIGHT):
            m = values[x][y]
            # The color depends on the number of iterations
            hue = 255 - int(255 * linear_interpolation(hues[floor(m)], hues[ceil(m)], m % 1))
            saturation = 255
            value = 255 if m < MAX_ITER else 0
            # Plot the point
            draw.point([x, y], (hue, saturation, value))

    im.convert('RGB').save('mandelbrot_zoom_270x180.png', 'PNG')
    return True

# Try to create an image, adjusting parameters if necessary
step = 0.00000001
max_attempts = 1000
attempts = 0

while not create_image(RE_START, RE_END, IM_START, IM_END) and attempts < max_attempts:
    RE_START += step
    RE_END += step
    IM_START += step
    IM_END += step
    attempts += 1
    print(f"{attempts} of {max_attempts}")

if attempts >= max_attempts:
    print("Failed to create an image after multiple attempts.")
else:
    print(f"Image created successfully after {attempts} attempts.")