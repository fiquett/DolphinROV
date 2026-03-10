"""Unit tests for BluetoothConnection (without real hardware)."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from software.communication.dive_computer.bluetooth_connection import BluetoothConnection


class TestBluetoothConnectionInit(unittest.TestCase):

    def test_default_port(self):
        conn = BluetoothConnection("TestDevice")
        self.assertEqual(conn.port, BluetoothConnection.RFCOMM_PORT)

    def test_custom_port(self):
        conn = BluetoothConnection("TestDevice", port=3)
        self.assertEqual(conn.port, 3)

    def test_not_connected_on_init(self):
        conn = BluetoothConnection("TestDevice")
        self.assertFalse(conn.is_connected())

    def test_connect_without_mac_raises(self):
        conn = BluetoothConnection("TestDevice")
        with self.assertRaises(ConnectionError):
            conn.connect()

    def test_get_data_when_not_connected_raises(self):
        conn = BluetoothConnection("TestDevice")
        with self.assertRaises(ConnectionError):
            conn.get_data()

    def test_send_command_when_not_connected_raises(self):
        conn = BluetoothConnection("TestDevice")
        with self.assertRaises(ConnectionError):
            conn.send_command("STATUS?")

    def test_disconnect_when_not_connected_is_safe(self):
        conn = BluetoothConnection("TestDevice")
        conn.disconnect()  # should not raise
        self.assertFalse(conn.is_connected())


class TestBluetoothPacketParser(unittest.TestCase):

    def test_parse_valid_packet(self):
        raw = b"depth=15.2,air=180,temp=22.5"
        result = BluetoothConnection._parse_packet(raw)
        self.assertAlmostEqual(result["depth"], 15.2)
        self.assertAlmostEqual(result["air"], 180.0)
        self.assertAlmostEqual(result["temp"], 22.5)

    def test_parse_empty_packet(self):
        result = BluetoothConnection._parse_packet(b"")
        self.assertEqual(result, {})

    def test_parse_string_value(self):
        raw = b"status=OK,depth=10"
        result = BluetoothConnection._parse_packet(raw)
        self.assertEqual(result["status"], "OK")
        self.assertAlmostEqual(result["depth"], 10.0)

    def test_parse_malformed_packet(self):
        # Should not raise, just return empty or partial
        result = BluetoothConnection._parse_packet(b"garbage!!!")
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
