# AI Decision Engine — rule-based state machine for DolphinROV

from typing import Any, Dict, Optional


class DecisionEngine:
    """Rule-based decision engine with a finite-state machine.

    States
    ------
    IDLE            ROV is stationary, awaiting commands.
    NAVIGATING      ROV is following a planned path to a destination.
    ASSISTING_DIVER ROV has detected a diver signal and is rendering aid.
    EXPLORING       ROV is running an autonomous survey pattern.
    EMERGENCY_ASCENT ROV is executing an emergency controlled ascent.

    Input keys (all optional, safe defaults applied)
    -------------------------------------------------
    depth_m     Current depth in metres (float).
    air_bar     Remaining tank pressure in bar (float).
    nav_status  "NAVIGATING" | "ARRIVED" | "IDLE" (str).
    diver_signal "NEED_HELP" | "OK" | None.
    obstacle    True if a collision-avoidance obstacle was detected.
    """

    STATES = frozenset(
        ["IDLE", "NAVIGATING", "ASSISTING_DIVER", "EXPLORING", "EMERGENCY_ASCENT"]
    )

    # Safety thresholds
    MIN_AIR_BAR: float = 50.0    # emergency ascent below this
    WARN_AIR_BAR: float = 80.0   # low-air warning
    MAX_DEPTH_M: float = 40.0    # emergency ascent above this depth

    def __init__(self):
        self.state: str = "IDLE"
        self._last_decision: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def make_decision(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate sensor inputs and return an action dict.

        Returns
        -------
        dict with keys:
            action  — string command for the ROV (e.g. "ASCEND", "NAVIGATE")
            reason  — human-readable explanation
            state   — new state after this decision
            alerts  — list of advisory strings (may be empty)
        """
        depth: float = float(inputs.get("depth_m", 0.0))
        air: float = float(inputs.get("air_bar", 200.0))
        nav_status: str = str(inputs.get("nav_status", "IDLE"))
        diver_signal: Optional[str] = inputs.get("diver_signal")
        obstacle: bool = bool(inputs.get("obstacle", False))

        alerts = []
        if air <= self.WARN_AIR_BAR:
            alerts.append(f"Low air warning: {air:.0f} bar remaining")

        # --- Emergency conditions (highest priority) ---
        if air < self.MIN_AIR_BAR:
            return self._transition(
                "EMERGENCY_ASCENT",
                "ASCEND",
                f"Air critically low ({air:.0f} bar < {self.MIN_AIR_BAR} bar)",
                alerts,
            )

        if depth > self.MAX_DEPTH_M:
            return self._transition(
                "EMERGENCY_ASCENT",
                "ASCEND",
                f"Depth limit exceeded ({depth:.1f}m > {self.MAX_DEPTH_M}m)",
                alerts,
            )

        # --- Diver assistance ---
        if diver_signal == "NEED_HELP":
            return self._transition(
                "ASSISTING_DIVER",
                "ASSIST",
                "Diver distress signal received",
                alerts,
            )

        # --- Obstacle avoidance ---
        if obstacle:
            alerts.append("Obstacle detected — replanning path")
            return self._transition(
                self.state,
                "REPLAN",
                "Obstacle in current path",
                alerts,
            )

        # --- Normal navigation ---
        if nav_status == "NAVIGATING":
            return self._transition("NAVIGATING", "CONTINUE", "On course", alerts)

        if nav_status == "ARRIVED":
            return self._transition("IDLE", "HOLD", "Destination reached", alerts)

        # --- Default: idle ---
        return self._transition("IDLE", "IDLE", "Awaiting commands", alerts)

    def execute_task(self, task: str) -> str:
        """Dispatch a task string to the appropriate handler.

        Returns a status message string.
        """
        handlers = {
            "ASCEND": self._handle_ascent,
            "ASSIST": self._handle_assist,
            "NAVIGATE": self._handle_navigate,
            "CONTINUE": self._handle_continue,
            "HOLD": self._handle_hold,
            "REPLAN": self._handle_replan,
            "IDLE": self._handle_idle,
        }
        handler = handlers.get(task.upper())
        if handler:
            result = handler()
            print(f"Executing task '{task}': {result}")
            return result
        print(f"Unknown task: {task}")
        return f"Unknown task: {task}"

    # ------------------------------------------------------------------
    # Task handlers
    # ------------------------------------------------------------------

    def _handle_ascent(self) -> str:
        return "Initiating controlled emergency ascent at ≤10 m/min"

    def _handle_assist(self) -> str:
        return "Moving to diver position to render assistance"

    def _handle_navigate(self) -> str:
        return "Resuming navigation to destination"

    def _handle_continue(self) -> str:
        return "Continuing along current path"

    def _handle_hold(self) -> str:
        return "Holding position at current coordinates"

    def _handle_replan(self) -> str:
        return "Replanning path around detected obstacle"

    def _handle_idle(self) -> str:
        return "ROV idle — no active task"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _transition(
        self, new_state: str, action: str, reason: str, alerts: list
    ) -> Dict[str, Any]:
        if new_state not in self.STATES:
            raise ValueError(f"Invalid state: {new_state}")
        self.state = new_state
        decision = {
            "action": action,
            "reason": reason,
            "state": self.state,
            "alerts": alerts,
        }
        self._last_decision = decision
        return decision


# Example usage:
# engine = DecisionEngine()
# decision = engine.make_decision({"depth_m": 20, "air_bar": 45})
# engine.execute_task(decision["action"])
