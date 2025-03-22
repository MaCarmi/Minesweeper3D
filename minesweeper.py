import sys
import math
from random import randrange, uniform
from functools import partial

from ursina import *


DEBUG = True


app = Ursina()

## Variabili globali

dim  = 8
side = 0.5
gap  = 0.08

difficulty = {
    'easy':    0.10,
    'medium':  0.15,
    'hard':    0.20,
    'extreme': 0.30
}

mines = difficulty['easy'] * dim * dim * dim

center = (dim - 1) * side / 2

rotation_speed = 50
zoom_speed = 0.2
min_zoom = 1
max_zoom = 50

## Flag Mode
global_flag_mode = False
flag_text = Text(text="Flag mode OFF", position=(-0.7, 0.45), scale=2, color=color.white)

## Funzioni e classi

class Cube(Entity):
    def __init__(self, position, id, **kwargs):
        super().__init__(
            model='cube',
            color=color.random_color(),
            scale=(side - gap, side - gap, side - gap),
            position=position,
            parent=pivot,
            collider='box',
            is_mine=False,
            **kwargs
        )
        self.id = id
        self.is_flagged = False
        self.is_revealed = False

    def reveal(self):
        if self.is_flagged:
            return

        x, y, z = map(int, self.id.split('_'))
        count = 0

        self.is_revealed = True

        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                for k in range(z - 1, z + 2):
                    if (i, j, k) == (x, y, z):
                        continue

                    cube = cubes_dict.get((i, j, k))
                    if cube and cube.is_mine:
                        count += 1

        if count > 0:
            self.text_entity = Text(
                text=str(count),
                position=self.position,
                scale=side * 20,
                parent=pivot,
                billboard=True,
                color=color.white
            )
        else:
            flood_fill(x, y, z)

        if DEBUG:
            print(f'Clicked {self.id}, Mines around: {count}, Is mine: {self.is_mine}, Revealed {self.is_revealed}')

        destroy(self)

    def on_click(self):
        global global_flag_mode

        if global_flag_mode:
            self.is_flagged = not self.is_flagged
            self.color = color.red if self.is_flagged else color.white

            for cube in cubes_dict.values():
                if cube.is_revealed and hasattr(cube, 'text_entity'):
                    count = int(cube.text_entity.text)
                    if self.is_flagged:  # Se è stato piazzato un flag, riduci di uno il numero
                        cube.text_entity.text = str(count - 1)
                    else:  # Se il flag è stato rimosso, aumenta di uno il numero
                        cube.text_entity.text = str(count + 1)

        else:
            self.reveal()

def input(key):
    global global_flag_mode
    if key == 'space':
        global_flag_mode = not global_flag_mode
        flag_text.text = "Flag mode ON" if global_flag_mode else "Flag mode OFF"
        print(f'Modalità flag: {global_flag_mode}')

def flood_fill(x, y, z):
    stack = [(x, y, z)]
    visited = set()

    while stack:
        cx, cy, cz = stack.pop()

        if (cx, cy, cz) in visited:
            continue
        visited.add((cx, cy, cz))

        cube = cubes_dict.get((cx, cy, cz))

        cube.is_revealed = True

        print(f'Popped {cube.id}, Revealed {cube.is_revealed}')

        if not cube or cube.is_mine:
            continue

        count = 0
        for i in range(cx - 1, cx + 2):
            for j in range(cy - 1, cy + 2):
                for k in range(cz - 1, cz + 2):
                    if (i, j, k) == (cx, cy, cz):
                        continue

                    neighbor = cubes_dict.get((i, j, k))
                    if neighbor and neighbor.is_mine:
                        count += 1

        if count > 0:
            cube.text_entity = Text(
                text=str(count),
                position=cube.position,
                scale=side * 20,
                parent=pivot,
                billboard=True
            )
        else:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == dy == dz == 0:
                            continue
                        nx, ny, nz = cx + dx, cy + dy, cz + dz
                        if (nx, ny, nz) not in visited and (0 <= nx < dim and 0 <= ny < dim and 0 <= nz < dim):
                            stack.append((nx, ny, nz))

        destroy(cube)

if __name__ == '__main__':

    pivot = Entity(
        position=(center,center,center),
    )

    camera.parent = pivot
    camera.position = (center, 20, center) 
    camera.look_at(pivot)

    cubes_dict = {}

    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                cube = Cube(
                    position=(x * side, y * side, z * side),
                    id=f'{x}_{y}_{z}'
                )
                cubes_dict[(x, y, z)] = cube

    for _ in range(int(mines)):
        cube = cubes_dict.get((randrange(dim), randrange(dim), randrange(dim)))
        cube.is_mine = True

    def update():
        if held_keys['w']:
            camera.position += camera.up * time.dt * 50
        if held_keys['s']:
            camera.position -= camera.up * time.dt * 50

        if held_keys['a']:
            camera.position -= camera.right * time.dt * 50
        if held_keys['d']:
            camera.position += camera.right * time.dt * 50

        if held_keys['up arrow']:
            camera.world_position += camera.forward * zoom_speed
        if held_keys['down arrow']:
            camera.world_position -= camera.forward * zoom_speed

        camera.look_at(pivot)

    app.run()
