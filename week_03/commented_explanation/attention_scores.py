#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nuitrack_skeleton.msg import Skeleton
from geometry_msgs.msg import PointStamped, Point
import tf2_ros
import tf2_geometry_msgs
import math
from pynput import keyboard
import sqlite3
import random
import time
import threading
import os
import pathlib

# Define the database path
DB_PATH = str(pathlib.Path.home() / "ros2_ws" / "scores.db")

# Configuration flags at the top of the file
ENABLE_VIRTUAL_OBJECTS = True  # Set to False to disable virtual object creation

#SQLite Functions ------------------------------------------------------------------------------
def data_entry(value, prev, table):
    #simply insert the current attention score into the table thats already been created
    table_name = f'"ID_{table}"'
    cur.execute(f"INSERT INTO {table_name} (current_score, prev_score) VALUES (?, ?)", (value, prev,))
    con.commit()

#call if you want to delete an SQLite table
def delete_table():
    cur.execute("DROP TABLE IF EXISTS info")
    # Recreate the table with the new schema
    create_table()

def get_latest_attention_score(skel_id):
    try:
        cur.execute("SELECT current_score, prev_score, attention_gradient FROM info WHERE skel_id=? ORDER BY rowid DESC LIMIT 1", (skel_id,))
        row = cur.fetchone()
        if row:
            return {"current_score": row[0], "prev_score": row[1], "attention_gradient": row[2]}
        else:
            print(f"No data found for skel_id {skel_id}")
            return None
    except sqlite3.Error as e:
        print(f"SQLite error during fetching data: {e}")
        return None


#function wont do anything if these tables already exist
def create_table():
    # First drop the existing table
    cur.execute('DROP TABLE IF EXISTS info')
    
    # Create the new table with all columns
    cur.execute('''CREATE TABLE IF NOT EXISTS info(
        skel_id REAL, 
        current_score REAL, 
        prev_score REAL, 
        attention_gradient REAL,
        start_x REAL,
        start_y REAL,
        start_z REAL,
        target_x REAL,
        target_y REAL,
        target_z REAL
    )''')
    con.commit()
    print("Table created fresh with new schema")

# either update row or insert new one
def add_data(cursor, conn, skel_id, current_score, prev_score, attention_gradient, start_pos=None, target_pos=None):
    try:
        print(f"\nAttempting to add/update data:")
        print(f"skel_id: {skel_id}")
        print(f"current_score: {current_score}")
        print(f"prev_score: {prev_score}")
        print(f"attention_gradient: {attention_gradient}")
        print(f"start_pos: {start_pos}")
        print(f"target_pos: {target_pos}")
        
        cursor.execute("SELECT * FROM info WHERE skel_id =?", (skel_id,))
        row = cursor.fetchone()
        
        if start_pos is None:
            start_pos = {'x': None, 'y': None, 'z': None}
        if target_pos is None:
            target_pos = {'x': None, 'y': None, 'z': None}
            
        if row:
            print(f"Updating existing record for skel_id {skel_id}")
            cursor.execute("""UPDATE info 
                          SET current_score=?, prev_score=?, attention_gradient=?,
                              start_x=?, start_y=?, start_z=?,
                              target_x=?, target_y=?, target_z=?
                          WHERE skel_id=?""",
                       (current_score, prev_score, attention_gradient,
                        start_pos['x'], start_pos['y'], start_pos['z'],
                        target_pos['x'], target_pos['y'], target_pos['z'],
                        skel_id))
        else:
            print(f"Inserting new record for skel_id {skel_id}")
            cursor.execute("""INSERT INTO info 
                          (skel_id, current_score, prev_score, attention_gradient,
                           start_x, start_y, start_z,
                           target_x, target_y, target_z)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (skel_id, current_score, prev_score, attention_gradient,
                        start_pos['x'], start_pos['y'], start_pos['z'],
                        target_pos['x'], target_pos['y'], target_pos['z']))
        
        conn.commit()
        print("Data successfully added/updated")
        
        # Verify the data was written
        cursor.execute("SELECT * FROM info WHERE skel_id=?", (skel_id,))
        result = cursor.fetchone()
        print(f"Verification - Record in database: {result}")
        
    except Exception as e:
        print(f"Error in add_data: {e}")
        print(f"Current values: skel_id={skel_id}, score={current_score}, prev={prev_score}, grad={attention_gradient}")

    
#SQLite Initializing code below ----------------------------------------------------------------

con = sqlite3.connect(DB_PATH)
cur = con.cursor()
# create the SQLite database if it hasn't already been made before
create_table() 
#delete the attention scores from the table scores, from the previous run
#cur.execute('DELETE FROM info')

# End of SQLite Initializing code below --------------------------------------------------------

# generates random start/target positions and random attention score
class DynamicObject:
    def __init__(self):
        self.id = random.randint(11, 100)
        self.attention_score = random.random() * 0.7
        self.prev_score = 0
        self.attention_gradient = 0
        self.lifespan = random.uniform(3, 10)  # seconds
        self.creation_time = time.time()
        
        
        arousal = 10  
        
        # Calculate ranges
        x_min = -3.0 + (-4.0 - (-3.0)) * (arousal - 1) / 9
        x_max = 3.0 + (4.0 - 3.0) * (arousal - 1) / 9
        y_min, y_max = -1.5, -5.0
        z_min = -1.5 + (-0.75 - (-1.5)) * (arousal - 1) / 9
        z_max = 0.5 + (2.0 - 0.5) * (arousal - 1) / 9
        
        # Generate start and target positions
        self.start_position = {
            'x': random.uniform(x_min, x_max),
            'y': random.uniform(y_min, y_max),
            'z': random.uniform(z_min, z_max)
        }
        
        self.target_position = {
            'x': random.uniform(x_min, x_max),
            'y': random.uniform(y_min, y_max),
            'z': random.uniform(z_min, z_max)
        }

    def is_expired(self):
        return time.time() - self.creation_time > self.lifespan

# runs in a backgroun thread and periodically creates up to 5 active objects, removes 
# expired ones, writes them into same info table as humans
class ObjectManager:
    def __init__(self):
        self.active_objects = {}
        self.running = True
        print("ObjectManager initialized")
        print(f"Virtual objects are {'enabled' if ENABLE_VIRTUAL_OBJECTS else 'disabled'}")
        self.last_object_time = time.time()
        self.thread = threading.Thread(target=self.object_management_loop)
        self.thread.daemon = True
        self.thread.start()

    def add_object_to_database(self, obj):
        try:
            print(f"\nAdding new virtual object:")
            print(f"Database path: {DB_PATH}")
            print(f"ID: {obj.id}")
            print(f"Attention Score: {obj.attention_score}")
            print(f"Start Position: {obj.start_position}")
            print(f"Target Position: {obj.target_position}")
            
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                add_data(cursor, conn, obj.id, obj.attention_score, obj.prev_score, obj.attention_gradient,
                        obj.start_position, obj.target_position)
                self.active_objects[obj.id] = obj
                print(f"Virtual object {obj.id} added to database")
        except sqlite3.Error as e:
            print(f"Error adding object to database: {e}")

    def remove_object_from_database(self, obj_id):
        try:
            # Create a new connection for this thread
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM info WHERE skel_id=?", (obj_id,))
                conn.commit()
                if obj_id in self.active_objects:
                    del self.active_objects[obj_id]
        except sqlite3.Error as e:
            print(f"Error removing object from database: {e}")

    def object_management_loop(self):
        print("Object management loop started")
        while self.running:
            try:
                if not ENABLE_VIRTUAL_OBJECTS:
                    time.sleep(1)  # Sleep briefly when disabled
                    continue

                current_time = time.time()
                
                # Check for expired objects
                for obj_id, obj in list(self.active_objects.items()):
                    if obj.is_expired():
                        print(f"Object {obj_id} expired (age: {current_time - obj.creation_time:.1f}s), removing from database")
                        self.remove_object_from_database(obj_id)

                # Create new object with higher probability
                time_since_last = current_time - self.last_object_time
                should_create = (
                    len(self.active_objects) < 5 and  # Limit total objects
                    (random.random() < 0.15 or time_since_last > 15)  # 30% chance or forced after 15s
                )
                
                if should_create:
                    print(f"\nCreating new virtual object (Current active objects: {len(self.active_objects)})")
                    new_obj = DynamicObject()
                    self.add_object_to_database(new_obj)
                    self.last_object_time = current_time
                
                # Print status update
                if len(self.active_objects) > 0:
                    print(f"\nCurrent active objects: {len(self.active_objects)}")
                    for obj_id, obj in self.active_objects.items():
                        remaining_life = obj.lifespan - (current_time - obj.creation_time)
                        print(f"Object {obj_id}: {remaining_life:.1f}s remaining")

                time.sleep(1)  # Check every 5 seconds instead of 10-30
                
            except Exception as e:
                print(f"Error in object_management_loop: {e}")
                time.sleep(1)  # Keep trying even if there's an error

    def stop(self):
        self.running = False
        self.thread.join()

def get_highest_attention_score_id():
    try:
        cur.execute("SELECT skel_id, current_score FROM info ORDER BY current_score DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]  # Return the skel_id with highest score
        return None
    except sqlite3.Error as e:
        print(f"SQLite error during fetching highest score: {e}")
        return None

# ROS node that subscribes to nuitrack_topic, receives Skeleton messages, computes an attention score
# and stores results in SQLite database. 
# Skeleton message contains user id, joint points, emotion fields, and dwelltime
class AttentionScoreCalculator(Node):
    def __init__(self):
        # node name is "nuitrack_subscriber"
        super().__init__('nuitrack_subscriber')
        # subscribing to "nuitrack_topic" with message type nuitrack_skeleton.msg.Skeleton
        # callback: listener_callback. Skeleton joint positions come in coordinate frame called
        # camera_frame but the script wants "human distance from the robot"
        self.subscription = self.create_subscription(
        Skeleton, 
        'nuitrack_topic',
        self.listener_callback, 
        10)

        # stores known transforms
        self.tf_buffer = tf2_ros.Buffer()
        # listens for transforms being published by other nodes
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        self.w_happy = 0.5
        self.w_angry = 0.4
        self.w_surprise = 0.3
        self.w_neutral = 0.1
        self.w_emotion = 0.2
        self.w_position = 0.4
        self.w_velocity = 0.4
        self.lambda_val = -0.07
        self.w_proximity = 0.7
        self.w_hand_pos = 0.4
        self.h_rhand = None
        self.h_lhand = None
        self.prev_distance = None
        self.prev_dis_rhand = None
        self.prev_dis_lhand = None
        self.human_vel = 0.0
        self.rhand_vel = 0.0
        self.lhand_vel = 0.0
        self.max_vel_lhand = 1.0
        self.max_vel_rhand = 1.0
        self.max_vel_torso = 1.0
        self.prev_hab = 0.0
        self.m_hab = -0.9
        self.m_rest = 0.6
        self.delta_t = 0.0
        self.last_time = None
        self.attention_array = []
        self.skeleton_score = {}
        self.skeleton_habit = {}
        self.skeleton_habit_past = {}
        self.count = 0
        self.number = 1
        self.prev = 0.0
        self.attention_rate = 0.0
        self.skeleton_last_update = {}
        self.reset_timer = self.create_timer(1.0, self.reset_attention_scores)
        self.object_manager = ObjectManager()

    def listener_callback(self, msg):
        self.attention_score_calculator(msg)

    def attention_score_calculator(self, msg):
        # Get the ID with highest attention score
        highest_score_id = get_highest_attention_score_id()
        
        # Set gamma based on whether this skeleton has the highest score
        # gamme is true if the current message is for the most attended skeleton
        gamma = (msg.user_id == highest_score_id)
        
        # weighted sum: linear, if happy is high and happy weight is big - emotion score increase
        emotion_score = self.w_happy*msg.happy + self.w_angry*msg.angry + self.w_surprise*msg.surprise + self.w_neutral*msg.neutral
        
        # transform the torso position into the robots frame of reference
        # from world origin to torso
        torso_from_robot = self.transform_point(msg.torso)
        human_distance = self.euclidean_distance(torso_from_robot.point)
        rhand_distance = self.euclidean_distance(msg.right_hand.point)
        lhand_distance = self.euclidean_distance(msg.left_hand.point)

        #check to see if the hands are above their respective shoulders
        if (abs(msg.right_hand.point.y) > abs(msg.right_shoulder.point.y)):
            self.h_rhand = 0.75
        else:
            self.h_rhand = 0
        if (abs(msg.left_hand.point.y) > abs(msg.left_shoulder.point.y)):
            self.h_lhand = 0.75
        else:
            self.h_lhand = 0

        # negative lambda means bigger distance - smaller exponent - smaller score, bonus if hand raised
        position_score = self.w_proximity*math.exp(self.lambda_val*human_distance) + self.w_hand_pos*(self.h_lhand+self.h_rhand)

        #the max velocities are divided later in the code
        if self.prev_distance is not None: 
            # derivative ~ motion proxy
            self.human_vel = abs(self.prev_distance - human_distance)/(0.001)
            self.rhand_vel = abs(abs(self.prev_dis_rhand - rhand_distance)/(0.001)- self.human_vel)
            self.lhand_vel = abs(abs(self.prev_dis_lhand - lhand_distance)/(0.001) - self.human_vel)

        #self.max_vel = max(self.max_vel, self.human_vel, self.rhand_vel, self.lhand_vel)
        if self.lhand_vel > self.max_vel_lhand:
            self.max_vel_lhand = self.lhand_vel

        if self.rhand_vel > self.max_vel_rhand:
            self.max_vel_rhand = self.rhand_vel

        if self.human_vel > self.max_vel_torso:
            self.max_vel_torso = self.human_vel

        # notice that you normalize the velocities here
        velocity_score = self.human_vel/self.max_vel_torso + self.rhand_vel/self.max_vel_rhand + self.lhand_vel/self.max_vel_lhand

        # compute time difference between messages
        current_time = self.get_clock().now()
        if self.last_time is not None:
            self.delta_t = (current_time.nanoseconds - self.last_time.nanoseconds) / 1e9
        self.last_time = current_time

        #initialize personal habituation scores for every new skeleton id
        if msg.user_id not in self.skeleton_habit:
            self.skeleton_habit[msg.user_id] = 0.0
        
        if msg.user_id not in self.skeleton_habit_past:
            self.skeleton_habit_past[msg.user_id] = 0.0
        
        if msg.dwelltime == 0:
            self.skeleton_habit[msg.user_id] = 0
            self.skeleton_habit_past[msg.user_id] =0

        self.skeleton_habit[msg.user_id] = self.skeleton_habit_past[msg.user_id] + (gamma * self.m_hab + (not gamma) * self.m_rest)*self.delta_t
        if self.skeleton_habit[msg.user_id] > 1:
            self.skeleton_habit[msg.user_id] = 1
        elif self.skeleton_habit[msg.user_id] < 0:
            self.skeleton_habit[msg.user_id] = 0
        
        self.skeleton_habit_past[msg.user_id] = self.skeleton_habit[msg.user_id]
        #make sure to assign the current position to the previous position variable
        self.prev_distance = human_distance
        self.prev_dis_lhand = rhand_distance
        self.prev_dis_rhand = rhand_distance

        attention_score = (self.w_emotion*emotion_score + self.w_position*position_score + self.w_velocity*velocity_score + self.skeleton_habit[msg.user_id]) #*math.exp(-msg.dwelltime*0.007)
        attention_score = float(int(attention_score*1000))/1000
        # if a user hasn't been seen yet add a user to the skeleton_score map
        if msg.user_id not in self.skeleton_score:
            self.skeleton_score[msg.user_id] = []
        #depending on whether or not there are 20 entries into a specific skeletons id map yet, we will either just append a score, or pop a score off the top and then append a score
        if len(self.skeleton_score[msg.user_id]) < 30:
            self.skeleton_score[msg.user_id].append(attention_score)

        else:
            self.skeleton_score[msg.user_id].pop(0)
            self.skeleton_score[msg.user_id].append(attention_score)

        # gradient, approx derivate of change in score over change in time
        self.attention_rate = (attention_score - self.prev)/0.03
        self.count = sum(self.skeleton_score[msg.user_id])
        
        #after summing up the map for the current skeletons id, divide by the length of the map to get a average
        attention_score = float(int((self.count/len(self.skeleton_score[msg.user_id]))*1000))/1000
        
        
        #print(attention_score, msg.right_hand.point.y, msg.right_shoulder.point.y, self.skeleton_habit[msg.user_id], self.attention_rate)

        if self.prev is None:
            self.prev = 0

        # Create a new connection for this thread
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            add_data(cursor, conn, msg.user_id, attention_score, self.prev, self.attention_rate)
        
        self.prev = attention_score
        self.skeleton_last_update[msg.user_id] = self.get_clock().now()

    def reset_attention_scores(self):
        current_time = self.get_clock().now()
        for skel_id, last_update in list(self.skeleton_last_update.items()):
            if (current_time - last_update).nanoseconds > 1e9 and self.skeleton_score[skel_id][0] != 0.0:
                print(f"Resetting attention score for skel_id {skel_id} due to timeout")
                self.skeleton_score[skel_id] = [0] * 30
                self.skeleton_habit[skel_id] = 0
                self.skeleton_habit_past[skel_id] = 0
                
                # Create a new connection for this thread
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    add_data(cursor, conn, skel_id, 0, 0, 0)
                
                self.skeleton_last_update[skel_id] = current_time

    def transform_point(self, point : PointStamped):
        try:
            # Get the transform from 'camera_frame' to 'world'
            transform = self.tf_buffer.lookup_transform(
                'world',  # target frame
                'camera_frame',  # source frame
                rclpy.time.Time())  # get the latest available transform
            # Transform the point from 'camera_frame' to 'world' frame
            transformed_point = tf2_geometry_msgs.do_transform_point(point, transform)
            return transformed_point
        except Exception as e:
            self.get_logger().error("Failed to transform point: %s" % str(e))

    def euclidean_distance(self, point : Point):
        return math.sqrt(point.x**2 + point.y**2 + point.z**2)
    
    

   
def main(args=None):
    rclpy.init(args=args)
    transformer = AttentionScoreCalculator()

    # blocks forever, repeatedly
    try:
        rclpy.spin(transformer)
        
    except KeyboardInterrupt:
        transformer.object_manager.stop()
        cur.execute("DELETE FROM info")
        con.commit()
        cur.close()
        con.close()
    finally:
        rclpy.shutdown()
        cur.close()
        con.close()

if __name__ == '__main__':
    main()