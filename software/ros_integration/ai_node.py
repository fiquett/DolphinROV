import rclpy
from rclpy.node import Node

class AINode(Node):
    def __init__(self):
        super().__init__('ai_node')
        self.subscription = self.create_subscription(
            String,
            'navigation_topic',
            self.listener_callback,
            10)
        self.subscription

    def listener_callback(self, message):
        self.get_logger().info('AI received: "%s"' % message.data)

def main(args=None):
    rclpy.init(args=args)
    ai_node = AINode()
    rclpy.spin(ai_node)
    ai_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
