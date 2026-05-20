# Social Life of Robot Arms: How Arousal and Attention Shape Human-Robot Interaction

citation: @misc{elhelou2025sociallifeindustrialarms,
      title={The Social Life of Industrial Arms: How Arousal and Attention Shape Human-Robot Interaction}, 
      author={Roy El-Helou and Matthew K. X. J Pan},
      year={2025},
      eprint={2504.01260},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2504.01260}, 
}

## Abstract
Explores how human perceptions of non-anthropomorphic robot manipulator can be shaped by arousal (movement energy, expressiveness) and attention (capacity to selectively orient and engage with a user). Combines gaze-like attention engine with arousal-modulated motion layer to explore how expressive and interactive behaviors influence social perception. Found that high attention = warmer and competent, high arousal (fast and energetic) = discomfort and disturbance.

## System Design
<p align="center">
  <img src="files\TIC\TIC_system_design.png" width="1000" alt="System Design">
  <br>
  <em>Figure 1: System Design</em>
</p>
Attention Engine:
Directs robots attention to salient features in its visual environment (within range of Intel RealSense D435 Depth Camera). Computes attention score for each individual, determining saliency and guiding robot’s gaze to enable dynamic responsive interactions.
Φ = wpP + wvV + Θ(t)
Where P is proximity and hand position, V is torso and hand motion, and Θ(t) is habituation which changes based on gaze history to maintain naturalistic attention shifts.
<p align="center">
  <img src="files\TIC\TIC_proximity_eqn.png" width="1000" alt="Proximity Equation">
  <br>
  <em>Figure 2: Proximity Equation</em>
</p>

<p align="center">
  <img src="files\TIC\TIC_torso_and_hand_motion.png" width="1000" alt="Torso and Hand Motion Equation">
  <br>
  <em>Figure 3: Torso and Hand Motion Equation</em>
</p>
Habituation, Θ(t), avoids sustained attention on a single user. γ = 1 for currently attended individual and 0 for others, m hab controls the negative decay rate and m rest the positive recovery rate.
<p align="center">
  <img src="files\TIC\TIC_habituation_eqn.png" width="1000" alt="Habituation Equation">
  <br>
  <em>Figure 4: Habituation Equation</em>
</p>
Robotic Gaze Algorithm:
Maps 3D target positions to joint-space postures, allowing robot to orient toward salient individuals. Arousal modulates posture and motions dynamics: low is subdued and high increases speed and reach. Sinusoidal oscillation is applied to simulate breathing. 
Attentional Drift Module: 
Avoid mechanical stiffness, naturalistic variability into gaze behavior – momentary attentional shift without disrupting motion continuity.

## User Study
1.	Low Attention + Low Arousal: minimal movement with no sustained orientation toward the participant
2.	Low Attention + High Arousal: energetic and expansive motion without directed attentional engagement
3.	High Attention + Low Arousal: Calm, sustained orientation toward the participant with restrained motion
4.	High Attention + High Arousal: Highly energetic motion combined with sustained attentional focus
Users preferred systems that are attentive without being overstimulating: high attention and low arousal.

