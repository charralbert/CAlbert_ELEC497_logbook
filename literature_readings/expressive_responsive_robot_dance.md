# How can we Make Robot Dance Expressive and Responsive?

citation: Wallace B, Glette K and Szorkovszky A (2025) How can we make robot dance expressive and responsive? A survey of methods and future directions. Front. Comput. Sci. 7:1575667. doi: 10.3389/fcomp.2025.1575667

## Abstract
The article reviews recent advances in robotics, AI, and HRI toward enabling various aspects of realistic dance, and examines potential paths toward a fully embodied dancing agent. Outlines essential abilities for human-like dance movements, summarized under the terms expressiveness and responsiveness. 

## Introduction
Dance can help to free HRI from cultural expectations such as human-ness, machine-ness, and efficiency.
Consider a standard HRI interaction context, where robots are distinct from any human performers. While morphology has a profound influence on affective qualities, we are most interested in control methods that are morphology-independent and hence as widely applicable as possible.

**Expressiveness**:
The agent's ability to move in a manner that conveys thought or feeling. Highly expressive robots should be able to signal agency and express a wide variety of emotional affect. Requires high level of variability, flexibility, and complexity. The dimensions of expressiveness can be captured in various ways, such as the 12 principles of animation or Laban movement analysis.

**Responsiveness**:
Current neuroscientific theory posits that music and dance help to train predictive networks in the brain, which may explain the pleasure associated with sensorimotor entrainment or "groove." This points to real-time responsiveness as another fundamental aspect of human dance. We define responsiveness as movement initiated by external stimulus, or modified in response to changing stimulus. The appropriateness of the timing of response is generally important. Also, awareness of context, not all stimuli are treated equally. 

## Dance-related Abilities in Robots: SOTA

### Movement Primitive Learning
Discrete building blocks such as stepping, reaching, or kicking, which can be combined into complex movements. Division of movement leads to hierarchical control schemes, where a high-level controller selects and sequences actions, and low-level controllers execute them with the necessary proprioceptive feedback as input. 

A common method to learn and generate primitives in robots is to learn a trajectory in a low-dimensional space (like hand position) which is then transformed into a stable attractor of a dynamical system in this space. In doing so, the system makes use of motor synergies, such that groups of associated joints do not need to be controlled independently. Traditionally, the spaces are specified manually, recent work uses unsupervised learning to find reusable low-dimensional latent spaces.