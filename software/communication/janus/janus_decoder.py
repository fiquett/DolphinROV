# JANUS Protocol Decoder

class JANUSDecoder:
    def __init__(self):
        self.commands = {
            "STOP": self.stop_operations,
            "DATA": self.process_data
        }

    def decode_message(self, message):
        try:
            header, payload = message.split(":")
            if header in self.commands:
                self.commands[header](payload)
            else:
                print(f"Unknown command: {header}")
        except ValueError:
            print("Invalid JANUS message format")

    def stop_operations(self, payload):
        print("STOP command received. Halting all operations.")
        # Add logic to stop ROV operations

    def process_data(self, payload):
        print(f"Processing data payload: {payload}")
        # Add logic for processing data
        # Example: Update sensor readings or telemetry logs

# Example usage:
# decoder = JANUSDecoder()
# decoder.decode_message("DATA:DEPTH=20")
