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
            timeout=0.5
        )

    def start_up(self):
        for i in range(3):
            self.send_command("MO", i + 1)
            self.send_command("OR", i + 1)

    def close_connection(self):
        self.ser.close()
        del self

    def send_command_no_error_check(self, command: str, xx_parameter=None, nn_parameter=None, debug=False):
        """
        Sends a command to the serial device with optional parameters and returns the response.

        Args:
            command (str): A string command that must be 2 or fewer characters long.
            xx_parameter (int, optional): An integer to prepend to the command. Defaults to an empty string if not provided.
            nn_parameter (int or float, optional): An integer or float to append to the command. Defaults to an empty string if not provided.
            debug (bool, optional): A flag to activate the debug mode. If activated prints the command.

        Returns:
            str: The response from the serial device as a string.

        Raises:
            AssertionError: If the length of the command is not between 1 and 2 characters.
            AssertionError: If xx_parameter is not None or an integer.
            AssertionError: If nn_parameter is not None, an integer, or a float.
        """
        assert 0 < len(command) <= 2, "command must be 2 or fewer characters"
        assert xx_parameter is None or isinstance(xx_parameter, int), "xx_parameter must be an integer"
        assert nn_parameter is None or isinstance(nn_parameter, (int, float, str)), "nn_parameter must be an integer, float or str"

        xx_str = str(xx_parameter) if xx_parameter is not None else ''
        nn_str = str(nn_parameter) if nn_parameter is not None else ''

        full_command = f"{xx_str}{command}{nn_str}\r".encode()
        if debug:
            print(full_command)
        self.ser.write(full_command)

        response = self.ser.read_until(b'\r\r\n').decode()
        return response

    def send_command(self, command: str, xx_parameter=None, nn_parameter=None, debug=False):
        """
            Sends a command to the serial device with optional parameters and checks for errors.

            Args:
                command (str): A string command that must be 2 or fewer characters long.
                xx_parameter (int, optional): An integer to prepend to the command. Defaults to an empty string if not provided.
                nn_parameter (int or float, optional): An integer or float to append to the command. Defaults to an empty string if not provided.
                debug (bool, optional): A flag to activate the debug mode. If activated prints the command.

            Returns:
                str: The response from the serial device as a string.

            Raises:
                AssertionError: If the length of the command is not between 1 and 2 characters.
                AssertionError: If xx_parameter is not None or an integer.
                AssertionError: If nn_parameter is not None, an integer, or a float.
                SerialError: If the device returns an error code.

            This method first sends the command to the serial device without performing any error checking. It then checks the device for any error codes by sending the "TB" command. If no errors are detected (error code 0), it returns the response from the device. If an error is detected, it raises a SerialError with the error message.
            """

        response = self.send_command_no_error_check(command, xx_parameter, nn_parameter, debug)

        error_code = self.send_command_no_error_check("TE", None, 1)

        if error_code == '':
            raise SerialError("Connection lost!")
        elif int(error_code) == 0:
            return response
        else:
            error_buffer = self.send_command_no_error_check("TB")
            raise SerialError(f"{error_buffer}")

    def error_check(self):

        error_count = self.send_command_no_error_check("TE", None, 2)

        if error_count == '':
            raise SerialError("Connection lost!")
        elif int(error_count) == 0:
            return True
        else:
            errors = []
            for i in range(int(error_count)):
                error = self.send_command_no_error_check("TB")
                errors.append(error)
            raise SerialError(errors)

    def clear_error_buffer(self):
        while True:
            error_message = self.send_command_no_error_check("TB")
            if "NO ERROR DETECTED" in error_message.strip():
                break

    def move_axis_absolut(self, axis, position, speed):
        """
        Move an axis to an absolute position at a specified speed.

        Parameters:
        axis (int): The axis to move, must be between 1 and 3 inclusive.
        position (float): The target position for the axis. Must be between 0 and the maximum position for the axis.
                         For axis 1 and 2, the maximum position is 25. For axis 3, the maximum position is 360.
        speed (float): The speed at which to move the axis. Must not exceed the maximum speed returned by the "VU" command for the specified axis.

        Raises:
        AssertionError: If the axis is not in the range 1 to 3.
        AssertionError: If the position is outside the valid range for the specified axis.
        AssertionError: If the speed exceeds the maximum speed for the specified axis.

        Description:
        This method moves the specified axis to the given absolute position at the specified speed. It first clears the error buffer and validates the
        input parameters. It then retrieves the maximum speed for the axis and verifies that the given speed does not exceed this limit.
        The method proceeds to enter program mode, change the speed to the specified value, move the axis to the desired position, wait for the
        motion to complete, and restore the original speed. Finally, it exits program mode and checks for any errors.

        Commands Used:
        - EP: Enter program mode.
        - VA: Set velocity.
        - PA: Move to absolute position.
        - WS: Wait for motion stop.
        - QP: Quit program mode.
        - EX: Execute program.
        - XX: Erase program.
        """

        self.clear_error_buffer()
        assert 0 < axis <= 3, "axis must be between 1 and 3"
        if 0 <= axis <= 2:
            max_position = 25
        else:
            max_position = 360
        assert 0 <= position <= max_position, f"position must be between 0 and {max_position}"
        max_speed = self.send_command("VU", axis, "?")
        assert speed <= float(max_speed), f"speed can't be higher than {max_speed}"

        self.send_command_no_error_check("EP", 1)
        current_speed = self.send_command_no_error_check("VA", axis, "?")
        self.send_command_no_error_check("VA", axis, speed)
        self.send_command_no_error_check("PA", axis, position)
        self.send_command_no_error_check("WS", axis)
        self.send_command_no_error_check("VA", axis, current_speed)
        self.send_command_no_error_check("QP", 1)
        self.send_command_no_error_check("EX", 1)
        self.send_command_no_error_check("XX", 1)
        self.error_check()

    def move_axis_relative(self, axis, units, speed):
        self.clear_error_buffer()
        assert 0 < axis <= 3, "axis must be between 1 and 3"
        max_speed = self.send_command("VU", axis, "?")
        assert speed <= float(max_speed), f"speed can't be higher than {max_speed}"

        self.send_command_no_error_check("EP", 1)
        current_speed = self.send_command_no_error_check("VA", axis, "?")
        self.send_command_no_error_check("VA", axis, speed)
        self.send_command_no_error_check("PR", axis, units)
        self.send_command_no_error_check("WS", axis)
        self.send_command_no_error_check("VA", axis, current_speed)
        self.send_command_no_error_check("QP", 1)
        self.send_command_no_error_check("EX", 1)
        self.send_command_no_error_check("XX", 1)
        self.error_check()
