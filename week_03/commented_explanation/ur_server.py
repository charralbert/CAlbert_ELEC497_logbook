#!/usr/bin/env python3

import URBasic
import math
import time
import socket
import pickle
import numpy as np
import sqlite3

con = sqlite3.connect('shared_data.db')
c = con.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, value INTEGER)''')


HOST = '192.168.1.101'  # Your CPC IP. If you don't have a divided control pc, it should be your computer ip.
PORT = 50002         
ROBOT_IP = '192.168.1.102' # Your Robot IP
ACCELERATION = 0.4  # Robot acceleration value for move to initial point
VELOCITY = 0.4  # Robot speed value for move to initial point




def receive_all(sock, n):
    """ Helper function to receive n bytes or return None if EOF is hit """
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


# main loop
# 1. read robot joints -> write shared_data.db
# 2. wait for 20-byte header from client
# 3. parse message type + payload length
# 4. run handler -> move robot
def handle_client(conn):
    
    while True:
        # publish joint state to db:
        # reads 6 joint angles from robot via RTDE, replaces entire data table, 
        positions = robot.get_actual_joint_positions() ## I think i need to add some of this stuff but im not sure where uet
        c.execute('''DELETE FROM data''')
        c.executemany('''INSERT INTO data (value) VALUES (?)''', [(value,) for value in positions])
        con.commit()
        

        # socket protocol:
        # 0-9: message type, left padded ASCII
        # 10-19: payload length as decimal string
        try:
            header = receive_all(conn, 20)
        
            if not header:
                break

            try:
                message_type = header[:10].decode('utf-8').strip()
                
                data_length = int(header[10:].decode('utf-8').strip())
            except UnicodeDecodeError as e:
                print(f"Unicode decode error: {e}")
                break
            except ValueError as e:
                print(f"Value error: {e}")
                break

            # current tool pose
            if message_type == 'tcp':

                tcp_pose = robot.get_actual_tcp_pose()
                # payload: pickle.dumps(...) bytes
                packed_data = pickle.dumps(tcp_pose)
                response_header = f"{message_type:<10}{len(packed_data):<10}".encode('utf-8')
                # reply with current tool pose: [x,y,z,rx,ry,rz]
                conn.sendall(response_header + packed_data)

            # main head-tracking command
            elif message_type == 'ee_target':
                # receive_all(sock, n) reads exactly n bytes - partial TCP reads
                data = receive_all(conn, data_length)
                ee_target = pickle.loads(data)
                robot.set_realtime_pose(ee_target)
            
            # rotate write 2 (joint 5)
            elif message_type == 'headspin':
                rotation = receive_all(conn, data_length)
                rotation = pickle.loads(rotation)
                initial_pos = robot.get_actual_joint_positions()

                position = initial_pos[:]
                if rotation[1] == 1:
                    position[4] = position[4] + rotation[0]
                else:
                    position[4] = position[4] - rotation[0]
                robot.movej(position, a = 2, v = 2)
            
            elif message_type == 'breathe':
                initial_pos = robot.get_actual_tcp_pose()
                breath = receive_all(conn, data_length)
                breath = pickle.loads(breath)
                initial_pos[0] = initial_pos[0] + breath[0]
                initial_pos[2] = initial_pos[2] + breath[1]
                robot.set_realtime_pose(initial_pos)
            
            # home
            elif message_type == 'init_pose':
                robot.movej(q=robot_startposition, a= ACCELERATION, v= VELOCITY)
                tcp_pose = robot.get_actual_tcp_pose()
                packed_data = pickle.dumps(tcp_pose)
                response_header = f"{message_type:<10}{len(packed_data):<10}".encode('utf-8')
                conn.sendall(response_header + packed_data)
                robot.init_realtime_control()  
            
            elif message_type == 'home':
                rotation = receive_all(conn, data_length)
                rotation = pickle.loads(rotation)
                robot.servoj(rotation, 1.5, 1.5, 1.5, 0.5, 150)
                #robot.set_realtime_pose(rotation)

            # smooth path waypoints
            # used when headtracking_client has no target person
            elif message_type == 'transition':
                transition_pos = receive_all(conn, data_length)
                transition_pos = pickle.loads(transition_pos)
                robot.set_realtime_pose(transition_pos)
                
                
        except (ConnectionResetError, BrokenPipeError):
            print('Connection lost')
            break
        
        

# home pose
robot_startposition = (math.radians(-76.57),
                    math.radians(-54.83),
                    math.radians(-93.14),
                    math.radians(-32.59),
                    math.radians(79.27),
                    math.radians(0))


# initialise robot with URBasic
print("initialising robot")
robotModel = URBasic.robotModel.RobotModel()
robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_IP,robotModel=robotModel)

robot.reset_error()
print("robot initialised")  #  sllab backwards
time.sleep(1)


# Move Robot to the midpoint of the lookplane
robot.movej(q=robot_startposition, a= ACCELERATION, v= VELOCITY)
robot.init_realtime_control()  
time.sleep(1) 

# start TCP server, blocks until headtracking_client connects
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Server is listening...')

    try:
        while True:       
            conn, addr = s.accept()
            print('Connected by', addr)
            handle_client(conn)
            conn.close()
            print('Connection closed')
    except KeyboardInterrupt as e:
        conn.close()
        c.close()
        con.close()
        print(e)
    finally:
        conn.close()
