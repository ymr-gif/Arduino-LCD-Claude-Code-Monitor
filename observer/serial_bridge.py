import time

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

class SerialBridge:
    def __init__(self, port: str, baud_rate: int):
        self._port = port
        self._baud = baud_rate
        self._conn = None
        self._connect()

    def _connect(self):
        if not SERIAL_AVAILABLE:
            return
        try:
            self._conn = serial.Serial(self._port, self._baud, timeout=1)
            time.sleep(2)
        except Exception:
            self._conn = None

    def _write(self, data: str):
        if self._conn is None:
            self._connect()
            if self._conn is None:
                return
        try:
            self._conn.write(data.encode())
        except Exception:
            self._conn = None

    def send(self, row1: str, row2: str):
        self._write(f"L1:{row1}\nL2:{row2}\n")

    def set_backlight(self, on: bool):
        self._write(f"BL:{'1' if on else '0'}\n")

    def close(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
