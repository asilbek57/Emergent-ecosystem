# Emergent-ecosystem
A small artificial-life simulation in Python and pygame. Cells search for food, reproduce, and pass mutated traits to their offspring. Over many generations, selection shapes the population.

Overview

Cells live on a grid and spend energy every tick. They find the nearest food within their vision radius using Euclidean distance and step toward it, or wander randomly when none is in range. A cell that reaches enough energy splits it with a child, which inherits the parent's genome with a small random mutation. The genome holds two genes, speed and vision, and each can shift by one per generation. Cells that find food efficiently pass on their traits, and cells that starve do not. A cell's brightness on screen shows its current energy.

Getting started

Requirements: Python 3.9 or newer and pygame.

bash
pip install pygame
python main.py

Replace main.py with the name of your script. Close the window to quit.

How it works

Each tick, the world does the following in order:

Every cell ages, loses 1 energy, and dies if its energy reaches 0.
Every living cell looks for the closest food within genome.vision and moves one step toward it, or moves randomly if none is in range.
Every cell with at least 150 energy reproduces. The parent keeps half its energy, and the child starts with that amount and a mutated genome.
Cells standing on food eat it and gain 50 energy.
Every second tick, one new food item spawns at a random position.
Concept	Implementation
Cell	Position, energy, age, and a Genome
Genome	Heritable traits (speed, vision) and the mutation rule in inheritance()
World	Grid size, the list of cells and food, and the update steps above
Configuration

Constants at the top of the file control the simulation:

Constant	Meaning	Default
GRID_WIDTH, GRID_HEIGHT	World size in grid squares	120, 67
CELL_SIZE	Pixels per grid square	16
FPS	Simulation ticks per second	10

The starting population (300 cells), starting energy (100), reproduction threshold (150), and food energy (50) are set in the code and can be changed there.

Roadmap
 Energy costs for speed and vision, so traits trade off against each other instead of only growing
 Average gene values logged over time, with a plot
 A fading trail layer (NumPy) that cells leave behind and can sense, inspired by slime-mold simulations
 Food that spawns in patches, so trails carry useful information
 Experiment: compare gene evolution with the trail enabled and disabled
Inspiration
Sebastian Lague, Coding Adventure: Ant and Slime Simulations: pheromone trails and agent-based pattern formation
Brainxyz, Create a Life from a Simple Rule: emergent behavior from simple interaction rules

<video src="https://raw.githubusercontent.com/asilbek57/Emergent-ecosystem/main/simulation.mp4" controls autoplay loop muted playsinline width="100%"></video>
