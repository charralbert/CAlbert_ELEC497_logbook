---
title: "WE ARE MOVING! An Overview Thus Far"
date: 2026-06-17
week: 6
contributors: [Charlotte]
---

## Intro

The following entry details the work done thus far. This includes three nodes and 1 script
- nuitrack_publisher.cpp: publishes PointStamped for body joints from Nuitrack to topic /nuitrack_data
- subject_subpub.py: Transforms the body joints from camera frame to base, calculates a distance, silhouette, and velocity score (added together computes the attention score). Publishes the subject id of interest, some skeleton points, and scores.
- robot_movement_sub.py: sets connection to robot, currently set in the avoidant position, head following and breathing.
- avoidant.py: Attributes specific to the robot character. 

## Script Details and Future Changes

### nuitrack_publisher 

**Description**: 
Initializes Nuitrack, publishes nuitrack data aside from fingertips and feet.

**Testing NuitrackPublisher**

terminal 1
```python
source /opt/ros/humble/setup.bash
source ~/CAlbert/calbert_ur5e/install/setup.bash
ros2 run character_trust NuitrackPublisher
```

terminal 2
```python
source /opt/ros/humble/setup.bash
source ~/CAlbert/calbert_ur5e/install/setup.bash
ros2 topic echo /nuitrack_data
```

if you step into camera view, you should see joint messages

running the script:
```python
cd ~/CAlbert/calbert_ur5e/install/setup.bash
source /opt/ros/humble/setup.bash
colcon build --packages-select trust_msgs character_trust
source install/setup.bash
ros2 launch character_trust character_trust.launch.py
```

### subject_subpub.py

**Description**
Computes attention score through the addition of distance, velocity, and silhouette. w stands for weight.
- Distance = (w_dist_head * e^(-lambda * dist_head) + w_dist_hand * e^(-lambda * (dist_r_hand + dist_l_hand)/2))/2
- Silhouette = w_silhouette * e^(w_alpha * (dist_torso_to_l_hand + dist_torso_to_r_hand))
- Velocity = (w_vel * (vel_l_hand/v_l_hand_max + vel_r_hand/v_r_hand_max + vel_head/v_head_max))
All calculations are clamped to stay between 0.0 and 1.0
- Attention = distance_score + silhouette_score + velocity score

**Improvements**
1. Further care needs to be put in the weights for the components, so far, random weights have been put in.
2. Further consideration needs to be put in for the information being sent from this node to the next.
3. The Avoidant personality is initialized in this node, it should be removed
4. Further consideration into the distance calculation. If a subject has hands extended, typically that is how an animal would trust... potentially move hand distance out of the distance score. 
5. Silhouette uses both the x,y,z distance... consider just using the z and y as that's what makes someone have a larger silhouette...

### robot_movement.py

**Description**
Sets up base position and breathing motions. By using some forward kinematics and calculus for wrist1 and wrist2, the robot can head track from this position. Calls avoidant object for joint limits. EMA filter for smooth head tracking motion. Sends robotic motion with set_realtime_pose

**Improvements**
1. EITHER create a separate node to decide robot behaviour OR add robust logic with the avoidant character which will decide behavior (probably the latter)
2. set_realtime_pose is good for head tracking... mostly(?) But especially for quirks and looking... consider a more animation-style sort of movement... I don't know how to do that yet but you know..

### avoidant.py
A class which hold parameters which will dictate how the avoidant character behaves. 

1. Add onto Avoidant character to allow for dynamic change over time AND "quirks"

## Measurements/Observations

| Joint | Negative | Positive | 
|-----------|----------|----------|
| Base | clockwise | counterclockwise | 
| Shoulder | Hunch | Straighten |
| Elbow | Close to body | away from body |
| Wrist 1 | Curl left (POV robot) | Curl right |
| Wrist 2 | Look right | Look left |
| Wrist 3 | clockwise | counterclockwise |

| Axis | Lowest Value | Highest Value | 
|-----------|----------|----------|
| X | -1.833 | 2.430 | 
| Y | -4.209 | -0.813 |
| Z | -1.455 | 1.262 |

**do more trials
| Parameter | Lowest Value | Highest Value |
|-----------|----------|----------|
| hand velocity | 0 | 16 |
| head velocity | 0 | 6.65 |
| hand acceleration | 0 | 337 |
| head acceleration | 0 | 45 |
| hand distance | 0.81 | 3.25 |
| head distance | 1.42 | 3.35 |
| silhouette | 0.06 | 3.27 |

## Challenges & Next Steps

1. Reorganize current code to prepare for more robust character development
1. Motion as less robotic

## Next Steps

- [ ] Research Animation Practices
- [ ] Research Disney Avatar robot?
- [ ] Clean Up Repo

### Immediate Actions (This Week)

| Action Items | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Nervous Base Personality | 2026-06-17 | ✅ Complete | |
| Research + Clean Up Repo | 2026-06-22 | ⚠️ In Progress | |
| Glance and Look | 2026-06-26 | ⏳ Upcoming | |
| Develop Ability to TOT (trust over time) | 2026-06-30 | ⏳ Upcoming | |

---

**Entry completed**: 2026-06-17 4:30