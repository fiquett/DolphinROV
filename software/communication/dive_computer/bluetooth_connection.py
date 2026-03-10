# Bluetooth Connection Interface for Dive Computers

import socket
import time


class BluetoothConnection:
    """Manages a Bluetooth RFCOMM connection to a dive computer."""

    RFCOMM_PORT = 1

    def __init__(self, device_name, mac_address=None, port=None):
        self.device_name = device_name
        self.mac_address = mac_address
        self.port = port or self.RFCOMM_PORT
        self._socket = None
        self._connected = False
        self._cached_data = {}

    def connect(self):
        """Establish Bluetooth RFCOMM connection to the device."""
        if not self.mac_address:
            raise ConnectionError(
                f"No MAC address provided for '{self.device_name}'. "
                "Scan for devices or supply mac_address explicitly."
            )
        try:
            self._socket = socket.socket(
                socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
            )
            self._socket.settimeout(10)
            self._socket.connect((self.mac_address, self.port))
            self._connected = True
            print(f"Connected to {self.device_name} ({self.mac_address})")
        except OSError as e:
            self._connected = False
            self._socket = None
            raise ConnectionError(f"Bluetooth connection failed: {e}") from e

    def is_connected(self):
        return self._connected

    def get_data(self):
        """Read a data packet from the dive computer and parse key metrics."""
        if not self._connected or self._socket is None:
            raise ConnectionError("Not connected to dive computer")
        try:
            raw = self._socket.recv(4096)
            self._cached_data = self._parse_packet(raw)
        except OSError as e:
            self._connected = False
            raise ConnectionError(f"Failed to read data: {e}") from e
        return self._cached_data

    def send_command(self, command):
        """Send a raw command string to the dive computer."""
        if not self._connected or self._socket is None:
            raise ConnectionError("Not connected to dive computer")
        try:
            self._socket.sendall(command.encode("ascii"))
        except OSError as e:
            self._connected = False
            raise ConnectionError(f"Failed to send command: {e}") from e

    def disconnect(self):
        """Close the Bluetooth connection."""
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
        self._socket = None
        self._connected = False
        print(f"Disconnected from {self.device_name}")

    # Context-manager support ---------------------------------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    # Internal helpers ----------------------------------------------------------

    @staticmethod
    def _parse_packet(raw_bytes):
        """Parse a simple key=value CSV packet returned by most dive computers.

        Expected format (ASCII): ``DEPTH=15.2,AIR=180,TEMP=22.5,TIME=42``
        Returns a dict with float values where parseable.
        """
        data = {}
        try:
            text = raw_bytes.decode("ascii", errors="replace").strip()
            for token in text.split(","):
                if "=" in token:
                    key, _, value = token.partition("=")
                    try:
                        data[key.strip().lower()] = float(value.strip())
                    except ValueError:
                        data[key.strip().lower()] = value.strip()
        except Exception:
            pass
        return data
