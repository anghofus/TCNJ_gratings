import serial


class SerialError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.args[0]}"


class ESPController:
    """
    A Python interface for controlling the ESP302 motion controller via a serial connection.

    The `ESPController` class facilitates communication with the ESP302 controller, allowing users to send commands to control motors and perform various operations such as homing, moving axes, and error checking. The class abstracts low-level serial communication details, providing methods for sending commands, handling errors, and performing common tasks like moving axes to specific positions.

    Attributes:
    -----------
    ser : serial.Serial
        The serial connection to the ESP302 controller.

    Methods:
    --------
    start_up():
        Initializes the ESP302 controller by enabling motors and performing a homing sequence on all axes.

    close_connection():
        Closes the serial connection to the ESP302 controller and deletes the instance.

    send_command_no_error_check(command: str, xx_parameter=None, nn_parameter=None, debug=False):
        Sends a command to the ESP302 controller without performing error checks on the response.

    send_command(command: str, xx_parameter=None, nn_parameter=None, debug=False):
        Sends a command to the ESP302 controller and checks for errors.

    error_check():
        Checks for errors on the ESP302 controller and raises an exception if any are found.

    clear_error_buffer():
        Continuously checks for errors until no error is detected.

    move_axis_absolut(axis: int, position: float, speed: float):
        Moves an axis to an absolute position at a specified speed.

    move_axis_relative(axis: int, units: float, speed: float):
        Moves an axis by a relative distance at a specified speed.

    Note:
    -----
    This class assumes that the ESP302 controller is properly connected via a serial port and that the motors are configured correctly. Before using this class, ensure that the serial port is accessible and that the controller is powered on.

    The ESP302 motion controller allows for precise control of up to three axes, typically used in scientific instruments where accurate positioning is required.

    """
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
        """
           Initializes the ESP302 controller by enabling motors and performing a homing sequence.

           This function iterates through the three available axes of the ESP302 controller. For each axis, it:

           1. Sends the `MO` (Motor On) command to enable the motor.
           2. Sends the `OR` (Origin Search) command to initiate a homing sequence.

           The homing sequence aligns the axes to a known reference position, ensuring accurate positioning for subsequent operations.

           Commands Used:
           --------------
           - `MO` : Turns the motor on for the specified axis.
           - `OR` : Initiates a homing sequence for the specified axis.

           Example:
           --------
           start_up()
               Enables the motors and performs a homing sequence on all three axes.

           Note:
           -----
           Ensure that the motors are correctly configured and unobstructed before calling this function to prevent damage or misalignment.
           """

        for i in range(3):
            self.send_command("MO", i + 1)
            self.send_command("OR", i + 1)

    def close_connection(self):
        """
       Closes the serial connection to the ESP302 controller.

       This function closes the active serial connection to the ESP302 controller and deletes the instance of the class
       to free up resources.

       Example:
       --------
       close_connection()
           Closes the connection to the controller and cleans up the instance.

       Note:
       -----
       Ensure that all necessary commands have been sent and that the controller is in a safe state before closing the connection.
       """
        self.ser.close()
        del self

    def send_command_no_error_check(self, command: str, xx_parameter=None, nn_parameter=None, debug=False):
        """
        Sends a command to the ESP302 controller without performing error checks on the response.

        This function constructs and sends a command to the ESP302 controller using the specified `command`,
        optional `xx_parameter`, and `nn_parameter`. It then reads and returns the response from the controller.

        Parameters:
        -----------
        command : str
            A two-character command mnemonic that specifies the action to be performed. The length of the command
            must be between 1 and 2 characters.
        xx_parameter : int, optional
            An optional integer parameter that precedes the command mnemonic, typically used to specify an axis
            number or other identifier (default is None).
        nn_parameter : int, float, or str, optional
            An optional parameter that follows the command mnemonic, typically used to specify a value or string
            (default is None).
        debug : bool, optional
            If set to `True`, the full command that is sent to the controller will be printed to the console for
            debugging purposes (default is False).

        Returns:
        --------
        str
            The response from the controller, decoded as a string.

        Raises:
        -------
        AssertionError
            If the `command` is not 1 or 2 characters long, or if the `xx_parameter` or `nn_parameter` are of
            incorrect types.

        Example:
        --------
        response = send_command_no_error_check("MO", 1)
            Sends the "MO" (Motor On) command for axis 1 and returns the controller's response.

        Note:
        -----
        This function does not perform any error checking on the response from the controller. Use it when
        you want to send a command and handle potential errors separately.
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
        Sends a command to the ESP302 controller and checks for errors.

        This function constructs and sends a command to the ESP302 controller, waits for a response, and then checks for
        any errors reported by the controller. If no errors are detected, the function returns the response. If an error is
        detected, it raises a `SerialError` with the corresponding error message.

        Parameters:
        -----------
        command : str
            A two-character command mnemonic that specifies the action to be performed. The length of the command
            must be between 1 and 2 characters.
        xx_parameter : int, optional
            An optional integer parameter that precedes the command mnemonic, typically used to specify an axis
            number or other identifier (default is None).
        nn_parameter : int, float, or str, optional
            An optional parameter that follows the command mnemonic, typically used to specify a value or string
            (default is None).
        debug : bool, optional
            If set to `True`, the full command that is sent to the controller will be printed to the console for
            debugging purposes (default is False).

        Returns:
        --------
        str
            The response from the controller, decoded as a string, if no errors are detected.

        Raises:
        -------
        SerialError
            If the connection is lost (indicated by an empty error code) or if the controller reports any errors.

        Example:
        --------
        response = send_command("MO", 1)
            Sends the "MO" (Motor On) command for axis 1, checks for errors, and returns the controller's response.

        Note:
        -----
        This function performs error checking after sending the command by querying the controller with the `TE`
        (Tell Error) command. If an error is detected, the function retrieves the error message using the `TB`
        (Tell Buffer) command and raises a `SerialError`.
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
        """
        Checks for errors on the ESP302 controller and raises an exception if any are found.

        This function queries the ESP302 controller for the number of errors currently stored using the `TE` command.
        It handles the following cases:

        - If the connection is lost (indicated by an empty response), a `SerialError` is raised with the message
          "Connection lost!".
        - If no errors are detected (`error_count` is 0), the function returns `True`.
        - If one or more errors are present, the function retrieves each error message using the `TB` command,
          collects them, and raises a `SerialError` with the list of errors.

        Commands Used:
        --------------
        - `TE` : Retrieves the number of errors currently stored in the controller's error buffer.
        - `TB` : Retrieves the current error message from the controller.

        Raises:
        -------
        SerialError
            If the connection is lost or if one or more errors are detected.

        Returns:
        --------
        bool
            Returns `True` if no errors are detected.

        Example:
        --------
        error_check()
            Checks the controller for errors, returning `True` if none are found,
            or raising an exception if errors are detected.

        Note:
        -----
        This function ensures that any errors reported by the controller are promptly identified and handled.
        The caller should manage the `SerialError` to properly address connection issues or other errors.
        """
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
        """
        Continuously checks for errors until no error is detected.

        This function repeatedly queries the ESP302 controller for error messages
        using the `TB` command. It continues to check until the response indicates
        that there are no errors ("NO ERROR DETECTED").

        The function operates in an infinite loop, breaking out only when the
        controller reports that no errors are present.

        Commands Used:
        --------------
        - `TB` : Retrieves the current error message from the controller.

        Example:
        --------
        check_for_errors()
            Continuously checks the controller for errors until the response
            is "NO ERROR DETECTED".

        Note:
        -----
        Use this function carefully, as it will enter an infinite loop if
        the controller continuously reports errors. Ensure that the controller
        is correctly set up to avoid endless looping.

        """
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

        """
           Move a specified axis by a relative distance at a given speed.

           This function commands an axis of the ESP302 controller to move a specified
           number of units at a designated speed. It checks for errors before and after
           execution, ensures that the speed does not exceed the maximum allowed for the axis,
           and temporarily changes the speed to achieve the motion.

           Parameters:
           -----------
           axis : int
               The axis number to move (must be 1, 2, or 3).
           units : float
               The distance to move the axis in user-defined units.
           speed : float
               The speed at which to move the axis, in units/second. This value must not
               exceed the maximum speed of the axis.

           Raises:
           -------
           AssertionError
               If the axis is not between 1 and 3 or if the speed exceeds the axis's
               maximum allowable speed.

           Commands Used:
           --------------
           - `VU` : Retrieves the maximum allowable velocity for the axis.
           - `EP` : Enters the program mode.
           - `VA` : Sets the velocity for the axis.
           - `PR` : Commands the axis to move to a relative position.
           - `WS` : Waits for the axis to stop moving.
           - `QP` : Exits program mode.
           - `EX` : Executes the program.
           - `XX` : Erases the program from memory.

           Example:
           --------
           move_axis_relative(1, 10.0, 5.0)
               Moves axis 1 by 10 units at a speed of 5 units/second.

           Note:
           -----
           This function automatically handles error checking before and after execution
           to ensure safe operation. The speed is temporarily adjusted for the motion
           and restored afterward.

           """
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
