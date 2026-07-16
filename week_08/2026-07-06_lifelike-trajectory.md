---
title: "Lifelike trajectory"
date: 2026-07-06
week: 08
contributors: [Charlotte]
---

Last week I was off! So I am labeling this my week 8.

## Final stretch

| Overall Goal | Target Date | Notes |
|-----------|-------------|--------|-------|
| Slow-fast-slow velocity planning | 2026-07-10 | |
| Develop more trusting animations | 2026-07-17 | |

## New launch file + robot movement to allow for testing

Normal run:
```python
ros2 launch character_trust character_trust.launch.py
```

Test:
```python
ros2 launch character_trust character_trust.launch.py behavior:=look trust_level:=175
```

behavior options:
- shake
- glance_user
- glance_surroundings
- look
- look_away
- base_motion

trust options:
- 0 (0)
- 100 (1)
- 175 (2)
- 250 (3)
- 325 (4)
- 400 (5)

## Detailed Work Log

I am frustrated. I don't know if speed commands will allow robot motion as fast as I'd like but perhaps I can test some more. First I'm going to do a code review of my scripts so I can think of where to go from here. My thoughts are getting jumbled and I am confused.

### avoidant.py
**Purpose**
The script serves as the character. It defines the trust level which increases over time if the user is slow and a fair distance away. There are 5 trust levels which compute different behavior, as trust increases it will display signs of trust. It defines the probability of certain behaviors. Right now, I am testing trust level 0 and 1 and the transition between them. 

some behaviors that are/being implemented:
- glance at user: quickly look at user and then look away (0.5-1s)
- glance at surroundings: quickly look at a random point and then look away (0.5-1s)
- shake: can overlap with other behaviors, implemented by a sawtooth motion about wrist1 (0.4-0.9s)
- look: stare at user (5.0-10s)

Each trust_level function is called depending on the current trust value:
- 0-100 is trust level 0, when trust is at 75 it begins to transition to level 1
- 100-175 is trust level 1, when trust is at 150 it transitions to level 2
so on and so forth... not currently implemented though
The current transition being worked on is from 0 to 1, this transition is defined in the function for level0. When trust is above 75, if the trust rate is rising (positive) then the robot will turn its base toward the user getting closer to the base config of trust level 1. If the trust rate is sinking (negative), then the base config retreats back. 
The base is capped between 0 and 26 so it doesn't go beyond either of trust level 0 or 1 base configuration.
Then, if the manual behavior isn't set (set on launch if a certain behavior is specified), a new behavior is computed. For any gaze behaviors - there is a check first to ensure that one isn't being computed currently.

On update, sets start to now if start is 0. Sets prev trust = trust, and checks for any expired behaviors to delete off the list. Similar to a FSM, if the trust variable is below a certain value, compute the behavior for that corresponding trust level. The trust rate is computed using trust - prev_trust. An EMA filter is placed over it with alpha of 0.4 to hopefully filter out some sensor noise. 

**Functions**
_set_config_from_template
sets a new config without the base joint snapping into place: Copies new set config for the trust level but changes the base to match the old previous base configuration.

_expire_behaviors
searches for the behavior name within the behavior_deadlines. If now >= the deadline, set attribute to false and delete from the behavior deadlines 

_start_behavior
The shortest (lo) and longest (hi) time for a behavior are defined within the BEHAVIOR_DURATIONS dict. If the behavior is exclusive - like a look and a glance cannot happen together but a look and shake can - check for other GAZE_BEHAVIORS and set them to false within the object (avoidant class has bools for each of the different behaviors). Then, it sets the designated behavior name to true and adds a deadline by choosing randomly between the lo and hi and adding it to "now".

**Forseeable edits**
- the going backward of the base configuration? Maybe just halt? I would like to add some randomness to it as well...?

### subject_subpub
subscribes to nuitrack_publisher.cpp which publishes nuitrack skeleton data. 

**Purpose**
Transforms the skeleton data from camera to robot. Then computes distance of head, distance of left/right hands, acceleration, and velocity. This is used to calculate an attention score which dictates the focus of the robot. The subject id, distance of head score, distance of left/right hands score, velocity score, acceleration score, as well as points for torso, left hand, right hand, left ankle, and right_ankle are sent in the ros message.

**Subject callback**
1. Subject is transformed
2. If the subject ID is new, add a new subject object into the subject array.
3. If subject is already in array, update the joints. A frame counter is incremented. If the frames < 3, then the subject is still in warmup and acceleration can't be computed yet.
Velocities of the head, torso, and hands are calculated using the difference in current points - prev points / dt. The hand velocities are subtracted from the torso to find how fast the limbs are going. The velocity score is computed by taking the max from raw velocitiy of left, right, and head divided by the max velocity (max velocity is a global which was found through measurement). 
The acceleration of the head and hands is found through the difference in prev and current velocities / dt, but the velocities in this case are fed through the EMA filter with alpha of 0.2. The velocity score is raw sensor value to be sensitive to movement, but if using the raw score to compute a derivative... it is much more sensitive. After the acceleration is calculated, it is again filtered with EMA. The acceleration score is calculated by choosing the max from acceleration of normalization of left hand, right hand, and head.
The distances are calulcated by finding the euclidean distance from the robot to head and hands, then the score is calculated by subtracting the distance/far distance and subtracting from 1. The hand distance is chosen by the closest hand.

**Forseeable edits**
- double EMA filtering for acceleration..? just raw for velocity..? maybe change this..?

### robot_movement_sub.py
**Purpose**
Subscribes to subject_subpub and sends commands to the UR5e. Sets initial config to trust level 0 if unspecified or to whatever is specified. 

**listener_callback**
Calls avoidant update to compute new trust levels given the information from subject_subpub.
Checks if gaze_active is false and was_gaze_active is true, if yes, reset trajectory path.
Logs a bunch of information for debugging...
Calls behavior selector to compute new behavior
Calls base_motion to add breathing.
Sets realtime pose.

**random_glance_point**
Each trust level has designated x,y quadrants they can look to glance, this is because I didn't want glance points to be completely random because this would cause the robot to look in really odd direction. Each axis has a range of where they can look: X and Y are +/- 12 and z is -0.3 to 1.2. A random point is generated given those limitations and goes through a check if it's within the correct quadrant. If not, a new point is generated. 

**_actual_joints**
returns the joint positions from the robot

**_actual_joint_speeds**
gets joint speeds from the robot

**_ruckig_substeps**
Ruckig is configured with delta_time = 0.01, but ROS callback is lower than that. 
- now = time.time()
- First call: _last_gaze_time is None, initialize timestamp and return 1 step
- dt = max(now-last gaze time, 0.001)
- last gaze time is now
- return the max( 1, min(number of 10ms chunks that have passed, 20))
For example: if callbacks are every 33ms, dt = 0.033/0.01 = 3.3 -> run 3 substeps
1 callback = several Ruckig steps, catch-up

**apply_base_smoothing**
Smoothes base angle when being incremented 

**_gaze_active**
returns true if self.test_behavior is set to any gaze behaviors, otherwise returns true if any avoidant class behaviors are set to true, otherwise false. 
- test_behavior is set manually through launch for testing a behavior

**behavior_selector**
Smoothes base joints. 
Checks what test_behavior is set to first
Else, checks character behaviors. 
Whatever behavior is true, the function for the dedicated behavior is called.

**base_motion**
Adds breathing offsets to shoulder and elbow joints

**shake**
Adds shake frequency with a sawtooth function based on character speed. Just adds offset, can be computed with gaze behaviors

**_smooth_gaze_joints**
calls wrist fk to get new joints from tracking point, if the wirst deltas are larger than 0.25 radians, compute trajectory with Ruckig using slow-fast-slow motion. If deltas are smaller, joints are set and returned.
Checks if pose is finished, if yes then break.
returns joints

**glance_user**
Looks at user for short amount of time.

**glance_surroundings**
Glance at a random point. Sets random glance point if was previously not glancing and now is. 

**look**
looks at user for longer amount of time

**look_away**
nothing burger

**Forseeable changes**
Change the base smoothing to just be joint smoothing... make it reusable
Make shake amp bigger...

### trajectory.py
**Purpose**
Wrapper around Ruckig for wrist only profile moves, does not continuously track head points, only for large wrist movement

**Constant**
PROFILE_MAX_VEL, PROFILE_MAX_ACCEL, PROFILE_MAX_JERK: per joint limits passed to Ruckig
LARGE_WRIST_ANGLE: threshold to decide whether to use profile
WRIST_RETARGET_TOLERANCE: used by caller to replan if target shifts mid profile
GAZE_ACTIVE_DOFS: only wrist 1 and 2 profiles are driven

**__init__**
creates 6-DOF Ruckig generator with 10ms timesteps, allocates reusable input/output buffers, initializes interanl state:
- path: whether profile is currently active
- _active_dofs: which joints profile affects
- _frame_pose: base pose for untouched joints

**reset_path**
Prevents stale profile targets/state from leaking into the next behavior profile
- stops any active profile
- re-seeds current position/velocity in Ruckig input
- resets acceleration to zero
- resets enabled joints to all true
- calls ruckig.reset() to clear internal planner state

**begin_profile**
- chooses active DOFS
- chooses current_pose, if mid-profile continue from Ruckig input state otherwise start from frame_pose
- For inactive joints, forces target_pose[i] = current_pose[i] (hold fixed)
- Configs ruckig input: curr and target pose, target 

**Change**
just remove trajectory atp it does nothing.

---

**Entry completed**: 2026-07-07 4:00
