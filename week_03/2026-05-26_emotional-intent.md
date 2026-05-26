---
title: "One Girl Versus Infinite Reading"
date: 2026-05-26
week: 3
contributors: [Charlotte]
---

## Objectives

- Read chapters 6-7 of Robot Modelling and Control - understand trajectory planning specifically...
- Read and understand Roy's emotional intent code

**Definitions**
- Ruckig is a motion planning library for robotics applications.
- Nuitrack is the skeleton tracking and gesture recognition solution.
- ROS uses a system called TF (tf2 in ROS2) that maintains a graph of frames and transforms between them - a shared dictionary for the whole system
- In ROS, "stamped" means the message includes a header with: timestamp (when the data was valid) and a frame name (what coordinate frame it's expressed in)
- Subscribing to a topic means "whenever someone publishes a message on this channel, call my callback function with that message"
- Pickle is Python's built in way to turn any Python value into bytes and later turn those bytes back into the same kind of value.
Movej versus Servoj:
- movej: one goal, trapezoid profile, then stop
- servoj: streaming joint targets - send a new q every few ms, arm tracks it. Used for real-time following


**d435_staticbroadcaster.py**
- TF is ROS's shared system for keeping track of coordinate frames (world, base_link, camera_frame) and the transforms between them over time
- tf2_ros.StaticTransformBroadcaster is a TF2 helper that publishes static transforms on the /tf_static topic
ROS has two main TF broadcasters:
- StaticTransformBroadcaster: for frames that do not move - camera bolted 
- TransformBroadcaster: for transforms that changes with time
- A quaternion corresponds to a rotation you can apply to vectors: converting
a point from camera to world uses: p(world) + R(world<-camera)*p(camera) + t(world<-camera) where R comes from the quaternion and t is translation vector.

**attention_scores.py**
ROS 2 node that subscribes to topic "nuitrack_topic," receives Skeleton messages (one per tracked person), computes attention score, and stores results in SQLite database (scores.db)
Other programs (headtracking_client.py) read that databse to decide which person the robot should pay attention to
- Skeleton message contains user id, joint points, emotion fields, and dwelltime
cur and con are SQLite database objects
- con: database connection
- cur: cursor = query executor

**headtracking_client.py**
A ROS2 node and TCP client
1. ROS subscriber: listens to skeleton messages on nuitrack_topic
2. TF user: converts head points from the camera frame into the world frame
3. Robot command client: sends commands over a TCP socket to ur_server.py (the program talking to the UR5e)
It also reads from scores.db (attention scores) and shared_data.db (robot joint angles, written by ur_server.py)

**ur_server.py**
Owns the UR5e; starts realtime servoj, listens on TCP port 50002, turns pickled commands into movej, set_realtime_pose, servoj, and continuously mirrors joint angles into shared_data.db for headtracking client

## Next Steps
I think I'm going to try and run emotional intent tomorrow... And then after attempt my own script?

- [ ] Run emotional intent
- [ ] ChUR5ette script (mixture of Charlotte and UR5e...)

### Immediate Actions (This Week)

| Action Items | Target Date | Status | Notes |
|--------------|-------------|--------|-------|
| Read through UR5e docs | 2026-05-22 | ✅ Complete | |
| Understand emotional intent | 2026-05-26 | ✅ Complete | |
| Read through 6-7 RMaC | 2026-05-25 | ⚠️ In Progress | I am almost done.. but reading through a textbook is making me tweak... I am not a physics goat |
| Create own script to perform basic movements | 2026-06-02 | ⏳ Upcoming | |
| Run emotional intent | 2026-06-03 | ⏳ Upcoming | I want it done by the 3rd bc thats when Mpan comes back, but goal would be tomorrow tbh that would be fire. |

**Entry completed**: 2026-05-26 4:30