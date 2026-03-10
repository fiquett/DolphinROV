# Navigation System with 3-D A* Pathfinding

import heapq
import math
from typing import List, Optional, Tuple


Coord3D = Tuple[int, int, int]


class NavigationSystem:
    """Autonomous 3-D navigation for DolphinROV.

    Coordinates are integer grid cells (x, y, z) where z < 0 means depth.
    Real-world scale is set by *cell_size_m* (default 1 m per cell).
    """

    # 26-directional movement in 3-D grid (face + edge + corner neighbours)
    _MOVES = [
        (dx, dy, dz)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        for dz in (-1, 0, 1)
        if not (dx == 0 and dy == 0 and dz == 0)
    ]

    def __init__(self, cell_size_m: float = 1.0):
        self.cell_size_m = cell_size_m
        self.current_location: Coord3D = (0, 0, 0)
        self.destination: Optional[Coord3D] = None
        self.obstacles: set = set()
        self.path: List[Coord3D] = []
        self.speed_ms: float = 1.5  # metres per second

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_location(self, location: Coord3D):
        """Update the ROV's current grid position."""
        self.current_location = location
        print(f"Current location updated to: {self.current_location}")

    def set_destination(self, destination: Coord3D):
        """Set the target grid position."""
        self.destination = destination
        self.path = []
        print(f"Destination set to: {self.destination}")

    def add_obstacle(self, obstacle: Coord3D):
        """Register an obstacle cell that pathfinding must avoid."""
        self.obstacles.add(obstacle)

    def remove_obstacle(self, obstacle: Coord3D):
        self.obstacles.discard(obstacle)

    def navigate_to_destination(self) -> List[Coord3D]:
        """Compute the A* path from current location to destination.

        Returns the ordered list of waypoints (including start and goal),
        or an empty list if no destination is set or no path exists.
        """
        if self.destination is None:
            print("No destination set.")
            return []

        self.path = self._astar(self.current_location, self.destination)

        if self.path:
            print(
                f"Navigating from {self.current_location} to {self.destination} — "
                f"{len(self.path)} waypoints, ~{self.estimated_travel_time():.1f}s."
            )
        else:
            print("No path found to destination.")
        return self.path

    def estimated_travel_time(self) -> float:
        """Estimate travel time in seconds based on path length and speed."""
        if len(self.path) < 2:
            return 0.0
        total_cells = sum(
            self._euclidean(self.path[i], self.path[i + 1])
            for i in range(len(self.path) - 1)
        )
        return total_cells * self.cell_size_m / self.speed_ms

    def next_waypoint(self) -> Optional[Coord3D]:
        """Return the next waypoint in the current path, if any."""
        if len(self.path) > 1:
            return self.path[1]
        return None

    # ------------------------------------------------------------------
    # A* implementation
    # ------------------------------------------------------------------

    # Maximum nodes to expand before giving up (prevents infinite search)
    _MAX_NODES = 50_000

    def _astar(self, start: Coord3D, goal: Coord3D) -> List[Coord3D]:
        if goal in self.obstacles:
            return []  # goal is blocked — no path possible

        open_heap: List[Tuple[float, Coord3D]] = []
        heapq.heappush(open_heap, (0.0, start))

        came_from: dict = {}
        g_score: dict = {start: 0.0}
        expanded = 0

        while open_heap:
            if expanded >= self._MAX_NODES:
                return []  # search budget exhausted
            _, current = heapq.heappop(open_heap)
            expanded += 1

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for neighbour in self._neighbours(current):
                tentative_g = g_score[current] + self._euclidean(current, neighbour)
                if tentative_g < g_score.get(neighbour, math.inf):
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g
                    f = tentative_g + self._euclidean(neighbour, goal)
                    heapq.heappush(open_heap, (f, neighbour))

        return []  # no path found

    def _neighbours(self, node: Coord3D) -> List[Coord3D]:
        x, y, z = node
        result = []
        for dx, dy, dz in self._MOVES:
            nb = (x + dx, y + dy, z + dz)
            if nb not in self.obstacles:
                result.append(nb)
        return result

    @staticmethod
    def _euclidean(a: Coord3D, b: Coord3D) -> float:
        return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

    @staticmethod
    def _reconstruct_path(came_from: dict, current: Coord3D) -> List[Coord3D]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path


# Example usage:
# nav = NavigationSystem()
# nav.set_destination((10, 20, -5))
# nav.navigate_to_destination()
