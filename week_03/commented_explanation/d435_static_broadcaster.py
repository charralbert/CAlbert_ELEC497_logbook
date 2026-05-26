#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import tf2_ros
import geometry_msgs.msg
import numpy as np

# this class is a ROS node
class StaticTransformPublisher(Node):
    def __init__(self):

        # creates a ROS node named static_transform_cam_broadcaster
        # super() is used to call the constructor of the parent class (Node) and initialize the node with the specified name
        super().__init__('static_transform_cam_broadcaster')

        # tf_broadcaster: an object that can publish transforms on behalf of this node
        self.tf_broadcaster = tf2_ros.StaticTransformBroadcaster(self)

    def publish_transform(self):

        # Defines an edge in the TF tree: world -> camera_frame

        # A TF message with: header containing timestamp, parent frame name, child frame name, translation, and rotation
        static_transformStamped = geometry_msgs.msg.TransformStamped()
        # the time associated with the transform
        static_transformStamped.header.stamp = self.get_clock().now().to_msg()
        # parent
        static_transformStamped.header.frame_id = "world"
        # child - defined relative to world
        static_transformStamped.child_frame_id = "camera_frame"
        # TF interprets the translation and rotation as: if you are standing in world,
        # how do you locate and orient the camera_frame origin

        # Define the transformation from the camera's reference frame to the robot's reference frame
        # This could be a transformation matrix
        translation = geometry_msgs.msg.Vector3(x=0.173, y=-0.332, z=0.075)
        # was translation = geometry_msgs.msg.Vector3(x=0.14, y=-0.285, z=0.075)
        # same rotation since I switched the y-axis
        rotation = geometry_msgs.msg.Quaternion(x=0.0, y=-0.6755902, z=0.7372773, w=0.0)

        # attach translation and rotation to the message
        static_transformStamped.transform.translation = translation
        static_transformStamped.transform.rotation = rotation

        # publish: sends the transform into the TF system on /tf_static topic
        self.tf_broadcaster.sendTransform(static_transformStamped)

def main(args=None):
    # start the ROS2 python client library: connects the process to the ROS graph
    rclpy.init(args=args)

    # create Node object
    static_publisher = StaticTransformPublisher()

    # while ROS "healthy"
    while rclpy.ok():
        # every loop pass re-broadcasts: camera is here relative to world, however
        # for a static transform - usually once is enough, repeating is harmless
        static_publisher.publish_transform()
        # processes ROS events for one step
        rclpy.spin_once(static_publisher)

    static_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
