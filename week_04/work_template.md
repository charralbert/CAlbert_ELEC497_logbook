---
title: "Nuitrack by Charlotte"
date: 2026-06-02
week: 4
contributors: [Charlotte]
---

## Objectives

Make my own script to run Nuitrack

- fool around with it
- understand it
- be goated

## Detailed Work Log

### Basically just copying console example 

**Description**: 
Modules in Nuitrack:
- ColorSensor:  It contains functions for configuring the module and retrieving the results of its work, along with the helper functions for interpreting the color values.
The Nuitrack Color Sensor module is used to obtain color maps from the sensor for each frame. The results of this module are used directly or indirectly in the work of other Nuitrack modules.

- DepthSensor:  It contains functions for configuring the module and retrieving the results of its work, along with the helper functions for interpreting the depth values.
The Nuitrack Depth Sensor module is used to obtain depth maps from the sensor for each frame. The module performs the primary processing of the depth data.

- UserTracker: This module provides access to user tracking capabilities.
The main class of this module is UserTracker. It contains functions for retrieving the results of module work.
The purpose of the Nuitrack User Tracker module is to detect users. The maximum number of users that can be detected is 6. The results of the module work are represented as UserFrame.

- HandTracker: Nuitrack Hand Tracker - This module provides access to user hand tracking capabilities.
The main class of this module is HandTracker. It contains functions for retrieving the results of module work.
The purpose of the Nuitrack Hand Tracker module is to track user hands and to interpret the actions performed by hands. Currently, the module can determine the rate of hand clenching and detect the "click" event. Only the hands of active users can be tracked (see the Nuitrack Skeleton Tracker description).

- GestureRecognizer: used to assess the state of user activity, detect gestures, and evaluate the state of these gestures. The state of the gesture is expressed as a numerical value equal to the progress of completion of the gesture as a percentage. There are 6 possible types of gestures: waving, swipe left, swipe right, swipe up, swipe down and push

**Process/Steps**:
1. made cpp file called "right hand tracking
2. Make your Cmake to have NUITRACK_SDK path, include DetectPlatform.cmake, include directories like Nuitrack/include and include/middlewhere
3. link_directories(${NUITRACK_SDK}/Nuitrack/lib/${PLATFORM_DIR}) - “When building right_hand_tracking, look in the SDK’s Nuitrack/lib/win64 folder for nuitrack.lib.”
4. executables and such... I am not a cmake goat. its all on github tho in the readme under right_hand_tracking for my repo

**Defintions n Descriptions n Nuitrack n Stuff**:
- underscores (_) before a variable indicate that is a member variable.

- connectOnNewFrame explanation
```python
_depthSensor->connectOnNewFrame(std::bind(&NuitrackGLSample::onNewDepthFrame, this, std::placeholders::_1));
```
_depthSensor is the DepthSensor member. 
The callback type is:
```python
typedef std::function<void (DepthFrame::Ptr)> OnNewFrame;
```
The function:
```python
	uint64_t connectOnNewFrame(const OnNewFrame& callback)
	{
		return _callbackStruct->addCallback(callback);
	}
```
So Nuitrack wants:
```python
void something(DepthFrame::Ptr frame);
```
It stores it in an internal list and whenever a new depth frame exists, Nuitrack invokes every registered callback and passes a DepthFrame::ptr

The handler, onNewDepthFrame, is a member function. Needs which object (this) and the argument (frame). So you can't write:
```python
_depthSensor->connectOnNewFrame(&NuitrackGLSample::onNewDepthFrame);
```
adapt the member function into plain callable that Nuitrack can invoke, use std::bind (from <functional>) which builds a new callable object that remembers which function to call, arguments are fixed now, arguments will be filled in later. std::bind stores the pointer (this) inside the wrapper and when Nuitrack calls the callback:
```python
(this->*onNewDepthFrame)(frame);
```

std::placeholders::_1 means the first argument passed when someone calls the wrapped function
1. Nuitrack calls: wrapped(frame)
2. frame lands in placeholder _1
3. bind forwards it as the first argument to onNewDepthFrame

Static callbacks don't need 'this':
_userTracker->connectOnNewUser(&NuitrackGLSample::onNewUserCallback);

- All types are under nuitrack-sdk-master/Nuitrack/include/nuitrack/types

- Non-static: "Do something to THIS sample's window/texture/state"
- Static: "Run this utility code that doesn't need a particular sample istance" cannot access class variables unless you pass 'this' via bind or use globals, authors are using static where the handler is just logging. 

*Figure 1: Brief description of what the image shows and its relevance to your work*

## Results & Data

### Measurements/Observations

| Parameter | Expected | Measured | Pass/Fail | Notes |
|-----------|----------|----------|-----------|-------|
| | | | | |

### Code Snippets

```python
# Add relevant code here
```

### Calculations

Show your mathematical work:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

## Challenges & Solutions

### Challenge 1: [Issue Description]

**Problem**: 

**Debugging Steps**:
1.
2.
3.

**Solution**: 

**Lessons Learned**: 

## Next Steps

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## References

- [Nuitrack module docs n such](https://download.3divi.com/Nuitrack/doc/group__UserTracker__group__csharp.html)
- [Reference 2](URL)

## Personal Notes

Any additional thoughts, observations, or things to remember...

### Immediate Actions (This Week)

| Action Items | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Action Item 1 | YYYY-MM-DD | ✅ Complete | |
| Action Item 2 | YYYY-MM-DD | ⚠️ In Progress | |
| Action Item 3 | YYYY-MM-DD | ⏳ Upcoming | |

---

**Entry completed**: YYYY-MM-DD HH:MM