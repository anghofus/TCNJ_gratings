import serial


class ShutterController:
    """
    A Python interface for controlling the SC10 shutter controller via a serial connection.

    The `ShutterController` class provides a high-level interface to interact with the SC10 controller,
    allowing users to open or close the shutter, check its status, and ensure proper communication with the device.
    The class handles the low-level details of serial communication, offering simple methods for common operations.

    Attributes:
    -----------
    ser : serial.Serial
        The serial connection to the SC10 controller.

    Methods:
    --------
    connection_check() -> bool:
        Checks the connection with the SC10 controller by sending an empty command.
        Returns `True` if the connection is established and an expected error response is received.
        Returns `False` if no response is received.

    close_connection():
        Closes the serial connection to the SC10 controller and deletes the instance.

    send_command(command: str) -> str:
        Sends a command to the SC10 controller and reads the response.

    get_shutter_state() -> bool:
        Retrieves the current state of the shutter (open or closed) from the SC10 controller.
        Returns `True` if the shutter is open, `False` if it is closed.

    open_shutter() -> bool:
        Opens the shutter if it is currently closed.
        Returns `True` if the shutter was successfully opened, `False` if it was already open.

    close_shutter() -> bool:
        Closes the shutter if it is currently open.
        Returns `True` if the shutter was successfully closed, `False` if it was already closed.

    Note:
    -----
    This class assumes that the SC10 controller is properly connected via a serial port and that the shutter is correctly installed.
    Before using this class, ensure that the serial port is accessible, the controller is powered on, and the shutter is in a known state.
    """
    def __init__(self, port):
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        print(f"Shutter: Initializing\n"
              f"\tport={self.ser.port}\n"
              f"\tbaudrate={self.ser.baudrate}\n"
              f"\tparity={self.ser.parity}\n"
              f"\tstopbits={self.ser.stopbits}\n"
              f"\tbytesize={self.ser.bytesize}\n"
              f"\ttimeout={self.ser.timeout}")

    def connection_check(self):
        """
            Checks the connection with the SC10 controller by sending an empty command.

        Returns:
            bool: True if the connection is established and responds with an error indicating
                  that the command is not defined. False if no response is received.
        """
        response = self.send_command("")
        if "Command error CMD_NOT_DEFINED" in response:
            print("Shutter: Connection check successful")
            return True
        if response == "":
            print("Shutter: Connection check failed")
            return False

    def close_connection(self):
        """
        Closes the serial connection to the SC10 controller and deletes the instance.
        This function should be called when the communication with the device is no longer needed.
        """
        self.ser.flush()
        self.ser.close()
        del self
        print("Shutter: Connection closed")

    def send_command(self, command: str):
        """
        Sends a command to the SC10 controller and reads the response.

        Args:
            command (str): The command string to be sent to the controller.

        Returns:
            str: The response received from the controller.
        """
        full_command = f"{command}\r"
        self.ser.write(full_command.encode())

        response = repr(self.ser.read_until(b'>').decode())

        print(f"Shutter: Command sent: {repr(full_command)}, response: {repr(response)}")

        return response

    def get_shutter_state(self):
        """
        Retrieves the current state of the shutter (open or closed) from the SC10 controller.

        Returns:
            bool: True if the shutter is open, False if it is closed.
        """
        response = self.send_command("ens?")

        if "0" in response:
            print("Shutter: is closed")
            return False
        if "1" in response:
            print("Shutter: is open")
            return True

    def open_shutter(self):
        """
        Opens the shutter if it is currently closed.

        Returns:
            bool: True if the shutter was successfully opened, False if the shutter was already open.
        """
        print("Shutter: Open shutter")
        state = self.get_shutter_state()
        if not state:
            self.send_command("ens")
            print("Shutter: Opened")
            return True
        else:
            print("Shutter: already open")
            return False

    def close_shutter(self):
        """
        Closes the shutter if it is currently open.

        Returns:
            bool: True if the shutter was successfully closed, False if the shutter was already closed.
        """
        print("Shutter: Close shutter")
        state = self.get_shutter_state()
        if state:
            self.send_command("ens")
            print("Shutter: closed")
            return True
        else:
            print("Shutter: already closed")
            return False
