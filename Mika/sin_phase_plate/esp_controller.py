import serial
import time


class SerialError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.args[0]}"


class ESPController:
    """
    A controller class for interfacing with the Newport ESP302 motion controller via a serial connection.

    The ESPController class provides methods to initialize the connection, send commands, check for errors,
    and control the motion of the connected stages. The controller operates through an RS-232 serial interface,
    allowing for control of up to three axes. The class includes methods to move axes, perform homing sequences,
    check motion status, and handle errors.

    Attributes:
    -----------
    ser : serial.Serial
        The serial connection object used for communication with the ESP302 controller.

    Methods:
    --------
    connection_check() -> bool:
        Verifies if the controller is properly connected by sending a test command.

    start_up():
        Enables the motors and performs a homing sequence on all connected axes.

    close_connection():
        Closes the serial connection to the controller and cleans up the instance.

    send_command_no_error_check(command: str, xx_parameter=None, nn_parameter=None, debug=False) -> str:
        Sends a command to the controller without checking for errors and returns the response.

    send_command(command: str, xx_parameter=None, nn_parameter=None, debug=False) -> str:
        Sends a command to the controller and checks for errors before returning the response.

    error_check() -> bool:
        Checks for errors reported by the controller and raises an exception if any are found.

    clear_error_buffer():
        Continuously checks and clears the controller's error buffer until no errors are detected.

    get_motion_status() -> list[int]:
        Retrieves the motion status of all axes, indicating whether each axis is currently in motion.

    move_axis_absolut(axis: int, position: float, speed=1):
        Moves the specified axis to an absolute position at a given speed.

    move_axis_relative(axis: int, units: float, speed=1):
        Moves the specified axis by a relative distance at a given speed.

    move_to_coordinates(x_coordinate: float, y_coordinate: float, phi_coordinate=None, speed=1):
        Moves the system to specified X, Y, and optional Phi coordinates at a given speed.

    wait_for_movement() -> bool:
        Waits until all axes have completed their movements and are stationary.
    """
    def __init__(self, port: str):
        self.__ser = serial.Serial(
            port=port,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts=True,
            timeout=0.5
        )

        print(f"ESP: Initializing\n"
              f"\tport={self.__ser.port}\n"
              f"\tbaudrate={self.__ser.baudrate}\n"
              f"\tparity={self.__ser.parity}\n"
              f"\tstopbits={self.__ser.stopbits}\n"
              f"\tbytesize={self.__ser.bytesize}\n"
              f"\trtscts={self.__ser.rtscts}\n"
              f"\ttimeout={self.__ser.timeout}")

    def connection_check(self):
        """
        Checks if the ESP302 controller is properly connected and responsive.

        This method sends a test command ('TE') to the controller and checks for a response. If the controller
        responds, the connection is considered successful; otherwise, the connection is deemed to have failed.

        Returns:
        --------
        bool
            True if the connection is successful, False if the connection check fails.

        Example:
        --------
        connection_status = connection_check()
            Checks the connection status of the controller and prints the result.

        Note:
        -----
        The connection check is crucial to ensure that the controller is online and capable of receiving further commands.
        """
        response = self.send_command_no_error_check("TE", None, 2)
        if response == '':
            print("ESP: Connection check failed")
            return False
        else:
            print("ESP: Connection check successful")
            return True

    def start_up(self):
        """
        Initializes the ESP302 controller by enabling motors and performing a homing sequence on all axes.

        This method performs the following steps:

        1. Iterates through all three axes of the ESP302 controller.
        2. Sends the "MO" (Motor On) command to each axis, powering it on.
        3. Sends the "OR" (Origin Search) command to each axis, initiating a homing sequence.
        4. Waits for all axes to complete their movements using the `wait_for_movement` method.

        The homing sequence ensures that each axis moves to its reference position, establishing a known starting point
        for subsequent operations. This is critical for ensuring accurate positioning during later commands.

        Example:
        --------
        start_up()
            Powers on all axes and performs a homing sequence to align them to their reference positions.

        Note:
        -----
        Ensure that all connected stages are clear of obstructions and properly mounted before calling this method
        to prevent potential damage during the homing process.
        """
        for i in range(3):
            self.send_command("MO", i + 1)
            print(f"ESP: Axis {i+1} power on")
            self.send_command("OR", i + 1)
            print(f"ESP: Axis {i+1} homing")
        self.wait_for_movement()

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
        self.__ser.flush()
        self.__ser.close()
        del self
        print("ESP: Connection closed")

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
        self.__ser.write(full_command)

        response = self.__ser.read_until(b'\r\r\n').decode()
        print(f"ESP: Command sent: {repr(full_command)}, response: {repr(response)}")
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
        self.clear_error_buffer()

        response = self.send_command_no_error_check(command, xx_parameter, nn_parameter, debug)

        error_code = self.send_command_no_error_check("TE", None, 1)

        if error_code == '':
            print("ESP: Error check failed: Connection lost")
            raise SerialError("Connection lost!")
        elif int(error_code) == 0:
            print("ESP: Error check: OK")
            return response
        else:
            error_buffer = self.send_command_no_error_check("TB")
            print(f"ESP: Error check failed: {error_buffer}")
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
            print("ESP: Error check failed: Connection lost")
            raise SerialError("Connection lost!")
        elif int(error_count) == 0:
            print("ESP: Error check: OK")
            return True
        else:
            errors = []
            for i in range(int(error_count)):
                error = self.send_command_no_error_check("TB")
                errors.append(error)
            print(f"ESP: Error check failed: {errors}")
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
                print("ESP: Error buffer cleared")
                break

    def get_motion_status(self):
        """
        Retrieves the motion status of all three axes.

        This method queries the ESP302 controller to determine whether each of the three axes (X, Y, and Phi) is currently in motion.
        The status is returned as a list of binary values, where 1 indicates that the axis is in motion, and 0 indicates that it is stationary.

        The method sends the "TS" (Tell Status) command to the controller, which returns the status in ASCII format. This status is then converted into a binary representation, with each bit corresponding to the motion state of one axis.

        Returns:
        --------
        List[int]
            A list of three integers (1 or 0) representing the motion state of the X, Y, and Phi axes, respectively.

        Raises:
        -------
        SerialError
            If the motion state cannot be read or if an invalid motion state is detected.

        Example:
        --------
        status = get_motion_status()
            Retrieves the motion status of all axes and prints whether each axis is in motion.

        Note:
        -----
        This method provides a simple way to monitor the movement of the axes, which is essential for ensuring that commands are issued only when the axes are in the correct state.
        """
        ascii_response = self.send_command("TS")[:-3].encode()
        binary = bin(int.from_bytes(ascii_response, "big"))[2:].zfill(8)

        print("ESP: get motion state")

        motion_state = []
        for i in range(3):
            if binary[-(i + 1)] == "1":
                motion_state.append(1)
                print(f"\tAxis {i + 1} in motion")
            elif binary[-(i + 1)] == "0":
                motion_state.append(0)
                print(f"\tAxis {i + 1} not in motion")
            else:
                print(f"\fAxis {i + 1} invalid reading")
                raise SerialError("Invalid reading for motion state")
        return motion_state

    def get_axis_position(self):
        """
        Retrieves the current position of all axes.

        This method queries the ESP302 controller for the positions of all three axes (X, Y, and Phi).
        The positions are returned as a list of floats, corresponding to the positions of the axes in user-defined units.

        Returns:
        --------
        List[float]
            A list containing the current positions of the X, Y, and Phi axes.

        Example:
        --------
        positions = get_axis_position()
            Retrieves the current positions of all three axes and prints them.

        Note:
        -----
        This method is useful for obtaining the precise position of each axis, which is essential
        for tasks that require accurate positioning.
        """

        position_str = self.send_command("TP")

        position = position_str.strip().split(",")
        position_float = [float(item) for item in position]

        print(f"ESP: get axis position\n\tAxis 1: {position_float[0]}\n\tAxis 2: {position_float[1]}\n\tAxis 3: {position_float[2]}")

        return position_float

    def get_axis_speed(self):
        """
        Retrieves the current speed of all axes.

        This method queries the ESP302 controller for the current speeds of the X, Y, and Phi axes.
        The speeds are returned as a list of floats, corresponding to the speeds of the axes in units/second.

        Returns:
        --------
        List[float]
            A list containing the current speeds of the X, Y, and Phi axes.

        Example:
        --------
        speeds = get_axis_speed()
            Retrieves the current speeds of all three axes and prints them.

        Note:
        -----
        This method is useful for monitoring the speed at which each axis is moving, which can
        be critical for applications that require precise control of motion.
        """

        speed_axis1_str = self.send_command("TV", 1)
        speed_axis2_str = self.send_command("TV", 2)
        speed_axis3_str = self.send_command("TV", 3)

        speed_list = [float(speed_axis1_str), float(speed_axis2_str), float(speed_axis3_str)]

        print(f"ESP: get axis speed\n\tAxis 1: {speed_list[0]}\n\tAxis 2: {speed_list[1]}\n\tAxis 3: {speed_list[2]}")

        return speed_list

    def move_axis_absolut(self, axis, position, speed=1):
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

        assert 0 < axis <= 3, "axis must be between 1 and 3"
        if 0 <= axis <= 2:
            max_position = 25
        else:
            max_position = 360
        assert 0 <= position <= max_position, f"position must be between 0 and {max_position}"
        max_speed = self.send_command("VU", axis, '?')
        assert speed <= int(max_speed), f"speed can't be higher than {max_speed}"

        print(f"ESP: Move (abs) Axis {axis} to {position} at speed {speed}")

        current_speed = self.send_command_no_error_check("VA", axis, "?").strip()
        self.send_command_no_error_check("EP", 1)
        self.send_command_no_error_check("VA", axis, speed)
        self.send_command_no_error_check("PA", axis, position)
        self.send_command_no_error_check("WS", axis)
        self.send_command_no_error_check("VA", axis, current_speed)
        self.send_command_no_error_check("QP", 1)
        self.send_command_no_error_check("EX", 1)
        self.send_command_no_error_check("XX", 1)
        if self.error_check():
            print("ESP: Movement successful")

    def move_axis_relative(self, axis, units, speed=1):

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
        assert 0 < axis <= 3, "axis must be between 1 and 3"
        max_speed = self.send_command("VU", axis, '?')
        assert speed <= int(max_speed), f"speed can't be higher than {max_speed}"

        print(f"ESP: Move (rel) Axis {axis} {units:+} units at speed {speed}")

        current_speed = self.send_command_no_error_check("VA", axis, "?")
        self.send_command_no_error_check("EP", 1)
        self.send_command_no_error_check("VA", axis, speed)
        self.send_command_no_error_check("PR", axis, units)
        self.send_command_no_error_check("WS", axis)
        self.send_command_no_error_check("VA", axis, current_speed)
        self.send_command_no_error_check("QP", 1)
        self.send_command_no_error_check("EX", 1)
        self.send_command_no_error_check("XX", 1)
        if self.error_check():
            print("ESP: Movement successful")

    def move_to_coordinates(self, x_coordinate: float, y_coordinate: float, phi_coordinate=None, speed=1):
        """
        Moves the system to specified X, Y, and optional Phi coordinates at a given speed.

        This method commands the ESP302 controller to move the X and Y axes to specified absolute positions
        and optionally moves the Phi axis if provided. The method ensures precise positioning by sequentially
        moving each axis to its target position, with checks to ensure that the coordinates are within their
        valid ranges.

        Parameters:
        -----------
        x_coordinate : float
            The target position for the X-axis. Must be within the allowable range of 0 to 25 units.
        y_coordinate : float
            The target position for the Y-axis. Must be within the allowable range of 0 to 25 units.
        phi_coordinate : float, optional
            The target position for the Phi axis. Must be within the allowable range of 0 to 360 units,
            or None if the Phi axis should not be moved (default is None).
        speed : float, optional
            The speed at which to move the axes, in units/second. Must not exceed the maximum allowable speed
            for any axis. The same speed is applied to all axes (default is 1).

        Raises:
        -------
        AssertionError
            If any coordinate is out of its valid range, or if the speed exceeds the maximum allowable speed.

        Example:
        --------
        move_to_coordinates(10.5, 20.0, 180.0, 2.0)
            Moves the X-axis to 10.5 units, the Y-axis to 20.0 units, and the Phi axis to 180.0 units
            at a speed of 2 units/second.

        Note:
        -----
        The method first validates the coordinate ranges and then calls `move_axis_absolut` for each axis,
        performing necessary error checks before and after moving each axis.
        """
        assert 0 <= x_coordinate <= 25, "x_coordinate must be between 0 and 25"
        assert 0 <= y_coordinate <= 25, "y_coordinate must be between 0 and 25"
        if phi_coordinate is not None:
            assert 0 <= phi_coordinate <= 360, "phi_coordinate must be between 0 and 360"

        if phi_coordinate is None:
            print(f"ESP: Move to X:{x_coordinate}, Y:{y_coordinate}")
        if phi_coordinate is not None:
            print(f"ESP: Move to X:{x_coordinate}, Y:{y_coordinate}, PHI: {phi_coordinate}")

        self.move_axis_absolut(1, x_coordinate, speed)
        self.move_axis_absolut(2, y_coordinate, speed)
        if phi_coordinate is not None:
            self.move_axis_absolut(3, phi_coordinate, speed)

    def wait_for_movement(self):
        """
        Waits for all axes to stop moving and ensures that the motion is complete.

        This method repeatedly checks the motion status of all axes by querying the controller. It pauses briefly
        between checks to allow for any ongoing motion to complete. After detecting that all axes are stationary,
        the method waits a short additional period to confirm the motion has fully ceased.

        Returns:
        --------
        bool
            True when all motion has stopped and the axes are stationary.

        Example:
        --------
        wait_for_movement()
            Waits for all axes to finish moving before proceeding with further commands.

        Note:
        -----
        This method is useful for ensuring that subsequent commands are not issued while the axes are still in motion.
        """
        while any(self.get_motion_status()):
            time.sleep(0.1)

        start_time = time.time()
        while time.time() < start_time + 0.3:
            if any(self.get_motion_status()):
                self.wait_for_movement()
            else:
                pass

        return True

    def emergency_stop(self):
        """
        Immediately stops all motion of the axes.

        This method sends an emergency stop command to the ESP302 controller, halting all motion
        on all axes. The method waits until all axes have stopped moving before returning.

        Returns:
        --------
        bool
            True when the emergency stop is successfully executed.

        Example:
        --------
        emergency_stop()
            Initiates an emergency stop on all axes.

        Note:
        -----
        This method should be used in situations where immediate cessation of motion is required,
        such as to prevent collisions or when an unexpected situation occurs.
        """
        print("ESP: Emergency stop initiated!")

        self.send_command_no_error_check("AB")

        while any(self.get_motion_status()):
            pass
        print("ESP: Emergency stop successful")
        return True

    def stop_movement(self):
        """
        Stops any ongoing movement of the axes.

        This method sends a stop command to the ESP302 controller to halt any ongoing motion
        on all axes. It waits until all axes have stopped moving before returning.

        Returns:
        --------
        bool
            True when all motion has stopped successfully.

        Example:
        --------
        stop_movement()
            Stops any ongoing movement of the axes.

        Note:
        -----
        This method can be used to stop the axes in a controlled manner, without the abruptness
        of an emergency stop. It is useful for routine stopping of motion during normal operation.
        """
        self.send_command("ST")

        while any(self.get_motion_status()):
            pass

        print("ESP: Movement stopped")
        return True
