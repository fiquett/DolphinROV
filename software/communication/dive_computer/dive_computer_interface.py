# Dive Computer Interface

from .bluetooth_connection import BluetoothConnection


def connect_dive_computer(device_name="DiveComputer123", mac_address=None):
    """Connects to a dive computer via Bluetooth.

    Args:
        device_name: Friendly name used for logging.
        mac_address: Bluetooth MAC address of the dive computer (e.g. "AA:BB:CC:DD:EE:FF").

    Returns:
        An open BluetoothConnection instance, or None on failure.
    """
    try:
        connection = BluetoothConnection(device_name=device_name, mac_address=mac_address)
        connection.connect()
        if connection.is_connected():
            print("Dive computer connected successfully")
            return connection
    except ConnectionError as e:
        print(f"Failed to connect to dive computer: {e}")
    return None


def fetch_dive_data(connection):
    """Fetches dive data from the connected dive computer.

    Args:
        connection: An open BluetoothConnection instance.

    Returns:
        A dict with keys such as 'depth', 'air', 'temp', 'time'.
    """
    data = connection.get_data()
    depth = data.get("depth", "N/A")
    air = data.get("air", "N/A")
    print(f"Dive depth: {depth} meters")
    print(f"Remaining air: {air} bar")
    return data
