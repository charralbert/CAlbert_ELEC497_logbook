---
title: "The Debug of Emotional Intent"
date: 2026-06-05
week: 4
contributors: [Charlotte]
---

## Objectives

- Document everything on this logbook
- Push working linux code to new branch
- Create new readme
- Find a question goddamnit

## The Random Decision to Debug that Solved it all

As I was reading through Nuitrack code, documentation, and understanding all the connections - I began to realize that it used a LOT of smart pointers. Because my windows laptop could run Nuitrack through the example code and the linux machine couldn't, there must be some difference between the operating systems that caused this bug. To understand this - I used valgrind: a linux debugging tool which essentially runs code in a sandbox to help find leaks, memory allocation issues, deadlocks, etc... it works as a VM by executing the code on a CPU. Through valgrind, the nuitrack code ran, though extremely slow. Gdb revealed errors as well. I realized that I needed to change the Nuitrack code - and I should've came to that conclusion a while ago.

## Changing the Nuitrack SDK code

### Summary of changes**
All changes target the Linux free(): invalid pointer crash when a user enters the frame (GDB showed it in FrameBorderIssue::~FrameBorderIssue()).

**Root cause**
Each user frame called getUserIssue<FrameBorderIssue>(), which did:
1.	new FrameBorderIssue(...)
2.	Wrap in a temporary std::shared_ptr
3.	Destroy it immediately in ~FrameBorderIssue / ~Issue

**Files changed**
1. Nuitrack/include/nuitrack/types/IssuesData.h
•	Added hasFrameBorderIssue(userId) — queries the C API (nuitrack_GetFrameBorderIssue) without heap-allocating FrameBorderIssue objects.
2. Examples/nuitrack_gl_sample/src/NuitrackGLSample.h
•	Mutex (_issuesDataMutex) for thread-safe access to issue data.
•	Cached border-issue flags: _frameBorderIssueByUserId (8 user labels).
•	Initialized _onIssuesUpdateHandler, _isInitialized, and _nuitrackReleased to safe defaults.
3. Examples/nuitrack_gl_sample/src/NuitrackGLSample.cpp
•	onIssuesUpdate: Updates the cached border-issue array using hasFrameBorderIssue() (no getUserIssue).
•	onUserUpdateCallback: Reads the cache only; removed all getUserIssue<FrameBorderIssue>() calls. Tightened label indexing (label & 7 for colors, bounds check for issue flags).
•	release(): Idempotent — won’t call Nuitrack::release() twice; disconnects issue callback; clears cached state under the mutex.
•	Destructor: Calls release() instead of calling Nuitrack::release() directly (avoids double-release on exit).

**How to run (reminder)**
```python
cd ~/sdk/NuiTrackSDK/nuitrack-sdk-0.38.5/Examples/nuitrack_gl_sample/build
export LD_LIBRARY_PATH=/usr/local/lib/nuitrack:$LD_LIBRARY_PATH
./nuitrack_gl_sample
```

**Linux versus Windows**
The bug was always there. Linux’s allocator and threading exposed it reliably; Windows was more forgiving, and Valgrind changed timing enough to hide it. glibc malloc is strict. When heap metadata is corrupted—or an invalid pointer is passed to free()—glibc aborts with:
free(): invalid pointer

That often happens at the next free(), not at the line that corrupted memory. So the crash looked like a generic heap error, but the backtrace pointed at FrameBorderIssue destruction.

On Linux, Nuitrack also tends to use more aggressive threading (Nuitrack::run() is asynchronous). That made the allocate/free pattern run often and concurrently with other callbacks, which made the failure show up quickly when someone stepped into frame.

Why Windows seemed fine
Windows uses a different C++ runtime and heap (MSVC/UCRT), not glibc. Those allocators:
•	Lay out memory differently
•	Check corruption differently (or less aggressively in some cases)
•	Can tolerate some misuse without aborting immediately
Same questionable pattern (new + immediate shared_ptr destroy on a callback thread), but you might never see a hard crash—maybe a small leak, subtle corruption, or simply “it works” if timing differs.

Why Valgrind “worked”
Valgrind doesn’t prove the code is safe. It changes how the program runs. It's much much slower, so race/timing bugs often disappear.
Different heap layout - corruption may not trigger the same way. Serialized threads, less overlap between issue updates and user-frame callbacks.

## Changing the Emotional Intent code

1. NuitrackGLSample.cpp / .h — same idea as the Nuitrack SDK fix
Before: onUserUpdateCallback called getUserIssue<FrameBorderIssue>() every frame, which allocated/freed FrameBorderIssue on Nuitrack’s thread.
After:
•	onIssuesUpdate fills a cached array with hasFrameBorderIssue(userId) (no heap alloc per frame).
•	onUserUpdateCallback only reads that cache under a mutex.
•	release() is idempotent via _nuitrackReleased and clears the cache safely.
Header additions: _issuesDataMutex, _frameBorderIssueByUserId, _nuitrackReleased, kMaxUserLabels.

2. new_skeleton_pub.cpp — shutdown / signal bugs
Before:
```python
void signalHandler(int signal) {
    if (signal == SIGINT)
        finished = true;
    rclcpp::shutdown(); // ran for ANY signal
    Nuitrack::release(); // ran during active tracking
    exit(EXIT_SUCCESS);
}
```
Also signal(SIGINT, &signalHandler) was called inside onNewSkeletonCallback on every skeleton message.

After:
•	Handler only reacts to SIGINT and sets finished + rclcpp::shutdown() (no Nuitrack::release() / exit() there).
•	signal(SIGINT, …) registered once in main().
•	After the spin loop ends: sampled.release() once (uses the idempotent release() above).

**RUN THE SCRIPT!**

After changing any code, make sure to colcon build, (if you haven't changed anything you shouldn't need to)
```python
colcon build --packages-select new_skeleton_pubsub nuitrack_skeleton
```

To run low arousal, high attention (cool but not scary)
```python
source install/setup.bash
ros2 launch new_skeleton_pubsub multi_node_launch.py mode:=2
```
mode 1: low arousal, low attention
mode 2: low arousal, high attention
mode 3: high arousal, low attention
mode 4: high arousal, high attention

**TLDR;**
stop calling getUserIssue<FrameBorderIssue>() in the GL sample code path, and stop calling Nuitrack::release() from a broken signal handler while tracking is still running.

## Question
1. How do repeated interactions with a robot arm affect perception, trust, and seeing the robot as a character?
- Does a UR5e become more "character-like" in participants' minds over time?
- Does familiarity reduce fear but increase trust?
- Does anthropomorphism increase, decrease, or stabilize with repeated exposure?
- Do people start assigning personalities to a robot arm?
- Does a perceived character emerge purely from movement patterns?
- How trust evolves after repeated successful interactions.
- Whether trust becomes overtrust.
- Whether trust is affected more by reliability or by movement style.
Compare conditions:
- Neutral movements vs. movements designed to express personality.


### Immediate Actions (This Week)

| Action Items | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Emotional Intent | like last week | ✅ Complete | |
| Decide on Question | 2026-06-05 | ⚠️ In Progress | |

---

**Entry completed**: 2026-06-05 2:00