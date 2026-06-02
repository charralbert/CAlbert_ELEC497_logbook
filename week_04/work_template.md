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

**Members Present**: [Name1, Name2, Name3]

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


**Materials/Tools Used**:
-
-

**Process/Steps**:
1.
2.
3.

**Documentation**:
<!-- Add images, diagrams, screenshots from the images/ folder -->
<!-- Store your images in: images/week-XX/ directory -->

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