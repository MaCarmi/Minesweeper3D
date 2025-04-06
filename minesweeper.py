import sys
import math
from random import randrange, uniform, randint
from functools import partial
from ursina import *



DEBUG = True

game_panel = Entity(parent=scene, enabled=False)
game_over_panel = Entity(parent=camera.ui, enabled=False)
menu_panel = Entity(parent=camera.ui)

app = Ursina()

## Il gioco si apre in una finestra window di dimensioni 800x800
window.title = 'Minesweeper'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True
window.color = color.black




## Variabili globali
dim = 5
side = 0.5
gap  = 0.08
revealed_cubes = []
not_revealed_cubes = []
camera_positions = []
difficulty_buttons = []
colors = {
    1: color.green,
    2: color.yellow,
    3: color.orange,
    4: color.cyan,
    5: color.magenta,
}


rand_color = randint(1,5)



difficulty = 0.10

mines = difficulty * dim * dim * dim
center = (dim - 1) * side / 2
rotation_speed = 50
zoom_speed = 0.2
min_zoom = 1
max_zoom = 50

#Game over text
game_over_text = Text(
        text='Game Over!',
        x = -0.15,
        y = 0.15,
        scale = 2,
        visible = False,)



## Flag Mode
global_flag_mode = False
flag_text = Text(text="Flag mode OFF", position=(-0.7, 0.45), scale=2, color=color.white)
flag_text.visible = False


# Dimensioni delle linee
LINE_LENGTH = 1000
LINE_THICKNESS = 0.05  # Aumenta lo spessore delle linee per renderle più visibili



## Funzioni e classi


    

class Cube(Entity):
    def __init__(self, position, id, **kwargs):
        random_variable = random.uniform(.3 , .9)
        super().__init__(
            model='cube',
            color=lerp(color.black, colors[rand_color], random_variable),
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
        #Creiamo comunque text_entity per ogni cubo, anche se quest'ultimo è vuoto 
        self.text_entity = Text(
            text='',
            position=self.position,
            parent=self,
            scale=0.1,
            visible=False
        )
    
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
            self.initial_value = count
        else:
            flood_fill(x, y, z)
        if not DEBUG:
            print(f'Clicked {self.id}, Mines around: {count}, Is mine: {self.is_mine}, Revealed {self.is_revealed}')
        self.disable()

        if self.is_mine:
            print('Game Over!')
            game_over()
    
    
    def get_neighbors(self):
        x, y, z = map(int, self.id.split('_'))
        neighbors = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                for k in range(z - 1, z + 2):
                    if (i, j, k) == (x, y, z):
                        continue
                    cube = cubes_dict.get((i, j, k))
                    if cube:
                        neighbors.append(cube)
        return neighbors
    def on_click(self):
        global global_flag_mode
        
        if global_flag_mode:
            self.is_flagged = not self.is_flagged
            self.color = color.red if self.is_flagged else color.black
            
            
                
            for cube in self.get_neighbors():
                if cube.is_revealed and hasattr(cube, 'text_entity'):
                    count = int(cube.text_entity.text)
                    if not DEBUG:
                        print(cube.text_entity.text)
                    
                    if self.is_flagged:  
                        if count > 0:  
                                cube.text_entity.text = str(count - 1)
                        
                    else:  
                        if count < cube.initial_value:
                            cube.text_entity.text = str(count + 1)
                        
        else:
            self.reveal()

def game_over():
    game_panel.enabled = False
    game_over_panel.enabled = True
    flag_text.visible = False
    
    game_over_text.visible = True
    
    restart_button = Button(
        text='Restart game',
        color = color.red,
        parent=game_over_panel,
        scale=.2,
        x = 0,
        y = -0.2,
        on_click=lambda: restart_game()
    )

    for btn in dimension_buttons:
        btn.color = color.violet

    for btn in difficulty_buttons:
        btn.color = color.azure


def restart_game():
    print("Restarting game...")
    game_over_panel.enabled = False
    menu_panel.enabled = True
    game_over_text.visible = False
    destroy_all_game_entities()

def destroy_all_game_entities():
    for e in game_panel.children:
        destroy(e)


def get_revealed_cubes():
        global revealed_cubes  
        revealed_cubes.clear() 
        for cube in cubes_dict.values():
            if cube.is_revealed:
                revealed_cubes.append((cube.id, cube.text_entity.text))
        return revealed_cubes 
def get_not_revealed_cubes():
        global not_revealed_cubes  
        not_revealed_cubes.clear() 
        for cube in cubes_dict.values():
            if not cube.is_revealed:
                not_revealed_cubes.append((cube.id))
        return not_revealed_cubes 

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
        if not DEBUG:
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
            cube.initial_value = count
        else:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == dy == dz == 0:
                            continue
                        nx, ny, nz = cx + dx, cy + dy, cz + dz
                        if (nx, ny, nz) not in visited and (0 <= nx < dim and 0 <= ny < dim and 0 <= nz < dim):
                            stack.append((nx, ny, nz))
        if cube:
            cube.disable()


def set_difficulty(value, selected_button = None):
    global difficulty
    difficulty = value
    print(f'Difficoltà impostata a {difficulty}')

    for btn in difficulty_buttons:
        btn.color = color.azure
    

    if selected_button:
        selected_button.color = color.orange

def set_dimension(value, selected_button = None):
    global dim
    dim = value
    print(f'Dimensione impostata a {dim}')

    for btn in dimension_buttons:
        btn.color = color.violet
    

    if selected_button:
        selected_button.color = color.magenta

def start_game():
    menu_panel.enabled = False
    game_over_panel.enabled = False
    
    game_over_text.visible = False
    global camera, pivot, cubes_dict, mines, center, global_flag_mode, flag_text, mines, difficulty, dim
    

    #Rendo visibile la modalità flag all'inizio del gioco
    flag_text.visible = True

    mines = difficulty * dim * dim * dim
    center = (dim - 1) * side / 2

    pivot = Entity(
        parent=game_panel,
        position=(center,center,center),
    )
    camera.parent = pivot
    if dim == 5:
        camera.position = (center, 20, center) 
    elif dim == 7:
        camera.position = (center, 23, center)
    elif dim == 9:
        camera.position = (center, 25, center)
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
    if DEBUG: 
        print(camera.position)
    
    def update():
        
        if not game_panel.enabled:
            return  # non fare nulla se il gioco è fermo

        ## MOVIMENTO WASD
        if held_keys['w']:          
            camera.position += camera.up * time.dt * 50
            camera.position += camera.forward * zoom_speed * .12           
        if held_keys['s']:
            camera.position -= camera.up * time.dt * 50
            camera.position += camera.forward * zoom_speed * .12
        if held_keys['a']:
            camera.position -= camera.right * time.dt * 50
        if held_keys['d']:
            camera.position += camera.right * time.dt * 50
        if held_keys['up arrow']:
            camera.world_position += camera.forward * zoom_speed
        if held_keys['down arrow']:
            camera.world_position -= camera.forward * zoom_speed
        # Mantiene la telecamera rivolta al centro
        camera.look_at(pivot)
    
    def input(key):
        global global_flag_mode
        if key == 'space':
            global_flag_mode = not global_flag_mode
            flag_text.text = "Flag mode ON" if global_flag_mode else "Flag mode OFF"
            print(f'Modalità flag: {global_flag_mode}')
    
    globals()['update'] = update
    globals()['input'] = input

    game_panel.enabled = True

if __name__ == '__main__':

    
    game_over_text.visible = False
    

    start_button = Button(
        text='Inizia Gioco',
        color = color.azure,
        parent=menu_panel,
        scale=.2,
        x = 0,
        y = -0.2,
        on_click=lambda: start_game()
    )

    easy_button = Button(
        text='Facile',
        color = color.azure,
        parent=menu_panel,
        scale=.15,
        x = -0.4,
        y = 0.2,
        on_click= lambda: set_difficulty(0.10, easy_button)
            
    )
    
    medium_button = Button(
        text='Medio',
        color = color.azure,
        parent=menu_panel,
        scale=.15,
        x = -0.1275,
        y = 0.2,
        on_click=lambda: set_difficulty(0.15, medium_button)
    )
    
    hard_button = Button(
        text='Difficile',
        color = color.azure,
        parent=menu_panel,
        scale=.15,
        x = 0.1275,
        y = 0.2,
        on_click=lambda: set_difficulty(0.20, hard_button)
    )
    
    extreme_button = Button(
        text='Estremo',
        color = color.azure,
        parent=menu_panel,
        scale=.15,
        x = 0.4,
        y = 0.2,
        on_click=lambda: set_difficulty(0.30, extreme_button)
    )
    
    exit_button = Button(
        text='Esci',
        color = color.brown,
        parent=menu_panel,
        scale=.07,
        x = 0.7,
        y = -0.35,
        on_click=application.quit
    )

    difficulty_buttons = [easy_button, medium_button, hard_button, extreme_button]

    dimension_button0 = Button(
        text='5',
        color = color.violet,
        parent=menu_panel,
        scale=.10,
        x = -0.2,
        y = 0,
        on_click= lambda: set_dimension(5, dimension_button0)
            
    )
    dimension_button1 = Button(
        text='7',
        color = color.violet,
        parent=menu_panel,
        scale=.10,
        x = 0,
        y = 0,
        on_click= lambda: set_dimension(7, dimension_button1)
            
    )
    dimension_button2 = Button(
        text='9',
        color = color.violet,
        parent=menu_panel,
        scale=.10,
        x = 0.2,
        y = 0,
        on_click= lambda: set_dimension(9, dimension_button2)
            
    )
    
    dimension_buttons = [dimension_button0, dimension_button1, dimension_button2]

    app.run()
        
    