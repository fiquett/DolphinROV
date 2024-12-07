# ROS Integration

The ROS (Robot Operating System) framework is used to manage communication between DolphinROV's systems, sensors, and AI modules. This integration ensures modularity, scalability, and real-time control.

## Features
- **Sensor Nodes**: Publish real-time data from sensors (e.g., sonar, depth).
- **Effector Nodes**: Control actuators (e.g., thrusters, manipulators).
- **AI Integration**: Leverage ROS topics and services for AI-driven decision-making.

## Core Nodes
1. **Navigation Node**: Processes sensor data and generates movement commands.
2. **Communication Node**: Manages data exchange via JANUS and RF protocols.
3. **AI Node**: Coordinates actions based on mission objectives and diver inputs.

## Getting Started
1. Install ROS 2 on your system.
2. Clone this repository and navigate to the `software/ros_integration/` folder.
3. Build the workspace:
   ```bash
   colcon build
   source install/setup.bash
   ```
4. Launch the system:
   ```bash
   ros2 launch dolphinrov_system launch_all.launch.py
   ```
