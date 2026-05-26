#!/usr/bin/env python3
import sys
import os
import rclpy
from rclpy.node import Node
from nuitrack_skeleton.msg import Skeleton
from geometry_msgs.msg import PointStamped, Point
import tf2_ros
import tf2_geometry_msgs
import math
from pynput import keyboard
import sqlite3
import numpy as np
import time
import socket
import pickle
import random
from copy import copy
from ruckig import InputParameter, OutputParameter, Result, Ruckig

from UR_Kinematics import inverse_kinematic_solution, forward_kinematic_solution, DH_matrix_UR5e


ROBOT_IP = '192.168.1.102'
HOST = '192.168.1.101' # Your CPC IP. If you don't have a divided control pc, it should be your computer ip.
PORT = 50002
Node.bool = 1

# ROS2 node
class SkeletonSubscriber(Node):
    Node.amplitude = 0.01
    Node.frequency = 0.2
    
    def __init__(self):
        # node name
        super().__init__('skeleton_subscriber')
        # subscriber to "nuitrack_topic"
        self.subscription = self.create_subscription(
            Skeleton,
            'nuitrack_topic',
            self.listener_callback,
            10)
        
        # Initialize the database connection
        self.con = sqlite3.connect("scores.db")
        self.cur = self.con.cursor()
        self.position_array = [[] for _ in range(6)]
        self.current_id = 1
        self.prev_id = None

        # current robot joints (read later from shared_data.db)
        self.current_positions = None

        # TF mechanism, allows you to ask: give me the transform from the camera frame to world, then apply to head point
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.new_target = [0]*6
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
            self.get_logger().info("Socket connection established")
        except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
            self.get_logger().error(f"Failed to connect to server: {e}")

        # Variable to store the highest score skeleton ID
        self.highest_score_id = 1
        self.highest_attention_score = 0.0
        self.length = None
        self.count = time.time()

        # joint configuration in the UR order
        self.robot_startposition = (math.radians(-76.57),
                    math.radians(-54.83),
                    math.radians(-93.14),
                    math.radians(-32.59),
                    math.radians(79.27),
                    math.radians(0))


    def listener_callback(self, msg):
        # Check if the message's skeleton ID matches the highest score skeleton ID
        # robot onlu attends to the person with the highest score
        if msg.user_id == self.highest_score_id:
            # self.get_logger().info(f'Received skeleton data for the highest score ID: {msg.user_id}')
            head_point = msg.head
                
            try:
                # convert the head point to world coordinates
                transform = self.tf_buffer.lookup_transform(
                    'world',
                    head_point.header.frame_id,
                    rclpy.time.Time())
                head_point = tf2_geometry_msgs.do_transform_point(head_point, transform)  

                # if tracked person changes, calculate new trajectory to transition to the new target   
                if self.highest_score_id != self.prev_id:
                    self.new_target = self.Track_New_User(head_point)
                    self.calculate_trajectory(self.current_positions, self.new_target, [1,1,1,1,1,1], [1,1,1,1,1,1], [2,2,2,2,2,2], [2,2,2,2,2,2], [1,1,1,1,1,1])
                    self.length = len(self.position_array[0]) # number of rows i think?
                    for i in range(self.length):
                        #self.send_target("transition", [self.position_array[0][i], self.position_array[1][i], self.position_array[2][i], self.position_array[3][i], self.position_array[4][i], self.position_array[5][i]])
                        print("gotta add stuff here")
                self.calc_ee_target(head_point)  
            except Exception as e:
                self.get_logger().error(f"Failed to transform point: {str(e)}")

        else:
            self.get_logger().info(f'Ignoring skeleton data for ID: {msg.user_id}')
        

    # the head tracking math, converts a 3D head point into a robot "look-at" TCP target
    # input: tracking_point is a PointStamped in world (has x,y,z)
    # output: 6 number list [x,y,z,rx,ry,rz] that is the target pose for the robot's end effector to look at the head
    def calc_ee_target(self, tracking_point):

        # Position mapping
        # y: clamps/warps head coordinates into safe robot workspace (-0.6 to -0.3) or linear function
        print("in ee target")
        print(tracking_point.point.x)
        if tracking_point.point.y < -5.00:
            ee_y = -0.600
        elif tracking_point.point.y > -1.50:
            ee_y = -0.300
        else:
            ee_y = (tracking_point.point.y*0.3)/3.5 - 0.17143

        # x: scale by 0.15, clamp to +/- 0.15
        # rz: using atan to yaw toward the person
        if tracking_point.point.x < 1.0 and tracking_point.point.x > -1.0:
            ee_x = 0.15*tracking_point.point.x
            ee_rz = -2*math.atan((tracking_point.point.x - ee_x)/tracking_point.point.y)
        elif tracking_point.point.x >= 1.0:
            ee_x = 0.15
            ee_rz = -2*math.atan((tracking_point.point.x - 0.15)/tracking_point.point.y)
        else:
            ee_x = -0.15
            ee_rz = -2*math.atan((tracking_point.point.x + 0.15)/tracking_point.point.y)

        # z: linear function
        # rx: using atan to tilt toward head height
        if tracking_point.point.z < 0.9 and tracking_point.point.z > 0.4: 
            ee_z = 0.4*tracking_point.point.z + 0.52
            ee_rx = math.atan((tracking_point.point.z - ee_z)/tracking_point.point.y)
        elif tracking_point.point.z >= 0.9: 
            ee_z = 0.88
            ee_rx = math.atan((tracking_point.point.z - 0.88)/tracking_point.point.y) 
        else: 
            ee_z = 0.68
            ee_rx = math.atan((tracking_point.point.z - 0.68)/tracking_point.point.y)


        current_time = time.time()
        if self.highest_attention_score > 0.9:
            Node.frequency = 0.6
            Node.amplitude = 0.02
            self.count = time.time()
        elif self.highest_attention_score < 0.9 and time.time() - self.count > 5:
            Node.amplitude = 0.01
            Node.frequency = 0.2
        
        # add small oscillations, changes amplitude/frequency based on attention score
        sinusoidal_term = Node.amplitude*math.sin(2*math.pi*Node.frequency*current_time)
        cos_term = Node.amplitude/1.7*math.cos(2*math.pi*(Node.frequency - 0.09)*current_time)
        
        self.send_target('ee_target', [ee_x + cos_term, ee_y, ee_z + sinusoidal_term, 1.5707963 + ee_rx, 0, ee_rz])
        


    def get_latest_attention_score(self, skel_id):
        try:
            self.cur.execute(
                "SELECT current_score, prev_score, attention_gradient FROM info WHERE skel_id=? ORDER BY rowid DESC LIMIT 1", 
                (skel_id,))
            row = self.cur.fetchone()
            if row:
                self.highest_attention_score = row[0]
                return {"current_score": row[0], "prev_score": row[1], "attention_gradient": row[2]}
            else:
                self.get_logger().info(f"No data found for skel_id {skel_id}")
                return None
        except sqlite3.Error as e:
            self.get_logger().error(f"SQLite error during fetching data: {e}")
            return None

    def get_highest_score_skeleton_id(self):
        try:
            self.cur.execute(
                "SELECT skel_id FROM info ORDER BY current_score DESC LIMIT 1"
            )
            row = self.cur.fetchone()
            if row:
                skel_id = row[0]
                self.cur.execute(
                    "SELECT current_score FROM info WHERE skel_id=?", (skel_id,)
                )
                score = self.cur.fetchone()
                if score is None or score[0] == 0:
                    self.get_logger().info("No data found in the database.")
                    return None
                if self.highest_score_id != None:
                    self.prev_id = self.current_id
                return skel_id
            else:        #made a change to the code here, gonna check about how we can check for people.
                self.get_logger().info("No data found in the database.")
                return None
        except sqlite3.Error as e:
            self.get_logger().error(f"SQLite error during fetching data: {e}")
            return None
        
    def send_target(self,message_type,data):
        try:
            if message_type == 'ee_target':
                packed_data = pickle.dumps(data) # No data to send
            if message_type == 'headspin':
                packed_data = pickle.dumps(data)
            if message_type == 'breathe':
                packed_data = pickle.dumps(data)
            if message_type == 'home':
                packed_data = pickle.dumps(data)
            if message_type == 'transition':
                packed_data = pickle.dumps(data)
                
            # first 10: message type padded, then payload length padded, then payload
            message_header = f"{message_type:<10}{len(packed_data):<10}".encode('utf-8')
            self.socket.sendall(message_header + packed_data)
            
        except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
            print(f'Failed to connect to server: {e}. Retrying in 5 seconds...')
            time.sleep(1)
            return
    def send_movement(self, message_type):
        try:    
            message_header = f"{message_type:<10}".encode('utf-8')
            self.socket.sendall(message_header)
            
        except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
            print(f'Failed to connect to server: {e}. Retrying in 5 seconds...')
            time.sleep(1)
            return
    
        
    def receive_all(sock, n):
        """ Helper function to receive n bytes or return None if EOF is hit """
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    

    def isRotationMatrix(self, R) :
        Rt = np.transpose(R)
        shouldBeIdentity = np.dot(Rt, R)
        I = np.identity(3, dtype = R.dtype)
        n = np.linalg.norm(I - shouldBeIdentity)
        return n < 1e-6

    def rotationMatrixToEulerAngles(self, R) :
 
        assert(self.isRotationMatrix(R))
 
        sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
 
        singular = sy < 1e-6
 
        if  not singular :
            x = math.atan2(R[2,1] , R[2,2])
            y = math.atan2(-R[2,0], sy)
            z = math.atan2(R[1,0], R[0,0])
        else :
            x = math.atan2(-R[1,2], R[1,1])
            y = math.atan2(-R[2,0], sy)
            z = 0
 
        return np.array([x, y, z])

    # inpute: current position (6 joints) and target position (6 joints)
    # output: a time sequence of intermediate joint positions
    def calculate_trajectory(self, current_pos, target_pos, target_vel, target_accel, max_vel, max_accel, max_jerk):
        holder = [0]*6
        angles = [0]*3
        otg = Ruckig(6, 0.01)   #DOF'S and control cycle
        inp = InputParameter(6)
        out = OutputParameter(6)

        inp.current_position = current_pos
        inp.current_velocity = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] #add accurate velocity and acceleration for joints later
        inp.current_acceleration = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        inp.target_position = target_pos
        inp.target_velocity = target_vel
        inp.target_acceleration = target_accel

        inp.max_velocity = max_vel
        inp.max_acceleration = max_accel
        inp.max_jerk = max_jerk

        first_output, out_list = None, []
        res = Result.Working
        for i in range(6):
            self.position_array[i].clear()

        while res == Result.Working:
            res = otg.update(inp, out)

            out_list.append(copy(out))
            #put outputs into an array that is held in the node
            for j in range(6):
                self.position_array[j].append(out.new_position[j]) 
            out.pass_to_input(inp)

            if not first_output:
                first_output = copy(out)
        length = len(self.position_array[0]) #count of columns

        # After Ruckig generates joint waypoints:
        for i in range(length):
            # FK converts joint angles to 4x4 transform -> tool position/orientation
            # stores xyz and Euler-ish angles into position array
            holder = forward_kinematic_solution(DH_matrix_UR5e, [self.position_array[0][i], self.position_array[1][i], self.position_array[2][i], self.position_array[3][i], self.position_array[4][i], self.position_array[5][i]])
            threebythree = holder[:3, :3]
            angles = self.rotationMatrixToEulerAngles(threebythree)
            xyz = holder[:3, 3]
            for j in range(3):
                self.position_array[j][i] = xyz[j]
                self.position_array[j+3][i] = angles[j]
            if i == length - 1:
                print(angles)
                print(holder)
            
                
            

    def update_positions(self, pos):
        self.current_positions = pos

    # builds a desired transform matrix from the head point
    def Track_New_User (self, tracking_point):
        if tracking_point.point.y < -5.00:
            ee_y = -0.600
        elif tracking_point.point.y > -1.50:
            ee_y = -0.300
        else:
            ee_y = (tracking_point.point.y*0.3)/3.5 - 0.17143

        if tracking_point.point.x < 1.0 and tracking_point.point.x > -1.0:
            ee_x = 0.15*tracking_point.point.x
            ee_rz = -2*math.atan((tracking_point.point.x - ee_x)/tracking_point.point.y)
        elif tracking_point.point.x >= 1.0:
            ee_x = 0.15
            ee_rz = -2*math.atan((tracking_point.point.x - 0.15)/tracking_point.point.y)
        else:
            ee_x = -0.15
            ee_rz = -2*math.atan((tracking_point.point.x + 0.15)/tracking_point.point.y)

        if tracking_point.point.z < 0.9 and tracking_point.point.z > 0.4: 
            ee_z = 0.4*tracking_point.point.z + 0.52
            ee_rx = math.atan((tracking_point.point.z - ee_z)/tracking_point.point.y)
        elif tracking_point.point.z >= 0.9: 
            ee_z = 0.88
            ee_rx = math.atan((tracking_point.point.z - 0.88)/tracking_point.point.y) 
        else: 
            ee_z = 0.68
            ee_rx = math.atan((tracking_point.point.z - 0.68)/tracking_point.point.y)
        transform = np.matrix ([[1.00000000e+00, 0.00000000e+00, 0.00000000e+00, ee_x],
                                [0.00000000e+00, 0.00000000e+00, -1.00000000e+00, ee_y],
                                [0.00000000e+00, 1.00000000e+00, 0.00000000e+00, ee_z],
                                [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
        
        # IK converts the desired tool transform into joint angles, which are sent as the new target
        IKS = inverse_kinematic_solution(DH_matrix_UR5e, transform)
        joint__positions = [round(IKS[j, 0], 2) for j in range(6)] #change the index in the array in the future to change the elbow position from being up or from being down
        return joint__positions
    

def main(args=None):
    rclpy.init(args=args)
    node = SkeletonSubscriber()
    past = None
    con2 = sqlite3.connect("shared_data.db")
    cur2 = con2.cursor()
    count = 1

    while rclpy.ok():
        # fetch the latest joint positions from the shared_data.db database
        cur2.execute('''SELECT value FROM data''')
        data = cur2.fetchall()
        positions = [row[0] for row in data] #for getting the angle of the arms joints
        amplitude = 0.001
        frequency = 0.2
        current_time = time.time()

        # let ROS handle callbacks (spin once)
        rclpy.spin_once(node, timeout_sec= 0.1)

        # Query attention DB to decide who to track
        highest_score_id = node.get_highest_score_skeleton_id()
        if highest_score_id is not None:
            latest_score = node.get_latest_attention_score(highest_score_id)
            #print("highest score found")
            if latest_score is not None:
                #print("latest score found")
                # node.get_logger().info(f"Highest score skeleton ID: {highest_score_id}, Score Data: {latest_score}")
                node.highest_score_id = highest_score_id  # Update the highest score ID

            count = 2
            node.update_positions(positions) #send into the node the positions of the joints
        
        # if nobody valid - breathe idle motion
        else:
            #print("in else statement")
            current_time = time.time()
            sinusoidal_term = amplitude*math.sin(2*math.pi*frequency*current_time)
            cos_term = amplitude/2.2*math.cos(2*math.pi*(frequency - 0.09)*current_time)
            node.send_target('breathe', [cos_term, sinusoidal_term])
            if count == 2:
                node.calculate_trajectory(positions, node.robot_startposition, [1,1,1,1,1,1], [1,1,1,1,1,1], [2,2,2,2,2,2], [2,2,2,2,2,2], [1,1,1,1,1,1])
                length = len(node.position_array[0])
                for i in range(length):
                    node.send_target('transition', (node.position_array[0][i], node.position_array[1][i],node.position_array[2][i],node.position_array[3][i],node.position_array[4][i],node.position_array[5][i],))
                count = 1
                

            
    
    node.destroy_node()
    rclpy.shutdown()
    node.cur.close()
    node.con.close()
    cur2.close()
    con2.close()

if __name__ == '__main__':
    main()

