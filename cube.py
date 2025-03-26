from ursina import *
import random
import sys

from config import dim
import config


DEBUG = True


def flood_fill(x, y, z, side, cubes_dict, pivot):
    stack = [(x, y, z)]
    visited = set()

    while stack:
        cx, cy, cz = stack.pop()

        if (cx, cy, cz) in visited:
            continue

        visited.add((cx, cy, cz))
        cube = cubes_dict.get((cx, cy, cz))
        cube.is_revealed = True

        if DEBUG:
            print(f"Popped {cube.id}, Revealed {cube.is_revealed}")

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
                billboard=True,
            )
        else:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == dy == dz == 0:
                            continue
                        nx, ny, nz = cx + dx, cy + dy, cz + dz
                        if (nx, ny, nz) not in visited and (
                            0 <= nx < dim and 0 <= ny < dim and 0 <= nz < dim
                        ):
                            stack.append((nx, ny, nz))

        if cube:
            cube.disable()


class Cube(Entity):
    def __init__(self, side, gap, position, id, colors, pivot, **kwargs):

        self.id = id
        self.cubes_dict = None
        self.side = side
        self.gap = gap
        self.pivot = pivot

        rand_color = random.randint(0, len(colors) - 1)
        random_variable = random.uniform(0.3, 0.9)

        super().__init__(
            model="cube",
            color=lerp(color.black, colors[rand_color], random_variable),
            scale=(side - gap, side - gap, side - gap),
            position=position,
            parent=pivot,
            collider="box",
            is_mine=False,
            **kwargs,
        )

        self.is_flagged = False
        self.is_revealed = False
        self.initial_value = 0

    def reveal(self):
        if self.is_flagged:
            return
        
        if self.is_mine:
            self.color = color.black
            print("Game Over")
            # sys.exit()
            return

        x, y, z = map(int, self.id.split("_"))
        count = 0

        self.is_revealed = True

        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                for k in range(z - 1, z + 2):
                    if (i, j, k) == (x, y, z):
                        continue

                    cube = self.cubes_dict.get((i, j, k))
                    if cube and cube.is_mine:
                        count += 1

        if count > 0:
            self.text_entity = Text(
                text=str(count),
                position=self.position,
                scale=self.side * 20,
                parent=self.pivot,
                billboard=True,
                color=color.white,
            )
            self.initial_value = count
        else:
            flood_fill(x, y, z, self.side, self.cubes_dict, self.pivot)

        if DEBUG:
            print(
                f"Clicked {self.id}, Mines around: {count}, Is mine: {self.is_mine}, Revealed {self.is_revealed}"
            )

        self.disable()

    def get_neighbors(self):
        x, y, z = map(int, self.id.split("_"))
        neighbors = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                for k in range(z - 1, z + 2):
                    if (i, j, k) == (x, y, z):
                        continue
                    cube = self.cubes_dict.get((i, j, k))
                    if cube:
                        neighbors.append(cube)
        return neighbors

    def on_click(self):
        if config.global_flag_mode:
            self.is_flagged = not self.is_flagged
            self.color = color.red if self.is_flagged else color.white

            for cube in self.get_neighbors():
                if cube.is_revealed and hasattr(cube, "text_entity"):
                    count = int(cube.text_entity.text)
                    print(cube.text_entity.text)

                    if count > 0:
                        new_count = count - 1
                        if new_count == 0:
                            cube.text_entity.disable()
                        else:
                            cube.text_entity.text = str(new_count)

                    else:
                        if count < cube.initial_value:
                            cube.text_entity.text = str(count + 1)

        else:
            self.reveal()
