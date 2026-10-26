# Emergent-ecosystem
A small personal project about emergent behavior of artificial cells. It is created for personal interest and experimenting.
It is only inspired by the real evolution, so it is not as complex. I was also inspired to create it by the Youtube creator Emergent Garden. All of the code was written in Python.


The simulation is built around a  **Object-Oriented Architecture**
For the start, this simulation has two classes: 
Cell : Individual organisms that track x , y positions. Their color is green that gradually blacks out as their energy drops down.
Population : designed to hold cells and operate an entire group of them. For visualising them, pygame was used. 
With pygame graphics engine, a black screen is created for now, where green cells appear. The population is created at random positions across the screen to make each running session a little different. Clock-based FPS regulation was added to control simulation speed and timing. Each second a certain action is repeated, like aging or energy drop. For now, cells die out after a few seconds as their energy levels drop.

What has to be done next is the movement of the cells. They do not interact with one another at any way, so I will add a movement for them.
