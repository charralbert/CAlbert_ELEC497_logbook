# Turkish Ice Cream Robot: Examining Playful Deception in Social Human-Robot Interactions

citation:
@misc{kim2025turkishicecreamrobot,
      title={The Turkish Ice Cream Robot: Examining Playful Deception in Social Human-Robot Interactions}, 
      author={Hyeonseong Kim and Roy El-Helou and Seungbeen Lee and Sungjoon Choi and Matthew Pan},
      year={2025},
      eprint={2509.21776},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2509.21776}, 
}

## Abstract
Playful deception in Human-Robot Interaction. Investigate how bounded, culturally familiar forms of deception influence user trust, enjoyment, and engagement during robotic handovers. Implemented 5 trick policies to deceptively delay handover. Results reveal that TIC deception enhances enjoyment and engagement but reduces perceived safety and trust. 

## Introduction
The TIC vendor routine is a short performance in which the handover deceives the user for a certain amount of time, but always results in a successful handover, and thus the deception is benign and not malicious.

## Background
Robot deception is often avoided. Hypothesize that playful deception may have multi-dimensional effects in everyday interaction scenarios. Rather than a risk to be avoided, it may serve as a potential interaction design component under certain conditions.
Incongruity Theory, which says that humour arises when expectations are disrupted.
Benign Violation Theory, which says that norm violations can be experienced humorously when framed as safe and acceptable.
-	H1: Playful, safety-bound deception can increase users’ enjoyment and engagement but may decrease trust and perceived safety
-	H2: The effects of playful deception can be moderated by interaction design factors such as motion style, timing, and sequence. 

## The TIC Robot
Design objectives:
	Implement a hardware module that ensures safe interaction even in unintended collisions
	Capture and reproduce the characteristic motions of TIC vendors while ensuring the deception remains socially acceptable and playful
	Implement multiple trick behaviours derived from observational analyses, allowing controlled manipulation of deceptive strategies and interaction time.
Built a custom TIC end-effector module that allows the robot to achieve swift and safe motions, developed trick policies, and integrated implementation details: inverse kinematics, hand tracking, and system synchronization.
End-effector module:
	Stepper motor for rapid twisting gestures.
	Carbon fiber rod is attached by neodymium magnets, reinforced with masking tape for stability during high-speed motion. 
	Cone is magnetically mounted at the rod tip
Trick Polices were focused on behaviours where deception arises from evasive motions.
	Bouncing: move cone from side-to-side in rhythmic, hopping motion.
	Twisting rotates the cone to opposite side of approaching hand while shaft is fixed.
	Large arc
	Continuous arc moves to the opposite side of the hand on the circle continuously
	Dancing
Implementation.
	Used a UR5e manipulator which has a 6-DOF arm controlled in a reduced 3-DOF task space anchored to human-centered frame, (r,θ,φ). R is a prismatic degree of freedom along forward-back axis, θ is azimuth (side to side angle), and φ is elevation. Joint commands are computed via inverse kinematics, subject to joint and velocity constraints to ensure smooth, safe execution.
	Hand Tracking: Leap Motion Controller 2 at 120 Hz. To mitigate latency effects on interaction, applied a velocity-based prediction with a 0.15 lookahead and low-pass filter to smooth noisy measurements.
	System Integration: ROS2 framework. UR5e is controlled at 200 Hz and twisting motor at 50 Hz.

## User Study
H1: How do perceptions of the robot differ between straight handover and deceptive handover?
H2: How does interaction length influence user perceptions of deceptive handovers?
Procedure: users participated in a straight handover (SH) and a deceptive handover (DH). DH had varying lengths: short, medium, and long, in which the robot executed a fixed sequence of five tricks.
They measured deception, enjoyment, performance trust, and moral trust through standardized scales, custom questions, and questionnaires based on 7-point Likert scales.
Used ANOVA (analysis of variance).
