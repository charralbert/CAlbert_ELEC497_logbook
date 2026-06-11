---
title: "[Descriptive Title of Your Work]"
date: YYYY-MM-DD
week: X
contributors: [Name1, Name2, Name3]
---

# Daily Logbook Entry Template

> **Instructions**: This is an example of a logbook template that describes work done on your project in a systematic manner. Copy this template to create your daily entries. Save as: `logbook/week-XX/YYYY-MM-DD_brief-description.md`

## Objectives

What did you plan to accomplish in this session?

-
-
-

## Detailed Work Log

### Definitions

**make_shared**
std::make_shared
C++ function that creates a shared pointer to a dynamically allocated object efficiently and safely

**Description**: 
Describe what you worked on in detail...

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

Testing NuitrackPublisher

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

- [Reference 1](URL)
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