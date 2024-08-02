import serial


class SerialError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.args[0]}"


class ESPController:
    def __init__(self, port: str):
        self.ser = serial.Serial(
            port=port,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts=True,
            timeout=5
        )

    def __send_command_no_error_check(self, command: str, xx_parameter=None, nn_parameter=None):
        """
        Sends a command to the serial device with optional parameters and returns the response.

        Args:
            command (str): A string command that must be 2 or fewer characters long.
            xx_parameter (int, optional): An integer to prepend to the command. Defaults to an empty string if not provided.
            nn_parameter (int or float, optional): An integer or float to append to the command. Defaults to an empty string if not provided.

        Returns:
            str: The response from the serial device as a string.

        Raises:
            AssertionError: If the length of the command is not between 1 and 2 characters.
            AssertionError: If xx_parameter is not None or an integer.
            AssertionError: If nn_parameter is not None, an integer, or a float.
        """
        assert 0 < len(command) <= 2, "command must be 2 or fewer characters"
        assert xx_parameter is None or isinstance(xx_parameter, int), "xx_parameter must be an integer"
        assert nn_parameter is None or isinstance(nn_parameter, (int, float)), "nn_parameter must be an integer or float"

        xx_str = str(xx_parameter) if xx_parameter is not None else ''
        nn_str = str(nn_parameter) if nn_parameter is not None else ''

        full_command = f"{xx_str}{command}{nn_str}\r".encode()
        self.ser.write(full_command)

        response = self.ser.read_until(b'\r').decode()
        return response

    def send_command(self, command: str, xx_parameter=None, nn_parameter=None):
        """
            Sends a command to the serial device with optional parameters and checks for errors.

            Args:
                command (str): A string command that must be 2 or fewer characters long.
                xx_parameter (int, optional): An integer to prepend to the command. Defaults to an empty string if not provided.
                nn_parameter (int or float, optional): An integer or float to append to the command. Defaults to an empty string if not provided.

            Returns:
                str: The response from the serial device as a string.

            Raises:
                AssertionError: If the length of the command is not between 1 and 2 characters.
                AssertionError: If xx_parameter is not None or an integer.
                AssertionError: If nn_parameter is not None, an integer, or a float.
                SerialError: If the device returns an error code.

            This method first sends the command to the serial device without performing any error checking. It then checks the device for any error codes by sending the "TB" command. If no errors are detected (error code 0), it returns the response from the device. If an error is detected, it raises a SerialError with the error message.
            """

        response = self.__send_command_no_error_check(command, xx_parameter, nn_parameter)

        error_buffer = self.__send_command_no_error_check("TB")

        if int(error_buffer[0]) == 0:
            return response
        else:
            raise SerialError(f"{error_buffer}")
