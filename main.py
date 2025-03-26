import sys
import math
from random import randrange, uniform, randint
from functools import partial

from ursina import *
from cube import Cube

import config
from config import dim, side, gap, colors, mines, center, rotation_speed, zoom_speed, min_zoom, max_zoom


app = Ursina()

window.title = 'Minesweeper 3D - SAT Solver'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = True
window.fps_counter.enabled = True
window.color = color.black


flag_text = Text(text="Flag mode OFF", position=(-0.7, 0.45), scale=2, color=color.white)


def input(key):
    if key == 'space':
        config.global_flag_mode = not config.global_flag_mode
        flag_text.text = "Flag mode ON" if config.global_flag_mode else "Flag mode OFF"
    
    if key == 'escape':
        application.quit()
        
    if key == 'scroll up':
        camera.world_position += camera.forward * zoom_speed * 3
    if key == 'scroll down':
        camera.world_position -= camera.forward * zoom_speed * 3


if __name__ == '__main__':
    pivot = Entity(
        position=(center,center,center)
    )

    camera.parent = pivot
    camera.world_position = (center, dim * 5, center) 
    camera.look_at(pivot)

    cubes_dict = {}

    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                cube = Cube(
                    side=side,
                    gap=gap,
                    position=(x * side, y * side, z * side),
                    id=f'{x}_{y}_{z}',
                    colors = colors,
                    pivot=pivot
                )
                cubes_dict[(x, y, z)] = cube
    
    for cube in cubes_dict.values():
        cube.cubes_dict = cubes_dict

    for _ in range(int(mines)):
        cube = cubes_dict.get((randrange(dim), randrange(dim), randrange(dim)))
        cube.is_mine = True


    def update():
        if held_keys['w']:
            camera.world_position += camera.up * time.dt * 50
        if held_keys['s']:
            camera.world_position -= camera.up * time.dt * 50

        if held_keys['a']:
            camera.world_position -= camera.right * time.dt * 50
        if held_keys['d']:
            camera.world_position += camera.right * time.dt * 50

        if held_keys['up arrow']:
            camera.world_position += camera.forward * zoom_speed
        if held_keys['down arrow']:
            camera.world_position -= camera.forward * zoom_speed

        camera.world_position = camera.world_position.normalized() * clamp(camera.world_position.length(), min_zoom, max_zoom)
        camera.look_at(pivot)
    
    app.run()