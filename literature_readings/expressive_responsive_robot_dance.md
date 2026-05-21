# How can we Make Robot Dance Expressive and Responsive?

citation: Wallace B, Glette K and Szorkovszky A (2025) How can we make robot dance expressive and responsive? A survey of methods and future directions. Front. Comput. Sci. 7:1575667. doi: 10.3389/fcomp.2025.1575667
https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2025.1575667/full

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

**Latent Space**: A hidden compressed representation of movement, instead of storing every detail directly, the AI learns underlying movement structure. 

Primitives can be learned through automated segmentation of longer demonstrations, using techniques such as change-point detection. Recent work in 3D animation and robot simulation has used vector-quantized autoencoders to learn a range of primitives from human movement datasets, also incorporating latent spaces.

For robot dance, movement primitives have been used to incorporate principles of specific dance styles such as neoclassical and tango, albeit in a hand-crafted way. Modulating certain movement primitives in their speed or amplitude can imbue the motion with affective and expressive qualities. Depending on how feedback is implemented, primitives can be made more or less responsive to external influences such as engagement, tactile feedback, or musical features.

### Movement Sequence Generation
Movement data can also be represented as a sequence by segmenting dance recordings into sequences of individual poses/MPs. In animation, generative movement models have been used to create realistic, fluid movements for characters, allowing for lifelike motion in films. Automatic generation of movement for robot control using deep learning has also emerged.

### Entrainment
Refers to general ability for an oscillating system to adapt its frequency to that of an external stimulus. 
1. Uses adaptive feedback to adjust an intrinsic oscillation frequency - has been used to find natural walking frequency for a given robot weight.
2. Self-organized responses of dynamical systems such as coupled oscillators. Been applied using gradient frequency networks.
Generally, nonlinear neural-like oscillators, when connected correctly, have a tendency to synchronize. Neural circuits governing vertebrate locomotion, known as central pattern generators (CPGs), can also show entrainment to a wide range of rhythmic stimuli when their parameters and weights are evolved for this property.

### Imitation
Motion characteristics of a partner need to be recognized through the senses, then reproduced by oneself. Mapping can occur on various levels of abstraction, from pure motion trajectories, to classifiable gestures or movement primitives, to achievement of a goal. For dance, lower level mapping is the most relevant, as in this case motion is not necessarily connected to function.

**Motion Retargeting**
For humanoids: one-to-one low-level mapping using inverse kinematics. Incorporating prediction into model, a robot can anticipate the partner's motion. 
For non-humanoid robots, analogous movement primitives can in principle be learned. Laban movement analysis can also be used to describe the characteristics of the motion to be matched. 

### Stabilization
Legged robots keep center of mass - continuous feedback control is ubiquitous for robots in industrial settings. relies on hand-designed motion plans so that the kinematic equations and necessary feedbacks are known. ML approaches (reinforcement learning) have been used to find motion plans and corresponding feedback

### Spatial Awareness
Recent adnaces have incorporated tactile and haptic sensors to enable robots to detect and respond to proxemic cues in partner dance scenarios. 

### Improvisation
The ability to respond spontaneously without a predefined plan. During training and ideation stage for choreographic development, improvisation often plays a central role. Robot's ability to perform unexpected and surprising movements may be favorable compared to more predictable movement patterns. 
In order to achieve more surprising and interesting interactions, previous work has leveraged the power of generative AI. 

## Discussion
Quantitative measures that capture aspects of expressive movement can be derived based on Laban movement analysis or animation principles. Entropy measures can then capture the overall utilization of the affective spaces that span a range of qualities or a learned set of motion primitives. 
Due to the subjective nature of expressiveness, these should be combined with surverys following performance and interaction studies. Metrics that capture responsiveness include Granger causality for low-dimensional data such as agent position and Markov-based conditional independence for higher-dimensional data such as motion capture. It is likely that these methods would need to be complemented with measures of entrainment such as mean asyncrhony, as synchronized repetitive motion will eliminate the temporal differences used to infer causality.

### Table listing promising methods
online = while robot is functioning
offline = before deployment

Ability: Movement primitive learning
Impact on responsiveness: Either
Impact on expressiveness: Increases
Methods: 
- Trajectory learning - training off and online
- Latent variable models - offline

Ability: Entrainment
Impact on responsiveness: Increases
Impact on expressiveness: Decreases
Methods: 
- Phase feedback CPGs - online
- Self-organized CPGs - offline

Ability: Motion recognition
Impact on responsiveness: Increases
Impact on expressiveness: Either
Methods: 
- Pose estimation - offline
- Motion capture system - none

Ability: Motion retargeting
Impact on responsiveness: Increases
Impact on expressiveness: Either
Methods: 
- Inverse kinematics - either
- data-driven - offline

Ability: Sequence generation
Impact on responsiveness: Decreases
Impact on expressiveness: Increases
Methods: 
- RNNs - offline
- Transformers - offline
- evolutionary algorithms - offline

Ability: Stabilization
Impact on responsiveness: Increases
Impact on expressiveness: Decreases
Methods: 
- Optimal control - either
- Reinforcement learning - online

Ability: Spatial awareness
Impact on responsiveness: Increases
Impact on expressiveness: Either
Methods: 
- Tactile sensors - None
- Haptic Sensors - None

Ability: Improvisation
Impact on responsiveness: Decreases
Impact on expressiveness: Increases
Methods: 
- Sampling Strategies - either
- Evolutionary algorithms - online

A combination of abilities is clearly required to allow a high degree of both qualities. In order to make these compatible , it is necessary to identify shared computational method and principles. 

**Latent Spaces**: low-dimensional representations that capture variation or structure in data, well suited to the high dimensional spatiotemporal data encountered in the study of movement. Been used for learning MPs, imitation, and improvisation

**Hierarchical Control**: Divides control problem into that of low-level movement aided by proprioceptive feedback and high level movement selection. Enables entrainment and sequence generation to be executed at the level of discrete motions, with expressivity and stabilization delegated to a continuous control scheme.

**Online Adaptivity**: A fully improvisational and interactive dancing robot would need to monitor its performance at runtime and manage tradeoffs. An architecture considering computational self-awareness could be a relevant framework in the design process. Since it is difficult to optimize several abilities simultaneously, it would also be useful to include some modules pre-trained offline, leaving continuous learning for modules where this is most important.

**Morphology dependence**: Given a common framework for movement, how can we apply to other forms than humanoid?

**Latency**: responsive motion requires fast motors and rapid computation. Low-cost platforms can be made rapidly responsive, expressiveness may be limited due to lack of computational power.

**Context-aware motion planning**: The future robot dancer that we imagined would require a context-rich state variable to allow flexibility in where and how it moves ahead in time.