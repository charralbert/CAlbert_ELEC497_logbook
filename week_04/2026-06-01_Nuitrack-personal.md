---
title: "Can I get it to work on my computer?"
date: 2026-06-01
week: 4
contributors: [Charlotte]
---

### Charlotte's 'puter runs nuitrack?

**Things Learned**: 
Sometimes I do things in engineering without really understanding what is happening, so I decided to write down some of the things that I should probably know.

What is Free Glut?
open-source alternative to the OpenGL utility toolkit. OpenGL (open graphics library) is a cross-platform API for rendering 2D and 3D graphics. 

What is Ubuntu?
An open-source OS based on Debian Linux distribution. 

**Process/Steps**:
1. Install a bunch of things... (Ros, Visual Studio, Nuitrack)
2. Fix broken website path on Nuitrack github page (looked for freeglut on a website that didn't exist)
3. I was able to run NuitrackGLSample.cpp!!!!!!! it was lowk chopped and bad but like it ran #yes
4. I was not able to run anything with the camera through Roy's code because its made for linux environment and wsl hates usb connections so... ts no working

**Pivoting**:
I am going to make my own script to do what Nuitrack demo does basically. 

*Figure 1: Brief description of what the image shows and its relevance to your work*

### Code Snippets

```python
$env:Path += ";C:\Program Files\CMake\bin"
```
```python
wsl -d Ubuntu
```

---

**Entry completed**: 2026-06-01 4:30