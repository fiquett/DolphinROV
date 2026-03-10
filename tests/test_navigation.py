"""Unit tests for NavigationSystem (A* pathfinding)."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from software.navigation.navigation_system import NavigationSystem


class TestNavigationSystem(unittest.TestCase):

    def setUp(self):
        self.nav = NavigationSystem()

    def test_initial_state(self):
        self.assertEqual(self.nav.current_location, (0, 0, 0))
        self.assertIsNone(self.nav.destination)
        self.assertEqual(self.nav.path, [])

    def test_update_location(self):
        self.nav.update_location((3, 4, -2))
        self.assertEqual(self.nav.current_location, (3, 4, -2))

    def test_set_destination_clears_path(self):
        self.nav.path = [(0, 0, 0), (1, 0, 0)]
        self.nav.set_destination((5, 5, 0))
        self.assertEqual(self.nav.destination, (5, 5, 0))
        self.assertEqual(self.nav.path, [])

    def test_navigate_no_destination(self):
        result = self.nav.navigate_to_destination()
        self.assertEqual(result, [])

    def test_navigate_to_adjacent_cell(self):
        self.nav.set_destination((1, 0, 0))
        path = self.nav.navigate_to_destination()
        self.assertEqual(path[0], (0, 0, 0))
        self.assertEqual(path[-1], (1, 0, 0))

    def test_navigate_finds_path(self):
        self.nav.set_destination((3, 3, 0))
        path = self.nav.navigate_to_destination()
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], (0, 0, 0))
        self.assertEqual(path[-1], (3, 3, 0))

    def test_navigate_avoids_obstacles(self):
        # Block intermediate cells but leave destination clear
        for x in range(1, 3):
            self.nav.add_obstacle((x, 0, 0))  # block (1,0,0) and (2,0,0)
        self.nav.set_destination((3, 0, 0))   # (3,0,0) is open
        path = self.nav.navigate_to_destination()
        self.assertGreater(len(path), 0)
        self.assertEqual(path[-1], (3, 0, 0))
        # The blocked intermediate cells must not appear in the path
        for x in range(1, 3):
            self.assertNotIn((x, 0, 0), path)

    def test_navigate_goal_in_obstacle_returns_empty(self):
        self.nav.add_obstacle((2, 0, 0))
        self.nav.set_destination((2, 0, 0))
        path = self.nav.navigate_to_destination()
        self.assertEqual(path, [])

    def test_navigate_same_start_and_goal(self):
        self.nav.set_destination((0, 0, 0))
        path = self.nav.navigate_to_destination()
        self.assertEqual(path, [(0, 0, 0)])

    def test_estimated_travel_time_no_path(self):
        self.assertAlmostEqual(self.nav.estimated_travel_time(), 0.0)

    def test_estimated_travel_time_positive(self):
        self.nav.set_destination((5, 0, 0))
        self.nav.navigate_to_destination()
        self.assertGreater(self.nav.estimated_travel_time(), 0.0)

    def test_next_waypoint_no_path(self):
        self.assertIsNone(self.nav.next_waypoint())

    def test_next_waypoint_returns_second_cell(self):
        self.nav.set_destination((2, 0, 0))
        path = self.nav.navigate_to_destination()
        wp = self.nav.next_waypoint()
        self.assertEqual(wp, path[1])


if __name__ == "__main__":
    unittest.main()
