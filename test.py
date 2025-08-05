import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import sys
import numpy as np

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluOrtho2D(-1, 1, -1, 1)
glClearColor(0.1, 0.1, 0.1, 1.0)

# Game state
catcher = {'x': 0, 'y': -0.9, 'width': 0.2, 'height': 0.05, 'color': [1, 1, 1]}
diamond = {'x': 0, 'y': 0.9, 'width': 0.05, 'height': 0.05, 'color': [1, 1, 0], 'dy': -0.01}
score = 0
game_over = False
paused = False
speed_increase = 0.0001
last_time = pygame.time.get_ticks()

# Buttons
buttons = [
    {'x': -0.8, 'y': 0.9, 'width': 0.1, 'height': 0.1, 'color': [0, 1, 1], 'shape': 'left_arrow'},
    {'x': 0, 'y': 0.9, 'width': 0.1, 'height': 0.1, 'color': [1, 0.7, 0], 'shape': 'play_pause'},
    {'x': 0.8, 'y': 0.9, 'width': 0.1, 'height': 0.1, 'color': [1, 0, 0], 'shape': 'cross'}
]

# Midpoint line drawing algorithm
def draw_line(x0, y0, x1, y1, vertices):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        vertices.append((x0, y0))
        if abs(x0 - x1) < 0.001 and abs(y0 - y1) < 0.001:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx * 0.001
        if e2 < dx:
            err += dx
            y0 += sy * 0.001

# Draw shapes using midpoint lines
def draw_diamond(x, y, w, h):
    vertices = []
    left, right = x - w / 2, x + w / 2
    top, bottom = y + h / 2, y - h / 2
    draw_line(left, y, x, top, vertices)
    draw_line(x, top, right, y, vertices)
    draw_line(right, y, x, bottom, vertices)
    draw_line(x, bottom, left, y, vertices)
    return vertices

def draw_catcher(x, y, w, h):
    vertices = []
    left, right = x - w / 2, x + w / 2
    top, bottom = y + h / 2, y - h / 2
    draw_line(left, bottom, left, top, vertices)
    draw_line(left, top, right, top, vertices)
    draw_line(right, top, right, bottom, vertices)
    draw_line(right, bottom, left, bottom, vertices)
    return vertices

def draw_left_arrow(x, y, w, h):
    vertices = []
    left, right = x - w / 2, x + w / 2
    top, bottom = y + h / 2, y - h / 2
    draw_line(right, top, left, y, vertices)
    draw_line(left, y, right, bottom, vertices)
    return vertices

def draw_play(x, y, w, h):
    vertices = []
    left, right = x - w / 2, x + w / 2
    top, bottom = y + h / 2, y - h / 2
    draw_line(left, bottom, left, top, vertices)
    draw_line(left, top, right, y, vertices)
    draw_line(right, y, left, bottom, vertices)
    return vertices

def draw_pause(x, y, w, h):
    vertices = []
    left, right = x - w / 2, x + w / 2
    top, bottom = y + h / 2, y - h / 2
    draw_line(left - w / 4, top, left - w / 4, bottom, vertices)
    draw_line(right - w / 4, top, right - w / 4, bottom, vertices)
    return vertices

def draw_cross(x, y, w, h):
    vertices = []
    left, right = x - w / 2, x + w / 2
    top, bottom = y + h / 2, y - h / 2
    draw_line(left, top, right, bottom, vertices)
    draw_line(left, bottom, right, top, vertices)
    return vertices

# Render shape with GL_POINTS
def render_shape(vertices, color):
    glBegin(GL_POINTS)
    glColor3f(*color)
    for x, y in vertices:
        glVertex2f(x, y)
    glEnd()

# AABB collision detection
def aabb_collision(obj1, obj2):
    return (obj1['x'] - obj1['width'] / 2 < obj2['x'] + obj2['width'] / 2 and
            obj1['x'] + obj1['width'] / 2 > obj2['x'] - obj2['width'] / 2 and
            obj1['y'] - obj1['height'] / 2 < obj2['y'] + obj2['height'] / 2 and
            obj1['y'] + obj1['height'] / 2 > obj2['y'] - obj2['height'] / 2)

# Generate random bright color
def random_bright_color():
    return [random.uniform(0.5, 1) for _ in range(3)]

# Reset diamond
def reset_diamond():
    diamond['x'] = random.uniform(-0.9, 0.9)
    diamond['y'] = 0.9
    diamond['color'] = random_bright_color()
    diamond['dy'] = -0.01

# Game actions
def restart_game():
    global score, game_over, paused, catcher, diamond
    score = 0
    game_over = False
    paused = False
    catcher['color'] = [1, 1, 1]
    diamond['dy'] = -0.01
    reset_diamond()
    print("Starting Over")

def toggle_pause():
    global paused
    if not game_over:
        paused = not paused

def exit_game():
    print(f"Goodbye! Final Score: {score}")
    pygame.quit()
    sys.exit()

# Main game loop
def main():
    global catcher, diamond, score, game_over, paused, last_time
    reset_diamond()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit_game()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                x = (x / display[0]) * 2 - 1
                y = 1 - (y / display[1]) * 2
                for button in buttons:
                    if (abs(x - button['x']) < button['width'] / 2 and
                            abs(y - button['y']) < button['height'] / 2):
                        if button['shape'] == 'left_arrow':
                            restart_game()
                        elif button['shape'] == 'play_pause':
                            toggle_pause()
                        elif button['shape'] == 'cross':
                            exit_game()

        if not game_over and not paused:
            # Handle input
            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                catcher['x'] = max(-1 + catcher['width'] / 2, catcher['x'] - 0.01)
            if keys[K_RIGHT]:
                catcher['x'] = min(1 - catcher['width'] / 2, catcher['x'] + 0.01)

            # Update diamond
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000
            last_time = current_time
            diamond['y'] += diamond['dy'] * delta_time * 60
            diamond['dy'] -= speed_increase * delta_time

            # Check collision
            if aabb_collision(catcher, diamond):
                score += 1
                print(f"Score: {score}")
                reset_diamond()
            elif diamond['y'] < -1:
                game_over = True
                catcher['color'] = [1, 0, 0]
                print(f"Game Over! Final Score: {score}")

        # Render
        glClear(GL_COLOR_BUFFER_BIT)
        render_shape(draw_catcher(catcher['x'], catcher['y'], catcher['width'], catcher['height']), catcher['color'])
        if not game_over:
            render_shape(draw_diamond(diamond['x'], diamond['y'], diamond['width'], diamond['height']), diamond['color'])
        for button in buttons:
            if button['shape'] == 'left_arrow':
                vertices = draw_left_arrow(button['x'], button['y'], button['width'], button['height'])
            elif button['shape'] == 'play_pause':
                vertices = draw_pause(button['x'], button['y'], button['width'], button['height']) if not paused else draw_play(button['x'], button['y'], button['width'], button['height'])
            else:
                vertices = draw_cross(button['x'], button['y'], button['width'], button['height'])
            render_shape(vertices, button['color'])

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()