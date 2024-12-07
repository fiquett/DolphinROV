import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class NavigationNode(Node):
    def __init__(self):
        super().__init__('navigation_node')
        self.publisher_ = self.create_publisher(String, 'navigation_status', 10)
        self.timer = self.create_timer(2.0, self.publish_navigation_status)

    def publish_navigation_status(self):
        message = String()
        message.data = 'Current status: Moving to destination.'
        self.publisher_.publish(message)
        self.get_logger().info('Publishing navigation status: "%s"' % message.data)

def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
