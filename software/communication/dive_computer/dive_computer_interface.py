# Dive Computer Interface

def connect_dive_computer():
    """Connects to a dive computer via Bluetooth."""
    try:
        connection = BluetoothConnection(device_name="DiveComputer123")
        if connection.is_connected():
            print("Dive computer connected successfully")
            return connection
    except ConnectionError:
        print("Failed to connect to dive computer")

def fetch_dive_data(connection):
    """Fetches dive data from the connected computer."""
    data = connection.get_data()
    print(f"Dive depth: {data['depth']} meters")
    print(f"Remaining air: {data['air']} bar")
