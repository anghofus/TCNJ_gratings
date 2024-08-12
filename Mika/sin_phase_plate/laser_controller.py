import serial


class SerialError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.args[0]}"


class LaserController:
    def __init__(self, port):
        self.ser = serial.Serial(
            port=port,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
       # self.send_command(">=0")

    def connection_check(self):
        response = self.send_command("")
        if response == '\r\n':
            return True
        if response == "":
            return False

    def close_connection(self):
        self.ser.flush()
        self.ser.close()
        del self

    def send_command(self, command):
        full_command = f"{command}\r"
        self.ser.write(full_command.encode())

        response = self.ser.read_until(b'\r\n').decode()
        if "\x00" in response:
            raise SerialError("Command unknown")
        elif response == "":
            raise SerialError("Connection lost")
        else:
            return response
