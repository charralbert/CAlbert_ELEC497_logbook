---
title: "Running Emotional Intent"
date: 2026-05-27
week: 3
contributors: [Charlotte]
---

# DAY 1: 05-27
## Objectives

Figure out how to run this guy

- Camera to world, measurements and all that...

## The Camera

**Description**: 
I set up the tripod to be adjacent to around where I believe Roy set up his mount... Now, I must figure out how to adjust the script so that the new camera setup can still run the script. From my research, it seems like x is forward/backward but based on Roy's code and his research images... it seems like x is side to side... I'm going to go based off his code I think. 

**Definitions**:
- Quaternion: is a compact way to represent 3D orientation and rotation without suffering from gimbal lock (a problem with Euler angles like roll/pitch/yaw)

### Measurements/Observations

| Parameter | Measured | Notes |
|-----------|----------|-------|
| x offset  |  0.375m  | |
| y offset  |  0.335m  | |
| z offset  |  0.145 - 0.012 = 0.133 | |
| base height | 0.012m | |

### Code Changes

**d435_static_broadcaster.py**
Roy's original translation
```python
translation = geometry_msgs.msg.Vector3(x=0.173, y=-0.332, z=0.075)
```

New estimated translation
```python
translation = geometry_msgs.msg.Vector3(x=0.375, y=-0.335, z=0.133)
```

**attention_scores.py**
Original:
```python
ENABLE_VIRTUAL_OBJECTS = True
```

New:
```python
ENABLE_VIRTUAL_OBJECTS = False
```

**new_head_tracking.py**
Original:
```python
AROUSAL = 1
```

New:
```python
AROUSAL = 10
```

### Calculations

Roy's original camera Quaternion to roll, pitch, yaw:
$$
x=0.0, y=-0.6755902, z=0.7372773, w=0.0

roll = atan2(2(wx+yz),1−2(x2+y2)) ~= -180 degrees
pitch = asin(2(wy−zx)) ~= 0 degrees
yaw = atan2(2(wz+xy),1−2(y2+z2)) ~= -85 degrees
$$

## Running the Script

ros2 run doesn't see the python nodes, I've tried colcon build. So I just directly run the python scripts, those seem to work.

Open 4 terminals, in all terminals, run:
```python
source /opt/ros/humble/setup.bash
source /emotional-intent/new_skeleton_pubsub/install/setup.bash
```
In terminal 1,3,4 cd to where the scripts are located 
(emotional-intent/src/new_skeleton_pubsub/scripts)

In terminal 1:
```python
python3 d435_static_broadcaster.py
```

In terminal 2:
```python
ros2 run new_skeleton_pubsub new_skeleton_pubsub
```

In terminal 3:
```python
python3 attention_scores.py
```

In terminal 4:
```python
python3 new_head_tracking.py
```

From this, the code begins, and there are no errors. However, after setting ENABLE_VIRTUAL_OBJECTS to False, it is clear that the robot cannot see anyone/track a skeleton.

## Challenges & Solutions

### Mini Challenge: [Which scripts to use!]

This is more of a note... and less of a challenge... but the code on the MItHRIL GitLab and the Linux Machine are different. I am unsure which is the newer script as I don't really wanna change anything to his code..? And don't think I should have to because it worked before...

There are comments in Korean on the Linux machine. I unfortunately do not speak Korean.

### Challenge 1: [How to control attention]

**Problem**: 
I want to run the "low arousal, high attention" because I feel like that's the best balance of safe, slow movement while seeing that the robot is actively tracking people. I can get the robot to run, but it's clearly not tracking a skeleton...

I also know little about ROS and this codebase is not super intuitive. 

**Debugging Steps**:
1. After running NuitrackGLSample with
```python
ros2 run new_skeleton_pubsub nuitrack_gl_sample
```
A view of the camera appears, the camera quality is superr bad, but after clicking it... it's fine (??ok??). When I go to step into frame, the script quits and the terminal spits the error: 
free(): invalid pointer
[ros2run]: Aborted

# DAY 2: 05-28

## Running the code from GitLab

**Description**
I have cloned the repository from GitLab onto the linux machine. The code from GitLab is older... So maybe I can incorporate my own fixes into it and feel less bad about it. First I will try running it straight up.

### Code Changes

I had to solve some paths in CMake like Nuitrack.h, etc...

### Emotional Intent code run
```python
cd emotional-intent-main_from-gitlab
colcon build --packages-select new_skeleton_pubsub nuitrack_skeleton

# Confirm scripts are installed
ls install/new_skeleton_pubsub/lib/new_skeleton_pubsub/

source install/setup.bash

ros2 launch new_skeleton_pubsub multi_node_launch.py mode:=2
```

### Test camera and nuitrack run

```python
# Default init
ros2 run new_skeleton_pubsub nuitrack_gl_sample
# Or with a Nuitrack config file
ros2 run new_skeleton_pubsub nuitrack_gl_sample /path/to/nuitrack.config
```

## The main Challenge

My enemy:
```python
free(): invalid pointer
```

### Next steps 
Reinstall Nuitrack?

# DAY 3: 05-29

**Description**
Hoping for a win today

## Nuitrack Subscription
Maybe the main culprit of it all is the fact that I am not logged into our Nuitrack subscription...

I asked my goat (Prof Pan) for the login. We will now continue our journey from here.

## I hate this bug

I hate it

I sent in a ticket to 3DiVi because I am actually lost at this point. The Nuitrack app works with skeleton tracking but it does not work on Roy's script or the example script from Nuitrack.

Same dumb ahh error bro I'm tweaking out.

### Immediate Actions (This Week)

| Action Items | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Action Item 1 | YYYY-MM-DD | ✅ Complete | |
| Action Item 2 | YYYY-MM-DD | ⚠️ In Progress | |
| Action Item 3 | YYYY-MM-DD | ⏳ Upcoming | |

---

**Entry completed**: YYYY-MM-DD HH:MM