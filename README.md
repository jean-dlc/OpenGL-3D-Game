## OpenGL-3D-Game

3D Image Synthesis Project
Module: TSI (Signal and Image Processing)
Authors: Lucic Arthus, De la chapelle Jean

## Project Overview
This project is a 3D platforming game developed in Python using the OpenGL API. The gameplay is inspired by Minecraft "jump" maps, where the player controls a sphere and must navigate through a course of cubes. The objective is to reach the finish platform in the shortest time possible.

## Technical Implementation
The project implements several core computer graphics and game engine concepts:
* **Graphics API:** OpenGL via the ModernGL and PyOpenGL libraries.
* **Shaders:** Custom GLSL implementation (vertex and fragment shaders) for object rendering.
* **Physics Engine:** Real-time gravity simulation and sphere-to-cube collision detection.
* **Mathematics:** Matrix transformations and camera projections handled via the Pyrr library.
* **Data Management:** Level layouts are stored and loaded using JSON files.

## Controls and Modes

### Game Mode (Default)
* **Player Movement:** Z, Q, S, D (Forward, Left, Backward, Right)
* **Jump:** Spacebar
* **Timer:** Automatically starts and stops when crossing the edges of the start and finish platforms.

### Editor Mode (Toggle: M)
* **Add Block:** E
* **Remove Block:** R
* **Save Map:** P (Exports current layout to a JSON file)
* **Load Map:** L (Refreshes map from the saved JSON file)

### Free Camera Mode (Toggle: N)
* **Movement:** Z, Q, S, D
* **Vertical Movement:** A (Up), W (Down)

## Installation
The following dependencies must be installed on your system Python environment:

```bash
pip install PyOpenGL PyOpenGL_accelerate glfw pyrr moderngl numpy