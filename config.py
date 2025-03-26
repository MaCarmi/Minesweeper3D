from ursina import color

global_flag_mode = False

dim  = 3     # lato del cubo
side = 0.5   # dimensione del lato
gap  = 0.08  # spazio tra i cubi

colors = [
    color.blue,
    color.green,
    color.yellow,
    color.orange,
    color.cyan,
    color.magenta
]

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