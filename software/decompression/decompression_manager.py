# Decompression Manager — Bühlmann ZH-L16C model with safety-stop timer

import math
import threading
import time
from typing import List, Tuple


class DecompressionManager:
    """Tracks diver tissue saturation using the Bühlmann ZH-L16C algorithm
    and enforces mandatory decompression / safety stops.

    References
    ----------
    Bühlmann, A.A. (1984). *Decompression–Decompression Sickness*.
    Springer-Verlag, Berlin.
    """

    # ZH-L16C half-times (minutes) for 16 tissue compartments
    HALF_TIMES: List[float] = [
        5.0, 8.0, 12.5, 18.5, 27.0, 38.3, 54.3, 77.0,
        109.0, 146.0, 187.0, 238.0, 304.0, 397.0, 503.0, 635.0,
    ]

    # M-value coefficients: P_limit = a + P_amb * b
    M_VALUES_A: List[float] = [
        1.2599, 1.0000, 0.8618, 0.7562, 0.6667, 0.5600, 0.4947, 0.4500,
        0.4187, 0.3798, 0.3497, 0.3223, 0.2850, 0.2737, 0.2523, 0.2327,
    ]
    M_VALUES_B: List[float] = [
        0.5050, 0.6514, 0.7222, 0.7825, 0.8126, 0.8434, 0.8693, 0.8910,
        0.9092, 0.9222, 0.9319, 0.9403, 0.9477, 0.9544, 0.9602, 0.9654,
    ]

    SURFACE_PRESSURE_BAR: float = 1.013   # bar at sea level
    N2_FRACTION: float = 0.7902           # nitrogen fraction in air

    def __init__(self):
        self.ascent_rate: float = 10.0        # metres per minute
        self.safety_stop_depth: float = 5.0   # metres
        self.safety_stop_duration: float = 3.0  # minutes

        # Initialise all compartments at surface saturation
        p_n2_surface = self.SURFACE_PRESSURE_BAR * self.N2_FRACTION
        self.tissue_pressures: List[float] = [p_n2_surface] * 16

        # Safety-stop timer state
        self._stop_timer: threading.Timer | None = None
        self._stop_completed: bool = False
        self._stop_start_time: float | None = None
        self._on_stop_complete_cb = None  # optional callback

    # ------------------------------------------------------------------
    # Tissue saturation
    # ------------------------------------------------------------------

    def update_exposure(self, depth_m: float, duration_min: float):
        """Advance tissue saturation for *duration_min* minutes at *depth_m*."""
        p_amb = self._depth_to_pressure(depth_m)
        p_inspired_n2 = (p_amb - 0.0627) * self.N2_FRACTION  # Schreiner equation
        for i, ht in enumerate(self.HALF_TIMES):
            k = math.log(2) / ht
            self.tissue_pressures[i] += (
                (p_inspired_n2 - self.tissue_pressures[i]) * (1 - math.exp(-k * duration_min))
            )

    def ceiling_depth(self) -> float:
        """Return the shallowest depth (in metres) the diver can safely ascend to."""
        ceiling_pressure = max(
            (self.tissue_pressures[i] - self.M_VALUES_A[i]) / self.M_VALUES_B[i]
            for i in range(16)
        )
        # Convert bar back to depth; clamp to surface
        ceiling_m = max(0.0, (ceiling_pressure - self.SURFACE_PRESSURE_BAR) * 10.0)
        return ceiling_m

    def is_clear_to_ascend(self, current_depth_m: float) -> bool:
        """True if the diver can ascend without violating any M-value."""
        return self.ceiling_depth() <= 0.0

    # ------------------------------------------------------------------
    # Decompression stop planning
    # ------------------------------------------------------------------

    def calculate_stops(self, depth_m: float, duration_min: float) -> List[Tuple[float, float]]:
        """Calculate required decompression stops after a dive.

        Args:
            depth_m:      Bottom depth in metres.
            duration_min: Bottom time in minutes.

        Returns:
            Ordered list of (stop_depth_m, stop_time_min) tuples from
            deepest to shallowest, always ending with the safety stop.
        """
        self.update_exposure(depth_m, duration_min)
        stops: List[Tuple[float, float]] = []

        # Check every 3-metre interval from bottom to surface
        check_depth = round(depth_m / 3) * 3
        while check_depth > self.safety_stop_depth:
            p_amb = self._depth_to_pressure(check_depth)
            if self._any_tissue_exceeds_m_value(p_amb):
                stop_time = self._required_stop_time(check_depth)
                stops.append((float(check_depth), stop_time))
            check_depth -= 3

        # Always append mandatory safety stop
        stops.append((self.safety_stop_depth, self.safety_stop_duration))
        return stops

    # ------------------------------------------------------------------
    # Safety-stop enforcement with timer
    # ------------------------------------------------------------------

    def enforce_safety_stop(self, on_complete=None):
        """Start a countdown timer for the safety stop.

        Args:
            on_complete: Optional callable invoked when the stop finishes.
        """
        if self._stop_timer is not None and self._stop_timer.is_alive():
            return  # already running

        self._on_stop_complete_cb = on_complete
        self._stop_completed = False
        self._stop_start_time = time.monotonic()
        duration_sec = self.safety_stop_duration * 60.0

        print(
            f"Safety stop required at {self.safety_stop_depth:.0f} m "
            f"for {self.safety_stop_duration:.0f} min."
        )

        self._stop_timer = threading.Timer(duration_sec, self._on_timer_expired)
        self._stop_timer.daemon = True
        self._stop_timer.start()

    def stop_timer_remaining(self) -> float:
        """Return seconds remaining on the safety-stop timer (0 if done/not started)."""
        if self._stop_start_time is None or self._stop_completed:
            return 0.0
        elapsed = time.monotonic() - self._stop_start_time
        remaining = self.safety_stop_duration * 60.0 - elapsed
        return max(0.0, remaining)

    def cancel_safety_stop(self):
        """Abort the safety-stop timer (e.g. on emergency ascent)."""
        if self._stop_timer is not None:
            self._stop_timer.cancel()
            self._stop_timer = None
        self._stop_completed = False
        self._stop_start_time = None

    def is_stop_completed(self) -> bool:
        return self._stop_completed

    def is_safe_to_ascend(self, current_depth_m: float) -> bool:
        """True when the diver is at or above safety-stop depth AND stop is done."""
        if current_depth_m <= self.safety_stop_depth:
            return self._stop_completed
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_timer_expired(self):
        self._stop_completed = True
        print("Safety stop completed. Safe to continue ascent.")
        if self._on_stop_complete_cb:
            self._on_stop_complete_cb()

    def _depth_to_pressure(self, depth_m: float) -> float:
        """Convert depth to absolute pressure in bar (fresh water ≈ sea water for diving)."""
        return self.SURFACE_PRESSURE_BAR + depth_m / 10.0

    def _any_tissue_exceeds_m_value(self, ambient_pressure: float) -> bool:
        for i, tp in enumerate(self.tissue_pressures):
            m_value = self.M_VALUES_A[i] + ambient_pressure * self.M_VALUES_B[i]
            if tp > m_value:
                return True
        return False

    def _required_stop_time(self, depth_m: float) -> float:
        """Simplified stop-time calculation (returns 5 min minimum per stop)."""
        return 5.0


# Example usage:
# manager = DecompressionManager()
# stops = manager.calculate_stops(30, 20)
# for depth, duration in stops:
#     print(f"Stop at {depth}m for {duration}min")
# manager.enforce_safety_stop()
