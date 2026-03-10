# JANUS Protocol Encoder — complement to JANUSDecoder

from typing import Any, Dict


class JANUSEncoder:
    """Encodes outgoing JANUS protocol messages for DolphinROV.

    Message format: ``<COMMAND>:<key1=val1,key2=val2,...>``

    Supported commands
    ------------------
    STATUS   — telemetry status broadcast
    DATA     — arbitrary key-value data payload
    ALERT    — safety or operational alert
    STOP     — request remote system to halt operations
    """

    SUPPORTED_COMMANDS = frozenset(["STATUS", "DATA", "ALERT", "STOP"])

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------

    def encode_status(self, status_data: Dict[str, Any]) -> str:
        """Encode a STATUS message from a dict of telemetry values."""
        return self._encode("STATUS", status_data)

    def encode_data(self, data_dict: Dict[str, Any]) -> str:
        """Encode a DATA message from a dict of sensor readings."""
        return self._encode("DATA", data_dict)

    def encode_alert(self, alert_type: str, severity: str) -> str:
        """Encode an ALERT message.

        Args:
            alert_type: e.g. "LOW_AIR", "OBSTACLE", "DIVER_DISTRESS"
            severity:   "INFO", "WARNING", or "CRITICAL"
        """
        return self._encode("ALERT", {"TYPE": alert_type, "SEVERITY": severity})

    def encode_stop(self, reason: str = "MANUAL") -> str:
        """Encode a STOP command."""
        return self._encode("STOP", {"REASON": reason})

    # ------------------------------------------------------------------
    # Low-level encoder
    # ------------------------------------------------------------------

    def encode_message(self, command: str, payload: Dict[str, Any]) -> str:
        """Encode a message with an explicit command string.

        Raises ValueError for unsupported commands.
        """
        command = command.upper()
        if command not in self.SUPPORTED_COMMANDS:
            raise ValueError(
                f"Unsupported JANUS command '{command}'. "
                f"Supported: {sorted(self.SUPPORTED_COMMANDS)}"
            )
        return self._encode(command, payload)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _encode(command: str, payload: Dict[str, Any]) -> str:
        payload_str = ",".join(f"{k}={v}" for k, v in payload.items())
        return f"{command}:{payload_str}"


# Example usage:
# encoder = JANUSEncoder()
# print(encoder.encode_status({"DEPTH": 15.2, "SPEED": 1.5, "HEADING": 270}))
# print(encoder.encode_alert("LOW_AIR", "CRITICAL"))
# print(encoder.encode_stop())
