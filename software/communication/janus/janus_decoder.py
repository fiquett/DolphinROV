# JANUS Protocol Decoder

from typing import Any, Callable, Dict, Optional


class JANUSDecoder:
    """Decodes incoming JANUS protocol messages and dispatches them to handlers.

    Message format: ``<COMMAND>:<key1=val1,key2=val2,...>``
    """

    def __init__(self):
        self._telemetry: Dict[str, Any] = {}
        self._stop_requested: bool = False
        self._alert_log: list = []

        self.commands: Dict[str, Callable[[str], None]] = {
            "STOP": self.stop_operations,
            "DATA": self.process_data,
            "STATUS": self.process_status,
            "ALERT": self.process_alert,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decode_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse and dispatch a JANUS message.

        Returns the parsed payload dict, or None on error.
        """
        try:
            header, _, payload_str = message.partition(":")
            header = header.strip().upper()
            if header in self.commands:
                parsed = self._parse_payload(payload_str)
                self.commands[header](payload_str)
                return parsed
            else:
                print(f"Unknown JANUS command: {header}")
                return None
        except Exception as e:
            print(f"Invalid JANUS message format: {e}")
            return None

    @property
    def telemetry(self) -> Dict[str, Any]:
        """Current telemetry state accumulated from DATA/STATUS messages."""
        return dict(self._telemetry)

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    @property
    def alert_log(self) -> list:
        return list(self._alert_log)

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------

    def stop_operations(self, payload: str):
        """Handle STOP command — sets the stop flag and logs reason."""
        parsed = self._parse_payload(payload)
        reason = parsed.get("REASON", "UNSPECIFIED")
        self._stop_requested = True
        print(f"STOP command received (reason={reason}). Halting all operations.")

    def process_data(self, payload: str):
        """Handle DATA command — merge key-value pairs into telemetry store."""
        parsed = self._parse_payload(payload)
        self._telemetry.update(parsed)
        print(f"DATA received: {parsed}")

    def process_status(self, payload: str):
        """Handle STATUS message — same as DATA but tagged differently."""
        parsed = self._parse_payload(payload)
        self._telemetry.update(parsed)
        print(f"STATUS received: {parsed}")

    def process_alert(self, payload: str):
        """Handle ALERT message — log alert and print warning."""
        parsed = self._parse_payload(payload)
        alert_type = parsed.get("TYPE", "UNKNOWN")
        severity = parsed.get("SEVERITY", "INFO")
        self._alert_log.append(parsed)
        print(f"ALERT [{severity}]: {alert_type}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_payload(payload_str: str) -> Dict[str, Any]:
        """Parse ``key=value,key=value`` payload into a dict.

        Values are cast to float when possible, otherwise kept as strings.
        """
        result: Dict[str, Any] = {}
        for token in payload_str.split(","):
            token = token.strip()
            if "=" in token:
                key, _, raw_val = token.partition("=")
                try:
                    result[key.strip()] = float(raw_val.strip())
                except ValueError:
                    result[key.strip()] = raw_val.strip()
        return result


# Example usage:
# decoder = JANUSDecoder()
# decoder.decode_message("DATA:DEPTH=20,TEMP=18.5")
# decoder.decode_message("ALERT:TYPE=LOW_AIR,SEVERITY=CRITICAL")
# print(decoder.telemetry)
