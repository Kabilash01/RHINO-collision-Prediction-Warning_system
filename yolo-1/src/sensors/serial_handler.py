import json
import serial

class SerialHandler:
    def __init__(self, port='COM3', baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connect()

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"[INFO] Connected to serial port {self.port}.")
        except serial.SerialException as e:
            print(f"[ERROR] Could not connect to serial port {self.port}: {e}")
            self.serial = None

    def read_data(self):
        if self.serial and self.serial.in_waiting:
            try:
                line = self.serial.readline().decode(errors='ignore').strip()
                if line.startswith("{") and line.endswith("}"):
                    return json.loads(line)
                else:
                    print("[WARNING] Invalid data received from serial.")
            except Exception as e:
                print(f"[ERROR] Failed to read from serial: {e}")
        return None

    def close(self):
        if self.serial:
            self.serial.close()
            print(f"[INFO] Serial port {self.port} closed.")