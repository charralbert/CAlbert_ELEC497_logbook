---
title: "Research and Work"
date: 2026-07-22
week: 10
contributors: [Charlotte]
---
# The Thought Process
What originally guided my thinking was:
- How can we see robots as a character and less "robotic"
My initial thought was: we will not ever truly get away from "robot" when working with a robot unless its completely in disguse - the UR5e arm will always be seen as a robot - but how can we make this robot meaningful, how can we see it as guided by its own decision? Think of Wall-E, he will always be a robot - but above all he is a character, guided by his own decisions.

Following this, I thought mostly about animals - potentially guided by my own issues with robots that imitate humans, its weird and offputting. To me, robots are easier to like when they resemble an animal. I was trying to find some persona to give it when I came across the paper: Personality Research in Mammalism Farm Animals: Concepts, Measures, and Relationship to Welfare. They define four different Identity Profiles of goats: Aggressive, Affiliative, Passive, and Avoiders.(https://pmc.ncbi.nlm.nih.gov/articles/PMC6031753/)

In conversation with Matt, "trust" is mentioned a lot in Human-Robot Interaction. How can we get people to trust this robot? Mistrust is a detriment in building a Human-Robot Relationship. In my brainstorm, I thought instead - what if we flipped this narrative and focused on the human trying to get the robot to trust them? I went with this idea for a couple reasons:
- It was interactive in a way I felt I could apply - as my first time working with robots, I was trying to find a good balance of feeling like this was an interaction without it being too complicated to make over the summer. 
- It forces the user to view the robot in a different way, instead of the robot being the "source of contention," the user would be. The focus is more distributed between the user and robot rather than just the robot - "it seems scared... am I too close? Maybe I should back up. It still seems scared - oh it's turning closer!" 
- Building trust is realistic, most robots automatically trust you but this is not the case for the majority of people and animals, a lot of the time you have to build some rapport to have this emotional connection to it. I thought that this emotional connection would be strongest if both parties are building trust with the other - reciprocation. 
- My original plan was to make all identity profiles: affiliative, aggressive, avoidant, and passive to compare how building trust between different personalities affects how the user sees this robot. Would seeing an aggressive robot become more trusting of you feel rewarding? Even if the first interaction was scary. Would seeing a really scared robot become happy to see you feel more rewarding? Or would a robot that's already happy around you be the best? 

I ended up choosing avoidant because I have often seen videos of rescuers building a relationship with a scared stray animal, there is often a very positive public reaction (lots of likes and many comments). 

## Research and How it Guided the Thought Process

### The Relationship of Animals and Humans
Human animal relationships are not new - wild and tamed animals as companions.
**Biophilia Hypothesis**
"Human beings have an innate propensity to attend to and be attracted by other animals and living things" - the key point here being "other animals"
**Applications**
- "Animal assisted intervention for children with Autism. Children can be rejected and victimized by peers..." - in this situation it would allow for children with ASD to learn boundaries without any repercussions.
link: https://www.sciencedirect.com/science/article/pii/S155878781000016X

### The Definition of Trust:
- the "Willingness of an entity" to become vulnerable to another entity. In taking this risk, the trustor presumes the trustee will act in a way that is conducive to the trustor's welfare despite the trustee's actions being outside the trustor's control.
link: https://www.mdpi.com/2306-7381/12/6/586

- "An individual's positive evaluation of others and the belief that these will fulfill their obligations when it matters. The elements of trust include the trustor's willingness to trust others, positive inferences about the trustee, and the trustor's ability to tolerate uncertainty."
- "Trust is a key factor in promoting relationship stability and quality."
- "Trust promotes the maintenance and development of intimacy in relationships"; Intimacy: "emotional closeness and support, has been shown to enhance the stability and quality of relationships, while trust serves as a fundamental element in maintaining and strengthening interpersonal bonds"
link: https://www.clausiuspress.com/assets/default/article/2024/05/19/article_1716108953.pdf

## Research and how it guided my stack

### Trust Levels
The trust levels explore the change from Maslow's Hierarchy of Safety Needs to Love and Belongingness. Trust levels 0 and 1 represent the robot seeking safety needs. 2 and 3 represent the robots transition from seeking safety needs to seeking love and belongingess. And trust levels 4 and 5 represent the robot seeking love and belongingness.
**Maslow's Hierarchy**
2. Safety Needs
- Security, stability, protection from danger
3. Love and Belongingness
- Relationships, intimacy, group belonging
link: https://www.mdpi.com/2306-7381/12/6/586

### Changing Between Trust Levels
"All animals must assess physical threat prior to engaging in trust at higher levels... basic physical safety is established and individuals recognize that the other party is not a threat... includes fragility where trust is subject to changes based on continued interactions, exchanges, and experiences and basic concepts of trust within interactions that align with threat assessment... this stage is established when... animal is willing to engage of their own volition... an individual who does not feel safe... will either cease to move towards or move away" " 
link: https://www.mdpi.com/2306-7381/12/6/586

### How to Gain Trust
- "physical proximity aligns with physical safety... allow freedome of movement to provide individuals with the ability to choose level of space needed to feel physically safe... assessing behavioral responses at different proximities and adjusting space to allow for increased feeling of safety."
- "through the establishment of consistent interactions and corresponding consistent reponses, each individual can better assess the intion of the other based on approach, retreat, and other behaviors that indicate intion, motivation or emotion." Be as consistent and predictable as possible.
- "The closer the individual, the higher the potential threat. How an individual approached and maintains proximity can provide additional information as to the subjective experience of safety of the individual, with fear responses often resulting in behaviors that decrease proximity"

- "If physical safety has been established through repeated interactions, additional communication may be developed that aligns with other emotions such as play, lust, grief, or even caregiving."
link: https://www.mdpi.com/2306-7381/12/6/586

### Types of Behaviors
**Stress**
shivering, pacing, increased respiration (panting, changes in posture)
link: https://www.tandfonline.com/doi/full/10.1080/09712119.2025.2583108#abstract
Tremble, panting, (pacing, shake-off, raising fur)
link: https://www.sciencedirect.com/science/article/pii/S1558787823001491

**Neutral**
- Eye-contact, Tail wag, (accepting treats, physical contact)

**Positive**
- Playing, exploring, tail wag
link: https://www.sciencedirect.com/science/article/pii/S1558787823001491
- animals show voluntary approach and spatial proximity and signs of anticipation, pleasure, relaxation, or other indicators of a rewarding experience arising from interacting with the human.
link: https://www.frontiersin.org/journals/veterinary-science/articles/10.3389/fvets.2020.590867

**Other notes**
Chronological order associated with a position HAR:
1. animal shows signs of anticipation before interaction in cases when HI predictable (pacing, vocalizations)
2. Orientation response - turns attention toward the human. Head, ear, body posture 
3. "Latency to approach - voluntary seeking behavior of the animal. Lack of approach does not preclude a position HAR but may just indicate low motivation. 
An animal approach and interacting with a human is a prime indicator of a positive HAR. Not sufficient to qualify as a specific positive HAR because may just be out of curiousity"


## What should I change to current implementation

- Make sure that no go zone is fluently implemented. 
- Make sure scared reaction is fluently implemented.
- Add adjustment to base to TL3, then constant adjustments to always be facing user in TL4 and TL5. 
- Only look at appendages if moving fast... otherwise look at face. 

- go towards ASD, testing connection - search about robots specifically and autism. 

design experiment:
- test connection, social perception, companionship, 

Find instruments or tools for companionship, trust

update question accordingly.. does trust create a meaningful relationship with the robot. 

### Session 1: [Activity Name] (HH:MM - HH:MM)

**Members Present**: [Name1, Name2, Name3]

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