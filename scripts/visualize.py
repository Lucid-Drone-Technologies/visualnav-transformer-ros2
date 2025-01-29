import numpy as np
import cv2
import rclpy
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray
from cv_bridge import CvBridge

from visualnav_transformer.deployment.src.topic_names import (
    IMAGE_TOPIC,
    SAMPLED_ACTIONS_TOPIC,
)

data = []

img = np.zeros((100, 100, 3), dtype=np.uint8)  # Ensure dtype is uint8 for visualization
bridge = CvBridge()

def camera_callback(msg):
    global img
    img = bridge.imgmsg_to_cv2(msg)

def callback(msg, publisher):
    global img
    actions = msg.data
    actions = np.array(actions)[1:].reshape(-1, 2)
    actions = actions * img.shape[0] / 20
    actions[:, 1] = actions[:, 1] - img.shape[1] // 2
    actions[:, 0] = actions[:, 0] - img.shape[0]
    data = actions

    # Create a visualization using OpenCV
    visualized_img = img.copy()
    
    # Draw all trajectories in green first
    for i in range(8, len(data), 8):  # Start from second trajectory (index 8)
        points = (-data[i:i+8, 1].astype(int), -data[i:i+8, 0].astype(int))
        points = np.array(list(zip(*points)), dtype=np.int32)
        cv2.polylines(visualized_img, [points], isClosed=False, color=(0, 255, 0), thickness=2)
    
    # Draw the selected trajectory (first one) in red
    selected_points = (-data[0:8, 1].astype(int), -data[0:8, 0].astype(int))
    selected_points = np.array(list(zip(*selected_points)), dtype=np.int32)
    cv2.polylines(visualized_img, [selected_points], isClosed=False, color=(0, 0, 255), thickness=3)
    
    # Highlight the chosen waypoint with a circle
    waypoint_idx = 2  # This should match the default waypoint index from explore.py
    chosen_point = (-int(data[waypoint_idx, 1]), -int(data[waypoint_idx, 0]))
    cv2.circle(visualized_img, chosen_point, radius=5, color=(255, 0, 0), thickness=-1)

    # Convert visualization to ROS 2 Image message and publish
    image_msg = bridge.cv2_to_imgmsg(visualized_img, encoding="bgr8")
    publisher.publish(image_msg)

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('sampled_actions_subscriber')
    camera_subscriber = node.create_subscription(Image, IMAGE_TOPIC, camera_callback, 10)

    publisher = node.create_publisher(Image, 'visualize_output', 10)
    subscriber = node.create_subscription(
        Float32MultiArray,
        SAMPLED_ACTIONS_TOPIC,
        lambda msg: callback(msg, publisher),
        1
    )
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
