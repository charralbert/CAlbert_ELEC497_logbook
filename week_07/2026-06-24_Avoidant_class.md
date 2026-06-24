---
title: "[Builing Trust with an Avoidant and the Fight for Velocity and Acceleration that Makes Sense]"
date: 2026-06-something
week: 7
contributors: [Charlotte]
---

## What I have done

I build upon the Avoidant class to essentially make an FSM. I will include a figure of it in this log because I think that would make a little more sense than me explaining it. The trust score ranges from 0 - 475 (?) and is a function of time basically. Trust will increase over time, because of familiarity, but if the user is too close, too fast, or accelerating too quick, it will subtract a certain amount dictated by an indicator variable with a threshold and a certain weight. Silhouette was removed for now because it is realllyyyy inconsistent... All scores: distance of head, distance of hands, velocity, acceleration, are normalized from 0 to 1 by dividing the max amount (done through some imperical testing). I have added behaviors that include: shaking (through a sawtooth function about wrist2), glancing at user, glancing around, looking at user, and look away. 

So far, trust level 0 (trust score is less than 100), and trust level 1 are being tested. Some initial thoughts are:
- I am standing still, why is my velocity score 1?
- I am standing still, why is my acceleration score 1?
- I am annoyed
- The glancing works but is superrrr robotic. Just like overall motion, I would like to (eventually) implement trajectory for the way this robot should move because right now it feels robotic and weird.
- I need to add limits to where the random glance is because sometimes that head is flipping upside down like I don't need all that. 

## What will I do

### Actions

| Action Items | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Nervous Base Personality | 2026-06-17 | ✅ Complete | |
| Research + Clean Up Repo | 2026-06-22 | ✅ Complete | |
| Glance and Look basics | 2026-06-26 | ✅ Complete | |
| Add limits to glances | 2026-06-26 | ⚠️ In Progress | |
| Figure out velocity and acceleration scores | 2026-06-26 | ⚠️ In Progress | |
| Height of arm measurement instead of silhouette(?) | 2026-06-26 | ⏳ Upcoming | |
| Develop Ability to TOT (trust over time) | 2026-06-30 | ⚠️ In Progress | |

---

**Entry completed**: 2026-06-24 4:30