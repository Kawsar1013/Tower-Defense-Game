from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Game state
catcher_x = 400
catcher_y = 30
catcher_width = 100
catcher_height = 20
move_step = 20

diamond_x = random.randint(20, 780)
diamond_y = 580
fall_speed = 5
diamond_color = [random.uniform(0.5, 1.0) for _ in range(3)]  # Bright random color

score = 0
paused = False
game_over = False
speed_increase = 0.5  # Speed increase per catch

# Draw a single point
def draw_point(x, y):
    glPointSize(2.0)
    glBegin(GL_POINTS)
    glVertex2i(round(x), round(y))
    glEnd()

# Find the zone for midpoint line algorithm
def findzone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx >= 0 and dy < 0:
            return 7
        elif dx < 0 and dy >= 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx >= 0 and dy < 0:
            return 6
        elif dx < 0 and dy >= 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5

# Convert coordinates to zone 0
def convertToZone0(zone, x, y):
    if zone == 0: return (x, y)
    elif zone == 1: return (y, x)
    elif zone == 2: return (y, -x)
    elif zone == 3: return (-x, y)
    elif zone == 4: return (-x, -y)
    elif zone == 5: return (-y, -x)
    elif zone == 6: return (-y, x)
    elif zone == 7: return (x, -y)

# Convert back to original zone
def originalZone(zone, x, y):
    if zone == 0: return (x, y)
    elif zone == 1: return (y, x)
    elif zone == 2: return (-y, x)
    elif zone == 3: return (-x, y)
    elif zone == 4: return (-x, -y)
    elif zone == 5: return (-y, -x)
    elif zone == 6: return (y, -x)
    elif zone == 7: return (x, -y)

# Midpoint line algorithm for zone 0
def midpoint_line(zone, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    dNE = 2 * (dy - dx)
    dE = 2 * dy
    x, y = x1, y1
    while x <= x2:
        cx, cy = originalZone(zone, x, y)
        draw_point(cx, cy)
        if d <= 0:  # Choose E
            x += 1
            d += dE
        else:  # Choose NE
            x += 1
            y += 1
            d += dNE

# 8-way midpoint line drawing
def midpoint_line_8way(x1, y1, x2, y2):
    zone = findzone(x1, y1, x2, y2)
    x1, y1 = convertToZone0(zone, x1, y1)
    x2, y2 = convertToZone0(zone, x2, y2)
    midpoint_line(zone, x1, y1, x2, y2)

# Draw catcher
def draw_catcher():
    glColor3f(1.0, 1.0, 1.0) if not game_over else glColor3f(1.0, 0.0, 0.0)
    x1 = catcher_x - catcher_width // 2
    x2 = catcher_x + catcher_width // 2
    y1 = catcher_y
    y2 = catcher_y + catcher_height
    midpoint_line_8way(x1, y1, x2, y1)  # Bottom
    midpoint_line_8way(x2, y1, x2, y2)  # Right
    midpoint_line_8way(x2, y2, x1, y2)  # Top
    midpoint_line_8way(x1, y2, x1, y1)  # Left

# Draw diamond
def draw_diamond():
    glColor3f(*diamond_color)
    x = diamond_x
    y = diamond_y
    size = 20
    midpoint_line_8way(x, y, x + size, y + size)  # Top-right
    midpoint_line_8way(x + size, y + size, x, y + 2 * size)  # Bottom-right
    midpoint_line_8way(x, y + 2 * size, x - size, y + size)  # Bottom-left
    midpoint_line_8way(x - size, y + size, x, y)  # Top-left

# Draw buttons
def draw_button(x, y, color, shape):
    glColor3f(*color)
    if shape == 'left_arrow':
        midpoint_line_8way(x + 50, y, x, y + 25)  # Left point to top
        midpoint_line_8way(x, y + 25, x + 50, y + 50)  # Top to right point
    elif shape == 'play':
        midpoint_line_8way(x, y, x, y + 50)  # Left vertical
        midpoint_line_8way(x, y + 50, x + 50, y + 25)  # Top to right point
        midpoint_line_8way(x + 50, y + 25, x, y)  # Right point to bottom
    elif shape == 'pause':
        midpoint_line_8way(x + 12, y, x + 12, y + 50)  # Left bar
        midpoint_line_8way(x + 38, y, x + 38, y + 50)  # Right bar
    elif shape == 'cross':
        midpoint_line_8way(x, y, x + 50, y + 50)  # Diagonal 1
        midpoint_line_8way(x, y + 50, x + 50, y)  # Diagonal 2

# Draw all buttons
def draw_buttons():
    draw_button(50, 550, (0.0, 1.0, 1.0), 'left_arrow')  # Restart
    draw_button(375, 550, (1.0, 0.75, 0.0), 'pause' if not paused else 'play')  # Play/Pause
    draw_button(700, 550, (1.0, 0.0, 0.0), 'cross')  # Exit

# Keyboard input for catcher movement
def keyboard(key, x, y):
    global catcher_x
    if not game_over and not paused:
        if key == GLUT_KEY_LEFT:
            catcher_x = max(catcher_width // 2, catcher_x - move_step)
        elif key == GLUT_KEY_RIGHT:
            catcher_x = min(WINDOW_WIDTH - catcher_width // 2, catcher_x + move_step)
        glutPostRedisplay()

# Mouse input for buttons
def mouse(button, state, x, y):
    global game_over, paused, catcher_x
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = WINDOW_HEIGHT - y  # Invert y coordinate
        if 50 <= x <= 100 and 550 <= y <= 600:  # Restart button
            restart()
        elif 375 <= x <= 425 and 550 <= y <= 600:  # Play/Pause button
            pause()
        elif 700 <= x <= 750 and 550 <= y <= 600:  # Exit button
            print(f"Goodbye Final Score: {score}")
            glutLeaveMainLoop()

# AABB collision detection
def check_collision():
    catcher_left = catcher_x - catcher_width // 2
    catcher_right = catcher_x + catcher_width // 2
    catcher_top = catcher_y + catcher_height
    catcher_bottom = catcher_y
    diamond_left = diamond_x - 20
    diamond_right = diamond_x + 20
    diamond_top = diamond_y + 40
    diamond_bottom = diamond_y
    return (catcher_left <= diamond_right and catcher_right >= diamond_left and
            catcher_bottom <= diamond_top and catcher_top >= diamond_bottom)

# Reset game state
def restart():
    global diamond_x, diamond_y, fall_speed, score, game_over, paused, catcher_x, diamond_color
    print("Starting Over")
    catcher_x = 400
    diamond_x = random.randint(20, 780)
    diamond_y = 580
    fall_speed = 5
    score = 0
    game_over = False
    paused = False
    diamond_color = [random.uniform(0.5, 1.0) for _ in range(3)]
    print(f"Score: {score}")
    glutPostRedisplay()
    glutTimerFunc(30, update, 0)  # Restart the timer

# Toggle pause state
def pause():
    global paused
    if not game_over:
        paused = not paused
        print("Paused" if paused else "Resumed")
    glutPostRedisplay()

# Update game state
def update(value):
    global diamond_y, game_over, score, diamond_x, fall_speed, diamond_color
    if not paused and not game_over:
        diamond_y -= fall_speed
        if check_collision() and diamond_y <= catcher_y + catcher_height:
            score += 1
            print(f"Score: {score}")
            diamond_x = random.randint(20, 780)
            diamond_y = 580
            diamond_color = [random.uniform(0.5, 1.0) for _ in range(3)]
            fall_speed += speed_increase
        elif diamond_y < catcher_y:
            game_over = True
            print(f"Game Over! Final Score: {score}")
        glutPostRedisplay()
    glutTimerFunc(30, update, 0)  # Continue the timer loop

# Set up viewport and projection
def iterate():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, WINDOW_WIDTH, 0.0, WINDOW_HEIGHT, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# Display callback
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.1, 0.1, 0.1, 1.0)  # Dark background
    glLoadIdentity()
    iterate()
    draw_catcher()
    if not game_over:
        draw_diamond()
    draw_buttons()
    if paused:
        glColor3f(0.8, 0.8, 0.0)
        glRasterPos2f(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2)
        glutBitmapString(GLUT_BITMAP_HELVETICA_18, b"Paused")
    if game_over:
        glColor3f(0.8, 0.1, 0.1)
        glRasterPos2f(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2)
        glutBitmapString(GLUT_BITMAP_HELVETICA_18, b"Game Over")
    glutSwapBuffers()

# Main function
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Catch the Diamonds")
    glutDisplayFunc(showScreen)
    glutMouseFunc(mouse)
    glutSpecialFunc(keyboard)
    glutTimerFunc(30, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()