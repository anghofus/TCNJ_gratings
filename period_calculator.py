import math

diffraction_angle = float(input("Enter diffraction angle in degrees: "))
order = int(input("Enter diffraction order (default: 1):") or 1)

# wavelength in µm
wavelength_red = 630 * 10 ** -3
wavelength_green = 530 * 10 ** -3
wavelength_blue = 488 * 10 ** -3

# period in µm
period_red = order * wavelength_red / math.sin(math.radians(diffraction_angle))
period_green = order * wavelength_green / math.sin(math.radians(diffraction_angle))
period_blue = order * wavelength_blue / math.sin(math.radians(diffraction_angle))

# period in x_max (for the old setup)
x_max_red = period_red / (1 / 15)
x_max_green = period_green / (1 / 15)
x_max_blue = period_blue / (1 / 15)

print(f"\n\t\tperiod [µm]\t\tx_max\nred:\t{period_red:.3f}\t\t\t{x_max_red:.2f}\ngreen:\t{period_green:.3f}\t\t\t{x_max_green:.2f}\nblue:\t{period_blue:.3f}\t\t\t{x_max_blue:.2f}")

