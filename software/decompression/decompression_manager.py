# Decompression Manager

class DecompressionManager:
    def __init__(self):
        self.ascent_rate = 10  # meters per minute
        self.safety_stop_depth = 5  # meters
        self.safety_stop_duration = 3  # minutes

    def calculate_stops(self, depth, duration):
        stops = []
        current_depth = depth
        while current_depth > self.safety_stop_depth:
            next_stop = max(current_depth - self.ascent_rate, self.safety_stop_depth)
            stops.append(next_stop)
            current_depth = next_stop
        return stops

    def enforce_safety_stop(self):
        print(f"Safety stop required at {self.safety_stop_depth} meters for {self.safety_stop_duration} minutes.")
        # Implement timer or alert logic

# Example usage:
# manager = DecompressionManager()
# print(manager.calculate_stops(30, 20))
