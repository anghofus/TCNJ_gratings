import serial
import logging


logger = logging.getLogger(__name__)
# to use centralized logging add the following code to the top of you code

# log_level = logging.DEBUG
# logging.basicConfig(level=log_level)
#
# logger = logging.getLogger(__name__)
#
# field_styles = {
#     'asctime': {'color': 'white'},
#     'levelname': {'color': 'blue', 'bold': True},
# }
# coloredlogs.install(
#     level=log_level,
#     logger=logger,
#     fmt='%(asctime)s - %(levelname)s - %(message)s',
#     field_styles=field_styles)


class SerialError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.args[0]}"


class LaserController:
    """
    Manages the connection and communication with a laser device over a serial interface.

    The `LaserController` class initializes a serial connection to the laser, provides methods to send commands, check
    the connection status, and safely close the connection. This class is essential for controlling the laser and ensuring
    proper communication is maintained throughout its operation.

    Parameters:
    -----------
    port : str
        The serial port identifier to which the laser is connected (e.g., 'COM3', '/dev/ttyUSB0').

    Returns:
    --------
    None

    Example:
    --------
    controller = LaserController('/dev/ttyUSB0')
        Initializes a connection to the laser on the specified serial port.

    Note:
    -----
    The connection is established with specific settings required by the laser device, such as baud rate, parity, and
    timeout values.
    """
    def __init__(self, port):
        self.__ser = serial.Serial(
            port=port,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )

        logger.info(f"Laser: initialized")
        logger.debug(f"port={self.__ser.port}\n"
                     f"\t\t\tbaudrate={self.__ser.baudrate}\n"
                     f"\t\t\tparity={self.__ser.parity}\n"
                     f"\t\t\tstopbits={self.__ser.stopbits}\n"
                     f"\t\t\tbytesize={self.__ser.bytesize}\n"
                     f"\t\t\ttimeout={self.__ser.timeout}")

        self.send_command(">=0")

    def connection_check(self):
        """
        Verifies if the connection to the laser is active.

        This method sends an empty command to the laser and checks for a standard response. If the expected response
        is received, the connection is considered active; otherwise, it is deemed inactive.

        Returns:
        --------
        bool
            `True` if the connection is active and the laser responds correctly, `False` if the connection is inactive.

        Example:
        --------
        is_connected = controller.connection_check()
            Checks if the connection to the laser is still active.

        Note:
        -----
        This method is useful for ensuring that the laser is ready for further commands or for detecting connection
        issues early.
        """
        response = self.send_command("")
        if response == '\r\n':
            logger.info("Laser: Connection check successful")
            return True
        if response == "":
            logger.critical("Laser: Connection check failed")
            return False

    def close_connection(self):
        """
        Closes the serial connection to the laser and cleans up resources.

        This method flushes any remaining data in the serial buffer, closes the connection to the laser, and deletes the
        `LaserController` instance. It should be called when the laser is no longer needed to ensure proper resource
        management.

        Returns:
        --------
        None

        Example:
        --------
        controller.close_connection()
            Safely closes the connection to the laser.

        Note:
        -----
        Always close the connection when finished with the laser to prevent communication issues or resource leaks.
        """
        self.__ser.flush()
        self.__ser.close()
        del self
        logger.info("Laser: Connection closed")

    def send_command(self, command):
        """
        Sends a command to the laser and handles the response.

        This method constructs and sends a command string to the laser, waits for a response, and processes it. If the
        laser returns an unknown command or if the connection is lost, a `SerialError` is raised. Otherwise, the response
        is returned for further processing.

        Parameters:
        -----------
        command : str
            The command to send to the laser. It should be formatted according to the laser's command protocol.

        Returns:
        --------
        str
            The decoded response from the laser, if no errors are detected.

        Raises:
        -------
        SerialError
            If the laser returns an unknown command (indicated by a null character) or if the connection is lost
            (indicated by an empty response).

        Example:
        --------
        response = controller.send_command("PON")
            Sends the "PON" (Power On) command to the laser and returns the response.

        Note:
        -----
        This method is central to interacting with the laser, as it handles both the command transmission and error
        checking processes.
        """
        full_command = f"{command}\r"
        self.__ser.write(full_command.encode())

        response = self.__ser.read_until(b'\r\n').decode()
        if "\x00" in response:
            logger.error(f"Laser: Command {repr({full_command})} is unknown")
            raise SerialError("Command unknown")
        elif response == "":
            logger.critical("Laser: Connection lost")
            raise SerialError("Connection lost")
        else:
            logger.info(f"Laser: Command sent: {repr(full_command)}")
            logger.debug(f"Laser: Command sent: {repr(full_command)}, response: {repr(response)}")
            return response
