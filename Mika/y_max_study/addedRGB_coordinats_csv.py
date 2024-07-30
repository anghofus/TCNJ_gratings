import csv


def calculate_coordinates(rows, columns, slm):
    """
    Calculate the coordinates in a snake pattern for the SLM.

    Args:
    rows (int): The number of rows in the image.
    columns (int): The number of columns in the image.
    slm (int): The SLM pixel pitch in micrometers.

    Returns:
    list: A list of coordinates for the snake pattern.
    """
    points = []
    # Start coordinates for the snake pattern
    start_x = ((columns / 2) - 1) * slm + slm / 2
    start_y = -(((rows / 2) - 1) * slm + slm / 2)

    for row in range(rows):
        for col in range(columns):
            points.append((start_x, start_y))

            # Update x-coordinate based on row parity and not at the end of the row
            if col < columns - 1:
                start_x -= slm if (row % 2 == 0) else 0
                start_x += slm if (row % 2 != 0) else 0

        # Update y-coordinate at the end of each row
        start_y += slm

    return points


def create_csv(added_RGB_values):
    """
    Create CSV files with the added RGB values and the coordinates for the SLM.
    """
    # Create a new CSV file and write the added_rgb_values to it
    added_RGB_values_path = "./y_max_study/added_RGB_values.csv"

    with open(added_RGB_values_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["addedRGB"])  # Header row

        for value in added_RGB_values:
            csv_writer.writerow([value])

    # Specify the input and output file paths
    dataset_path = './y_max_study/dataset.csv'

    # Calculate new coordinates without relying on added_RGB_values.csv
    coordinates = calculate_coordinates(1, 90, 484)

    # Create a new list to store the modified data
    modified_data = []

    # Ensure that only the second and third columns are extended with the calculated coordinates
    for i in range(len(coordinates)):
        # Include exp_times in the first column and update the second and third columns
        modified_data.append([added_RGB_values[i]] + [int(coord) for coord in coordinates[i]])

    # Open the CSV file for writing
    with open(dataset_path, 'w', newline='') as output_file:
        # Write the header row
        writer = csv.writer(output_file)
        writer.writerow(["addedRGB", "X", "Z"])
        # Write the modified data
        writer.writerows(modified_data)

    print("Both CSV-Sheets have been created")


added_RGB_values = []
for i in range(90):
    added_RGB_values.append(765)

create_csv(added_RGB_values)