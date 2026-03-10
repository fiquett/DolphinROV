"""Unit tests for DecisionEngine."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from software.ai.decision_engine import DecisionEngine


class TestDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DecisionEngine()

    def test_initial_state(self):
        self.assertEqual(self.engine.state, "IDLE")

    def test_idle_on_no_inputs(self):
        decision = self.engine.make_decision({})
        self.assertEqual(decision["action"], "IDLE")
        self.assertEqual(decision["state"], "IDLE")

    def test_emergency_ascent_low_air(self):
        decision = self.engine.make_decision({"air_bar": 30})
        self.assertEqual(decision["action"], "ASCEND")
        self.assertEqual(decision["state"], "EMERGENCY_ASCENT")

    def test_emergency_ascent_depth_exceeded(self):
        decision = self.engine.make_decision({"depth_m": 50, "air_bar": 150})
        self.assertEqual(decision["action"], "ASCEND")
        self.assertEqual(decision["state"], "EMERGENCY_ASCENT")

    def test_low_air_warning_in_alerts(self):
        decision = self.engine.make_decision({"air_bar": 75})
        self.assertTrue(any("Low air" in a for a in decision["alerts"]))

    def test_diver_distress(self):
        decision = self.engine.make_decision({
            "diver_signal": "NEED_HELP",
            "air_bar": 120,
        })
        self.assertEqual(decision["action"], "ASSIST")
        self.assertEqual(decision["state"], "ASSISTING_DIVER")

    def test_navigating_state(self):
        decision = self.engine.make_decision({
            "nav_status": "NAVIGATING",
            "air_bar": 150,
        })
        self.assertEqual(decision["action"], "CONTINUE")
        self.assertEqual(decision["state"], "NAVIGATING")

    def test_arrived_transitions_to_idle(self):
        decision = self.engine.make_decision({
            "nav_status": "ARRIVED",
            "air_bar": 150,
        })
        self.assertEqual(decision["action"], "HOLD")
        self.assertEqual(decision["state"], "IDLE")

    def test_obstacle_triggers_replan(self):
        self.engine.state = "NAVIGATING"
        decision = self.engine.make_decision({
            "obstacle": True,
            "nav_status": "NAVIGATING",
            "air_bar": 150,
        })
        self.assertEqual(decision["action"], "REPLAN")
        self.assertTrue(any("Obstacle" in a for a in decision["alerts"]))

    def test_emergency_overrides_diver_signal(self):
        """Emergency ascent takes priority over diver distress signal."""
        decision = self.engine.make_decision({
            "air_bar": 20,
            "diver_signal": "NEED_HELP",
        })
        self.assertEqual(decision["action"], "ASCEND")

    def test_execute_known_task(self):
        result = self.engine.execute_task("ASCEND")
        self.assertIn("ascent", result.lower())

    def test_execute_unknown_task(self):
        result = self.engine.execute_task("FLY")
        self.assertIn("Unknown", result)


if __name__ == "__main__":
    unittest.main()
