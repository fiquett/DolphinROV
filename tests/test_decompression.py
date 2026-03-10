"""Unit tests for DecompressionManager (Bühlmann ZH-L16C)."""

import time
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from software.decompression.decompression_manager import DecompressionManager


class TestDecompressionManager(unittest.TestCase):

    def setUp(self):
        self.mgr = DecompressionManager()

    def test_initial_tissue_pressures(self):
        expected = DecompressionManager.SURFACE_PRESSURE_BAR * DecompressionManager.N2_FRACTION
        for tp in self.mgr.tissue_pressures:
            self.assertAlmostEqual(tp, expected, places=4)

    def test_update_exposure_increases_tissue_pressure(self):
        before = list(self.mgr.tissue_pressures)
        self.mgr.update_exposure(depth_m=30, duration_min=20)
        after = self.mgr.tissue_pressures
        # Fast compartments should have increased
        self.assertGreater(after[0], before[0])

    def test_ceiling_at_surface_after_no_dive(self):
        ceiling = self.mgr.ceiling_depth()
        self.assertAlmostEqual(ceiling, 0.0, places=1)

    def test_calculate_stops_returns_safety_stop(self):
        stops = self.mgr.calculate_stops(depth_m=30, duration_min=25)
        # Last stop must always be the mandatory safety stop
        self.assertGreater(len(stops), 0)
        last_depth, last_time = stops[-1]
        self.assertAlmostEqual(last_depth, self.mgr.safety_stop_depth, places=1)
        self.assertAlmostEqual(last_time, self.mgr.safety_stop_duration, places=1)

    def test_calculate_stops_ordered_descending(self):
        stops = self.mgr.calculate_stops(depth_m=40, duration_min=30)
        depths = [d for d, _ in stops]
        self.assertEqual(depths, sorted(depths, reverse=True))

    def test_enforce_safety_stop_sets_timer(self):
        self.assertFalse(self.mgr.is_stop_completed())
        self.mgr.safety_stop_duration = 1 / 60  # 1 second for testing
        self.mgr.enforce_safety_stop()
        time.sleep(1.5)
        self.assertTrue(self.mgr.is_stop_completed())

    def test_cancel_safety_stop(self):
        self.mgr.safety_stop_duration = 60  # long enough not to expire
        self.mgr.enforce_safety_stop()
        self.mgr.cancel_safety_stop()
        self.assertFalse(self.mgr.is_stop_completed())

    def test_stop_timer_remaining_decreases(self):
        self.mgr.safety_stop_duration = 10 / 60  # 10 seconds
        self.mgr.enforce_safety_stop()
        r1 = self.mgr.stop_timer_remaining()
        time.sleep(0.5)
        r2 = self.mgr.stop_timer_remaining()
        self.assertLess(r2, r1)
        self.mgr.cancel_safety_stop()

    def test_is_safe_to_ascend_requires_completed_stop(self):
        # At safety-stop depth, not safe until stop is done
        self.assertFalse(self.mgr.is_safe_to_ascend(self.mgr.safety_stop_depth))

    def test_is_safe_to_ascend_above_stop_depth(self):
        # Deeper than safety stop — not gated by stop timer
        self.assertTrue(self.mgr.is_safe_to_ascend(10.0))

    def test_depth_to_pressure(self):
        p = self.mgr._depth_to_pressure(10.0)
        self.assertAlmostEqual(p, 2.013, places=2)

    def test_callback_invoked_on_stop_complete(self):
        completed = []
        self.mgr.safety_stop_duration = 1 / 60
        self.mgr.enforce_safety_stop(on_complete=lambda: completed.append(True))
        time.sleep(1.5)
        self.assertEqual(completed, [True])


if __name__ == "__main__":
    unittest.main()
