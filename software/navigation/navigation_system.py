# Navigation System

class NavigationSystem:
    def __init__(self):
        self.current_location = (0, 0, 0)  # x, y, z coordinates
        self.destination = None

    def update_location(self, location):
        self.current_location = location
        print(f"Current location updated to: {self.current_location}")

    def set_destination(self, destination):
        self.destination = destination
        print(f"Destination set to: {self.destination}")

    def navigate_to_destination(self):
        if self.destination:
            print(f"Navigating from {self.current_location} to {self.destination}")
            # Add navigation logic such as pathfinding algorithms
        else:
            print("No destination set.")

# Example usage:
# nav = NavigationSystem()
# nav.set_destination((10, 20, -5))
# nav.navigate_to_destination()
