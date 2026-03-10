"""Unit tests for JANUSDecoder and JANUSEncoder."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from software.communication.janus.janus_decoder import JANUSDecoder
from software.communication.janus.janus_encoder import JANUSEncoder


class TestJANUSDecoder(unittest.TestCase):

    def setUp(self):
        self.decoder = JANUSDecoder()

    def test_decode_data_message(self):
        result = self.decoder.decode_message("DATA:DEPTH=20,TEMP=18.5")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["DEPTH"], 20.0)
        self.assertAlmostEqual(result["TEMP"], 18.5)

    def test_data_updates_telemetry(self):
        self.decoder.decode_message("DATA:DEPTH=15")
        self.assertAlmostEqual(self.decoder.telemetry["DEPTH"], 15.0)

    def test_decode_status_message(self):
        result = self.decoder.decode_message("STATUS:SPEED=1.5,HEADING=270")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["SPEED"], 1.5)

    def test_decode_stop_message(self):
        self.decoder.decode_message("STOP:REASON=MANUAL")
        self.assertTrue(self.decoder.stop_requested)

    def test_decode_alert_message(self):
        self.decoder.decode_message("ALERT:TYPE=LOW_AIR,SEVERITY=CRITICAL")
        self.assertEqual(len(self.decoder.alert_log), 1)
        self.assertEqual(self.decoder.alert_log[0]["TYPE"], "LOW_AIR")
        self.assertEqual(self.decoder.alert_log[0]["SEVERITY"], "CRITICAL")

    def test_unknown_command_returns_none(self):
        result = self.decoder.decode_message("FLY:FAST=YES")
        self.assertIsNone(result)

    def test_invalid_format_returns_none(self):
        result = self.decoder.decode_message("NODIVIDER")
        self.assertIsNone(result)

    def test_telemetry_accumulates_across_messages(self):
        self.decoder.decode_message("DATA:DEPTH=20")
        self.decoder.decode_message("DATA:TEMP=22")
        self.assertAlmostEqual(self.decoder.telemetry["DEPTH"], 20.0)
        self.assertAlmostEqual(self.decoder.telemetry["TEMP"], 22.0)


class TestJANUSEncoder(unittest.TestCase):

    def setUp(self):
        self.encoder = JANUSEncoder()

    def test_encode_status(self):
        msg = self.encoder.encode_status({"DEPTH": 15, "SPEED": 1.5})
        self.assertTrue(msg.startswith("STATUS:"))
        self.assertIn("DEPTH=15", msg)
        self.assertIn("SPEED=1.5", msg)

    def test_encode_data(self):
        msg = self.encoder.encode_data({"TEMP": 22})
        self.assertTrue(msg.startswith("DATA:"))
        self.assertIn("TEMP=22", msg)

    def test_encode_alert(self):
        msg = self.encoder.encode_alert("OBSTACLE", "WARNING")
        self.assertTrue(msg.startswith("ALERT:"))
        self.assertIn("OBSTACLE", msg)
        self.assertIn("WARNING", msg)

    def test_encode_stop(self):
        msg = self.encoder.encode_stop("EMERGENCY")
        self.assertTrue(msg.startswith("STOP:"))
        self.assertIn("EMERGENCY", msg)

    def test_encode_message_unknown_command_raises(self):
        with self.assertRaises(ValueError):
            self.encoder.encode_message("FLY", {"FAST": "YES"})

    def test_roundtrip_encode_decode(self):
        original = {"DEPTH": 30.0, "AIR": 180.0}
        encoded = self.encoder.encode_data(original)
        decoder = JANUSDecoder()
        decoded = decoder.decode_message(encoded)
        self.assertAlmostEqual(decoded["DEPTH"], 30.0)
        self.assertAlmostEqual(decoded["AIR"], 180.0)


if __name__ == "__main__":
    unittest.main()
