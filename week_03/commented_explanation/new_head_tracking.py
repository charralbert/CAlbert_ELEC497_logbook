#!/usr/bin/env python3
import URBasic
import math
import time
import numpy as np
import URBasic.urScript
import rclpy
from rclpy.node import Node
from nuitrack_skeleton.msg import Skeleton
from geometry_msgs.msg import PointStamped
import tf2_ros
import tf2_geometry_msgs
import threading
import sqlite3
import pathlib
from ruckig import InputParameter, OutputParameter, Result, Ruckig

ROBOT_IP = '192.168.1.102'
HOST = '192.168.1.101' # Your CPC IP. If you don't have a divided control pc, it should be your computer ip.
PORT = 50002

ACCELERATION = 0.5
VELOCITY = 0.5
AROUSAL = 1
alpha_idle = 0.3 + (0.7 - 0.3) * (AROUSAL - 1) / 9
alpha_active = 0.03 + (1.0 - 0.03) * (AROUSAL - 1) / 9
joint1_offset = -107.78 + 2.78 * AROUSAL
joint2_offset = -124.44 + 4.44 * AROUSAL
wrist_duration = 1.5 + (0.4 - 1.5) * (AROUSAL - 1) / 9 
idle_filter_alpha = 0.15 + (0.151 - 0.015 * (11 - AROUSAL)) * (AROUSAL - 1) / 9


robot_startposition = (math.radians(-85),
                    math.radians(-107.78 + 2.78*AROUSAL),
                    math.radians(-124.44 + 4.44*AROUSAL) ,
                    -3.14159 - math.radians(-107.78 + 2.78*AROUSAL) - math.radians(-124.44 + 4.44*AROUSAL),
                    math.radians(85),
                    math.radians(0))

DH1 = np.array([
    [0, 0.1625, 0, np.pi/2, 0],  # Joint 1
    [0, 0, -0.425, 0, 0],        # Joint 2
    [0, 0, -0.3922, 0, 0],       # Joint 3
    [0, 0.1333, 0, np.pi/2, 0],   # Joint 4
    [0, 0.0997, 0, 	-np.pi/2, 0], # Joint 5
    [0, 0.0996, 0, 0, 0]          # Joint 6
])

DH2 = np.array([
    [0, 0.1625, 0, np.pi/2, 0],  # Joint 1
    [0, 0, -0.425, 0, 0],        # Joint 2
    [0, 0, -0.3922, 0, 0],       # Joint 3
    [0, 0.1333, 0, np.pi/2, 0]   # Joint 4
])

class SkeletonSubscriber(Node):
    def __init__(self):
        super().__init__('skeleton_subscriber')
        self.subscription = self.create_subscription(
            Skeleton, 
            'nuitrack_topic',
            self.listener_callback, 
            10)
        
        robotModel = URBasic.robotModel.RobotModel()
        self.robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_IP,robotModel=robotModel)
        # self.robot.movej(q=robot_startposition, a= ACCELERATION, v= VELOCITY)
        self.robot.reset_error()
        self.head_point = None
        self.r = PointStamped()
        self.xfilter = PoseFilter(alpha=0.01 * AROUSAL * 0.5, start_pose=math.radians(-85))
        self.idle_betafilter = PoseFilter(alpha=alpha_idle, start_pose=0)
        self.idle_alphafilter = PoseFilter(alpha=alpha_idle, start_pose=0)
        self.betafilter = PoseFilter(alpha=alpha_active, start_pose=0)
        self.alphafilter = PoseFilter(alpha=alpha_active, start_pose=0)
        self.idlefilter = PoseFilter(alpha=idle_filter_alpha, start_pose=math.radians(-85))
        self.wrist_timer_start = None
        self.wrist_tracking_duration = wrist_duration
        self.last_message_time = time.time()
        self.non_callback_interval = 0.01
        self.in_no_message_state = True
        self.wrist_above_shoulder = False
        self.inp = self.out = self.otg = None

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.robot.init_realtime_control()

        self.execution_thread = threading.Thread(target=self.check_and_execute)
        self.execution_thread.daemon = True
        self.execution_thread.start()
        self.new_target = True
        self.first_pass = True
        
        # Add these new variables for tracking cooldown
        self.currently_tracked_id = None
        self.last_switch_time = 0
        self.switch_cooldown = 2.0  # 2 seconds cooldown
        
    def listener_callback(self, msg):
        highest_attention_id = get_highest_attention_score()
        
        if self.in_no_message_state:
            self.in_no_message_state = False
            self.first_pass = False
            self.xfilter.filtered_pose = self.robot.get_actual_joint_positions()[0] 
        self.last_message_time = time.time()
        current_time = time.time()
        should_switch = False
        if self.currently_tracked_id is None:
            should_switch = True
        elif not self.target_exists(self.currently_tracked_id):
            should_switch = True
        elif (current_time - self.last_switch_time >= self.switch_cooldown and 
              highest_attention_id != self.currently_tracked_id):
            should_switch = True

        if should_switch and highest_attention_id is not None:
            self.currently_tracked_id = highest_attention_id
            self.last_switch_time = current_time
            print(f"Switching to track ID: {self.currently_tracked_id}")

        tracking_point = PointStamped()
        
        # Handle virtual objects (IDs 11-100)
        if self.currently_tracked_id and 11 <= self.currently_tracked_id <= 100:
            try:
                db_path = str(pathlib.Path.home() / "ros2_ws" / "scores.db")
                with sqlite3.connect(db_path) as con:
                    cur = con.cursor()
                    cur.execute("SELECT target_x, target_y, target_z FROM info WHERE skel_id=?", 
                              (self.currently_tracked_id,))
                    row = cur.fetchone()
                    if row:
                        tracking_point.point.x = row[0]
                        tracking_point.point.y = row[1]
                        tracking_point.point.z = row[2]
                        tracking_point.header.frame_id = 'world'
            except sqlite3.Error as e:
                print(f"SQLite error while reading virtual object position: {e}")
                return
                
        # Handle physical objects (IDs 1-10)
        else:
            self.head_point = self.transform_point(msg.head)
            self.left_wrist = self.transform_point(msg.left_wrist)
            self.right_wrist = self.transform_point(msg.right_wrist)
            self.right_shoulder = self.transform_point(msg.right_shoulder)
            

            if (self.left_wrist.point.z > (self.right_shoulder.point.z + 0.15) or 
                    self.right_wrist.point.z > (self.right_shoulder.point.z + 0.15)):
                    if not self.wrist_above_shoulder:
                        self.wrist_above_shoulder = True
                        self.wrist_timer_start = time.time()
            else:
                self.wrist_above_shoulder = False

            if self.wrist_above_shoulder and time.time() - self.wrist_timer_start <= self.wrist_tracking_duration:
                tracking_point = self.left_wrist if self.left_wrist.point.z > self.right_wrist.point.z else self.right_wrist
            else:
                tracking_point = self.head_point

        self.inp = self.out = self.otg = None
        self.new_target = True

        joints = self.track_point(tracking_point) 
        
        # Add breathing offsets
        breathing_offset1, breathing_offset2 = self.calculate_breathing_offsets()
        joints[1] += breathing_offset1  # Add breathing to joint1
        joints[2] += breathing_offset2  # Add breathing to joint2
        
        self.robot.set_realtime_pose(joints)
        
        

    def track_point(self, tracking_point, flag=True):
        if tracking_point.point.x <= -2.00:
            joint0 = math.radians(-105)
        elif tracking_point.point.x >= 2.00:
            joint0 = math.radians(-65)
        else:
            joint0 = math.radians(-65 - (-tracking_point.point.x + 2.00)*10)
        
        
        if flag:
            joint0 = self.xfilter.apply_filter(joint0)
        else:
            joint0 = self.idlefilter.apply_filter(joint0)

        # Base joint angles that change with arousal
        joint1 = math.radians(-107.78 + 2.78*AROUSAL)
        joint2 = math.radians(-124.44 + 4.44*AROUSAL)
        
        
        depth_factor = 1 + (5 - 1) * (AROUSAL - 1) / 9  # Linearly scale from 1 to 5 as AROUSAL goes from 1 to 10
        if flag and hasattr(self, 'head_point') and self.head_point:  # Only adjust for depth when actively tracking
            # Normalize depth between -4.0 (forward) and -1.5 (back)
            normalized_depth = (self.head_point.point.y + 4.0) / 2.5  # Maps -4.0 to 0 and -1.5 to 1
            depth_adjustment = depth_factor * normalized_depth  # Removed the (1 - ) to invert behavior

            # Adjust joints for lean - positive joint1 leans back, negative joint2 leans forward
            joint1 += math.radians(depth_adjustment * 5)  # 5 degrees max forward tilt
            joint2 -= math.radians(depth_adjustment * 3)  # 3 degrees max forward bend
        
        joint3 = -3.14159 - joint1 - joint2
        joint4 = -joint0
        joint5 = 0
        joints = [joint0, joint1, joint2, joint3, joint4, joint5] 

        pose = fkin(np.eye(4), DH1, np.eye(4), joints)
        self.r.point.x = pose[0]
        self.r.point.y = pose[1]
        self.r.point.z = pose[2]

        x = tracking_point.point.x - self.r.point.x
        y = abs(tracking_point.point.y) - abs(self.r.point.y)
        z = tracking_point.point.z - self.r.point.z

        beta = math.atan(x/y) - 0.0436332
        alpha = math.atan(z/y) + 0.0436332
        if AROUSAL != 10:
            if flag:
                beta = self.betafilter.apply_filter(beta)
                alpha = self.alphafilter.apply_filter(alpha)
            else:
                beta = self.idle_betafilter.apply_filter(beta)
                alpha = self.idle_alphafilter.apply_filter(alpha)

        if self.first_pass:
            self.alphafilter.filtered_pose = alpha
            self.betafilter.filtered_pose = beta

        joints = [joint0, joint1, joint2, joint3+alpha, joint4+beta, joint5] 
        return joints
 

    def transform_point(self, point):
        """Helper function to transform a point to the 'world' frame."""
        try:
            transform = self.tf_buffer.lookup_transform('world', point.header.frame_id, rclpy.time.Time())
            return tf2_geometry_msgs.do_transform_point(point, transform)
        except Exception as e:
            self.get_logger().error(f"Failed to transform point: {str(e)}")
            return point  # Return original point in case of failure
        
    def check_and_execute(self):
        while True:
            # Check if more than 1.5 seconds have passed since the last message
            if time.time() - self.last_message_time > 1.5:
                if not self.in_no_message_state:
                    # Transition from message-receiving state to no-message state
                    #self.execute_transition_code()  # Execute the transition code
                    self.in_no_message_state = True  # Now in no-message state
                    self.current_id = None
                    self.first_pass = True

                # Execute non-callback code continuously in the no-message state
                self.execute_non_callback_code()
            
            time.sleep(self.non_callback_interval)

    def execute_non_callback_code(self):
        tracking_point = PointStamped()
        x_min = -3.0 + (-4.0 - (-3.0)) * (AROUSAL - 1) / 9
        x_max = 3.0 + (4.0 - 3.0) * (AROUSAL - 1) / 9
        y_min, y_max = -1.5, -5.0  # No change for Y range
        z_min = -1.5 + (-0.75 - (-1.5)) * (AROUSAL - 1) / 9
        z_max = 0.5 + (2.0 - 0.5) * (AROUSAL - 1) / 9

        # Set tracking_point with interpolated ranges
        tracking_point.point.x = np.random.uniform(x_min, x_max)
        tracking_point.point.y = np.random.uniform(y_min, y_max)
        tracking_point.point.z = np.random.uniform(z_min, z_max)
        
        
        last_update_time = time.time()

        current_q = list(self.robot.get_actual_tcp_pose())
        target_q = self.track_point(tracking_point, False)

        while self.in_no_message_state:  

            # Update the target pose every 3.5 seconds
            current_time = time.time()

            min_interval = 2.5 + (0.5 - 2.5) * (AROUSAL - 1) / 9
            max_interval = 10.0 + (2.0 - 10.0) * (AROUSAL - 1) / 9
            update_interval = np.random.uniform(min_interval, max_interval)
            if current_time - last_update_time > (update_interval):
                tracking_point.point.x = np.random.uniform(x_min, x_max)
                tracking_point.point.y = np.random.uniform(y_min, y_max)
                tracking_point.point.z = np.random.uniform(z_min, z_max)
                target_q = self.track_point(tracking_point, False)
                last_update_time = current_time
                self.new_target = True

            current_q = list(self.robot.get_actual_joint_positions())

            # Calculate the next step in the trajectory
            next_step = self.calculate_trajectory(
                current_q,        # Current position
                target_q,         # Target position
                [0, 0, 0, 0, 0, 0], # Target velocity
                [0, 0, 0, 0, 0, 0], # Target acceleration
                [0.1,0.1,0.1,60 - (10 - AROUSAL)*6 , 60 - (10 - AROUSAL)*6, 1], # Max velocity
                [1,1,1,160 - (10 - AROUSAL)*15 , 160 - (10 - AROUSAL)*15 ,1], # Max acceleration
                [5,5,5,500 - (10 - AROUSAL)*25 , 500 - (10 - AROUSAL)*25, 1] # Max jerk
            )
            
            breathing_offset1, breathing_offset2 = self.calculate_breathing_offsets()
            
            self.robot.set_realtime_pose([
                next_step.new_position[0], 
                next_step.new_position[1] + breathing_offset1, 
                next_step.new_position[2] + breathing_offset2, 
                next_step.new_position[3], 
                next_step.new_position[4], 
                next_step.new_position[5],
                0
            ])

            # Sleep for 10ms before calculating the next step
            #time.sleep(0.01)

    def calculate_trajectory(self, current_pos, target_pos, target_vel, target_accel, max_vel, max_accel, max_jerk):
        if self.inp == None:
            self.inp = InputParameter(6)
            self.inp.current_position = current_pos

        if self.out == None:
            self.out = OutputParameter(6)

        if self.otg == None:
            self.otg = Ruckig(6, 0.01)

        if self.new_target:
            min_duration = 4.5 + (0 - 4.5) * (AROUSAL - 1) / 9
            max_duration = 6.3 + (0.01 - 6.3) * (AROUSAL - 1) / 9
            duration = np.random.uniform(min_duration, max_duration)

            self.inp.target_position = target_pos
            self.inp.target_velocity = target_vel
            self.inp.target_acceleration = target_accel
            self.inp.minimum_duration = duration
            self.inp.max_velocity = max_vel
            self.inp.max_acceleration = max_accel
            self.inp.max_jerk = max_jerk
            self.new_target = False

        res = self.otg.update(self.inp, self.out)

        if res == Result.Error:
            print("Error in trajectory generation!")
            return None

        self.out.pass_to_input(self.inp)

        return self.out

    def interpolate_pose(self, start_pose, target_pose, progress):
        """Linear interpolation for a given progress (0.0 to 1.0)."""
        return [
            start + progress * (target - start)
            for start, target in zip(start_pose, target_pose)
        ]

    def calculate_breathing_offsets(self):
        breathing_freq = 0.05 + (0.1 * AROUSAL/3)
        breathing_amp1 = math.radians(0.75)
        breathing_amp2 = math.radians(1.00)
        breathing_offset1 = breathing_amp1 * math.cos(2 * math.pi * breathing_freq * time.time())
        breathing_offset2 = breathing_amp2 * math.cos(2 * math.pi * breathing_freq * time.time())
        return breathing_offset1, breathing_offset2
    
    def target_exists(self, target_id):
        """Check if target_id still exists in the database"""
        try:
            db_path = str(pathlib.Path.home() / "ros2_ws" / "scores.db")
            with sqlite3.connect(db_path) as con:
                cur = con.cursor()
                cur.execute("SELECT skel_id FROM info WHERE skel_id=?", (target_id,))
                return cur.fetchone() is not None
        except sqlite3.Error as e:
            print(f"SQLite error while checking target existence: {e}")
            return False

def fkin(Tbase, dh, Ttool, q):
    # Number of joints and elements in the DH chain
    n = min(dh.shape[0], len(q))

    # Start at the base
    T = Tbase

    # Proceed down the DH chain
    for i in range(n):
        # Pull out the DH values and precompute the sine/cosine terms
        if dh[i, 4] == 1:
            # Prismatic
            stheta = np.sin(dh[i, 0])
            ctheta = np.cos(dh[i, 0])
            d = dh[i, 1] + q[i]
        else:
            # Revolute
            stheta = np.sin(dh[i, 0] + q[i])
            ctheta = np.cos(dh[i, 0] + q[i])
            d = dh[i, 1]
        
        a = dh[i, 2]
        salpha = np.sin(dh[i, 3])
        calpha = np.cos(dh[i, 3])

        # Create the transformation matrix
        T = T @ np.array([
            [ctheta, -stheta*calpha, stheta*salpha, a*ctheta],
            [stheta,  ctheta*calpha, -ctheta*salpha, a*stheta],
            [0,       salpha,         calpha,        d],
            [0,       0,              0,             1]
        ])

    # Finally, add the tool transform
    T = T @ Ttool

    # Extract the position (x, y, z)
    
    x = T[0, 3]
    y = T[1, 3]
    z = T[2, 3]

    return [x, y, z]

class PoseFilter:
    def __init__(self, alpha=0.1, start_pose = None):
        self.alpha = alpha
        self.filtered_pose = start_pose

    def apply_filter(self, current_pose):
        if self.filtered_pose is None:
            # Initialize the filtered pose with the first pose
            self.filtered_pose = current_pose
        else:
            # Apply the exponential moving average filter for a single float
            self.filtered_pose = self.alpha * current_pose + (1 - self.alpha) * self.filtered_pose
        return self.filtered_pose
    

def get_highest_attention_score():
    try:
        db_path = str(pathlib.Path.home() / "ros2_ws" / "scores.db")
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT skel_id, current_score FROM info ORDER BY current_score DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                #print(f"Skeleton ID with highest attention score: {row[0]} (score: {row[1]})")
                return row[0]
            return None
    except sqlite3.Error as e:
        print(f"SQLite error while reading the highest score: {e}")
        return None
    
    
def main(args=None):
    rclpy.init(args=args)
    node = SkeletonSubscriber()
    node.robot.init_realtime_control()

    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec= 0.1)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()