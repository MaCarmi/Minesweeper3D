# Minesweeper3D
Minesweeper 3D created with Python using Ursina library 

We created a cube made up by NxN cubes. Each cube is an entity that is flagged with the property of being a mine or not. 
The mines are generated randomly but the quantity depends on the difficulty of the game, we used the parameters {easy : 0.1, medium : 0.15, hard : 0.2, extreme : 0.3} that is multiplied by the 3 dimensions.

The game use the "flood fill" algorithm which destroys every cube that doesn't have any mines in the vicinity. 
We created a flag mode, activable by a button on screen or by pressing the space bar, in this mode, every time a cube is clicked it become red. 

## TO BE ADDED ## 
Every time a cube is flagged, all the numbers in the vicinity are decreased by one. \
Button "Resolve" that, thanks to Z3 - SAT solver solves the current minesweeper game. Looking forward to add the possibility to get some hints to resolve the game partially.

## TO BE IMPROVED ##
The graphics, the lights and shadow and the user interface




Created by Giovanni Norbedo and Marco Carmignano, students of Artificial Intelligence and Data Analytics at the University Of Trieste
