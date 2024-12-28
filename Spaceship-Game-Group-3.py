import random as rd
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
screen_w = 500
screen_h = 500
rocket_x = screen_w / 2
rocket_y = 20
rocket_radius = 30
rocket_speed = 10
projectiles = []  # fired_bullet_info
falling_circles = []  # falling_circle_enemy
falling_bombs = [] # List of collected bombs
max_circle_radius = 20  # radius
game_mode = 0
play_button_visibility = True
Count_score = 0
Misfired_count = 0
missed_count = 0
game_over = False
collected_bombs = 0  # Track the number of collected bombs
max_lives = 10  # Maximum health/lives
lives = max_lives  # Initial lives
bomb_projectiles = [] #List of fired bombs
falling_proteins = [] #List of proteins

# MPC Algo
def drawing_circle(center_x, center_y, r):
    cx, cy = center_x, center_y
    x = r
    y = 0
    dinit = 0
    while x >= y:
        glVertex2f(cx + x, cy + y)
        glVertex2f(cx - x, cy + y)
        glVertex2f(cx + x, cy - y)
        glVertex2f(cx - x, cy - y)
        glVertex2f(cx + y, cy + x)
        glVertex2f(cx - y, cy + x)
        glVertex2f(cx + y, cy - x)
        glVertex2f(cx - y, cy - x)
        y = y + 1
        dinit = dinit + (2 * y + 1)
        if 2 * (dinit - x) + 1 > 0:
            x = x - 1
            dinit = dinit + (1 - 2 * x)

class Projectile:  # For Bullet
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.2  # speed of the bullet
        self.radius = 9  # bullet size
    def update(self):
        self.y += self.speed  # Bullet going
    def draw(self):
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_POINTS)
        drawing_circle(self.x, self.y, self.radius)
        glEnd()

class EnemyCircle:  # Circles falling
    def __init__(self):
        self.x = rd.randint(0, screen_w)
        self.y = screen_h
        self.speed = 0.013
        self.radius = rd.randint(10, max_circle_radius)
    def update(self):
        self.y -= self.speed  # Enemy falling
    def draw(self):
        glColor3f(1.0, 1.0, 0.0)
        glBegin(GL_POINTS)
        drawing_circle(self.x, self.y, self.radius)
        glEnd()

class Bomb:
    def __init__(self):
        self.x = rd.randint(0, screen_w)
        self.y = screen_h
        self.speed = 0.045
        self.radius = 15
    def update(self):
        self.y -= self.speed
    def draw(self):
        glColor3f(1.0, 0.5, 0.0)  #Orange color for bombs
        glBegin(GL_POINTS)
        drawing_circle(self.x, self.y, self.radius)
        glEnd()
        glColor3f(0.0, 0.5, 0.1)  #Dark Purple color for the thread
        glBegin(GL_POINTS)
        for i in range(9):
            glVertex2f(self.x, self.y + self.radius + i)  #Plot points along the line
        glEnd()

class FireBomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.08
        self.radius = 15
    def update(self):
        self.y += self.speed
    def draw(self):
        glColor3f(1.0, 0.5, 0.0)  # Orange color for bombs
        glBegin(GL_POINTS)
        drawing_circle(self.x, self.y, self.radius)
        glEnd()
        glColor3f(0.0, 0.5, 0.1)  # Dark Purple color for the thread
        glBegin(GL_POINTS)
        for i in range(9):
            glVertex2f(self.x, self.y + self.radius + i)  #Plot points along the line
        glEnd()

def point_in_triangle(px, py, v0, v1, v2): #Test to see if px,py are inside the triangle
    dX = px - v2[0]
    dY = py - v2[1]
    dX21 = v2[0] - v1[0]
    dY12 = v1[1] - v2[1]
    D = dY12 * (v0[0] - v2[0]) + dX21 * (v0[1] - v2[1])
    s = dY12 * dX + dX21 * dY
    t = (v2[1] - v0[1]) * dX + (v0[0] - v2[0]) * dY
    return s >= 0 and t >= 0 and s + t <= D

class ProteinBar:
    def __init__(self):
        self.x = rd.randint(0, screen_w)
        self.y = screen_h
        self.speed = 0.035
        self.size = 20
    def update(self):
        self.y -= self.speed
    def draw(self):
        glColor3f(0.5, 1.0, 0.5)  # Red color for the triangle
        glBegin(GL_POINTS)
        v0 = (self.x, self.y) #Vertices of the triangle
        v1 = (self.x - self.size / 2, self.y - self.size)
        v2 = (self.x + self.size / 2, self.y - self.size)
        x_min = min(v0[0], v1[0], v2[0]) # Boundary box for the triangle
        x_max = max(v0[0], v1[0], v2[0])
        y_min = min(v0[1], v1[1], v2[1])
        y_max = max(v0[1], v1[1], v2[1])
    
        for px in range(int(x_min), int(x_max) + 1): # Iterate over bounding box and draw points inside the triangle
            for py in range(int(y_min), int(y_max) + 1):
                if point_in_triangle(px, py, v0, v1, v2):
                    glVertex2f(px, py)
        glEnd()

def check_protein_collision():
    global falling_proteins, lives
    for protein in falling_proteins[:]:
        dx = protein.x - rocket_x
        dy = protein.y - rocket_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < rocket_radius + protein.size:
            falling_proteins.remove(protein)
            if lives < max_lives:
                lives += 1
            print("Lives increased to:", lives)

def drawline(x1, y1, x2, y2):
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_hud(): # Draw score and collected bombs text
    global GLUT_BITMAP_HELVETICA_18 
    glColor3f(1.0, 1.0, 1.0)  # White color
    glRasterPos2f(10, screen_h - 30)
    score_text = f"Score: {Count_score} | Bombs: {collected_bombs}"
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_health_bar(): # Health bar: Draw a filled bar based on lives
    x_start, y_start = 10, screen_h - 45  # Start coordinates
    bar_width, bar_height = 150, 15  # Size of the bar
    x_end = x_start + bar_width
    y_end = y_start - bar_height
    glColor3f(1.0, 0.0, 0.0) # Draw background for the health bar (red)
    glBegin(GL_POINTS)

    for x in range(int(x_start), int(x_end)): # Iterate over the x and y range to fill the rectangle
        for y in range(int(y_end), int(y_start)):
            glVertex2f(x, y)
    glEnd()

    glColor3f(0.0, 1.0, 0.0) # Draw foreground for the health bar (green)
    filled_width = (lives / max_lives) * bar_width
    glBegin(GL_POINTS)
    
    for x in range(int(x_start), int(x_start + filled_width)): # Loop through each pixel in the rectangular area
        for y in range(int(y_start - bar_height), int(y_start)):
            glVertex2f(x, y)  # Plotting points
    glEnd()

def play(): #Play Button
    global play_button_visibility
    play_button_visibility= True
    glColor3f(1.0, 1.0, 0.0)
    px1= int(240)
    px2= int(280)
    py1= int(screen_h - 45)
    py2= int(screen_h - 10)
    py_mid= int(py1 + (py2 - py1) / 2)
    drawline(px1, py2, px2, py_mid)
    drawline(px1, py1, px1 - 0.0000001, py2)
    drawline(px1, py1, px2, py_mid)

def pause(): #Pause Button
    global play_button_visibility
    play_button_visibility= False
    glColor3f(1.0, 1.0, 0.0)
    tx1= int(240)
    tx2= int(280)
    ty1= int(screen_h - 45)
    ty2= int(screen_h - 10)
    t_part= int((tx2 - tx1) / 3)
    drawline(tx1 + t_part - 0.001, ty1, tx1 + t_part, ty2)
    drawline(tx1 + 2 * t_part - 0.0001, ty1, tx1 + 2 * t_part, ty2)

def cross(): #Cross Button
    glColor3f(1.0, 0.0, 0.0)
    cx1= int(440)
    cx2= int(470)
    cy1= int(screen_h - 45)
    cy2= int(screen_h - 10)
    drawline(cx1, cy1, cx2, cy2)
    drawline(cx1, cy2, cx2, cy1)

def mouseclickfunc(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        check_button_click(x, y)

def check_button_click(x, y):
    check_play_button_click(x, y)
    check_cross_button_click(x,y)

def toggle_play_pause_button():
    global play_button_visibility, game_mode
    play_button_visibility = not play_button_visibility
    game_mode = 0 if play_button_visibility else 1

def check_play_button_click(x, y):
    global game_mode
    px1, px2 = int(240), int(280)
    py1, py2 = int(440), int(480)
    if px1 <= x <= px2 and py1 <= screen_h - y <= py2:
        toggle_play_pause_button()
        glutPostRedisplay()

def check_cross_button_click(x,y):
    global game_over
    cx1, cx2 = 440, 470
    cy1, cy2 = screen_h - 45, screen_h - 10
    if cx1 <= x <= cx2 and cy1 <= screen_h - y <= cy2:
        reset_game(show_message=True)
        glutPostRedisplay()

def check_rocket_collision():
    global falling_circles, lives, game_over, Count_score
    for circle in falling_circles[:]:
        # Define rocket boundaries
        rocket_left = rocket_x - rocket_radius / 2
        rocket_right = rocket_x + rocket_radius / 2
        rocket_bottom = rocket_y - 30  # Adjust based on rocket's dimensions
        rocket_top = rocket_y + 30
        # Get circle center
        circle_center_x = circle.x
        circle_center_y = circle.y
        # Find the closest point on the rocket rectangle to the circle center
        closest_x = max(rocket_left, min(circle_center_x, rocket_right))
        closest_y = max(rocket_bottom, min(circle_center_y, rocket_top))
        # Calculate distance from the circle center to the closest point
        dx = circle_center_x - closest_x
        dy = circle_center_y - closest_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        # Check if the circle collides with the rocket
        if distance < circle.radius:
            falling_circles.remove(circle)
            lives -= 1
            print(f"Collision! Lives remaining: {lives}")
            if lives == 0:
                print("Game Over! Final Score:", Count_score)
                game_over = True

def check_bomb_collision():
    global collected_bombs
    for bomb in falling_bombs[:]:
        dx = bomb.x - rocket_x
        dy = bomb.y - rocket_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < rocket_radius + bomb.radius:
            falling_bombs.remove(bomb)
            collected_bombs += 1
            print("Bombs collected:", collected_bombs)

def drawrocket(x, y, width, height):  # Rocket Body
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_POINTS)
    def draw_rectangle_midpoint(x1, y1, x2, y2, x3, y3, x4, y4):
        def draw_line_midpoint(x0, y0, x1, y1):
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy
            while True:
                glVertex2f(x0, y0)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy
        # Draw edges of the rectangle
        draw_line_midpoint(round(x1), round(y1), round(x2), round(y2))
        draw_line_midpoint(round(x2), round(y2), round(x3), round(y3))
        draw_line_midpoint(round(x3), round(y3), round(x4), round(y4))
        draw_line_midpoint(round(x4), round(y4), round(x1), round(y1))

    # Rectangle coordinates
    x1, y1 = x - width / 2, y - height / 2  # Bottom Left
    x2, y2 = x + width / 2, y - height / 2  # Bottom Right
    x3, y3 = x + width / 2, y + height / 2  # Top Right
    x4, y4 = x - width / 2, y + height / 2  # Top Left
    draw_rectangle_midpoint(x1, y1, x2, y2, x3, y3, x4, y4)

    # Rocket Nose
    glColor3f(0.0, 1.0, 0.0)
    def draw_triangle_midpoint(x1, y1, x2, y2, x3, y3):
        def draw_line_midpoint(x0, y0, x1, y1):
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy
            while True:
                glVertex2f(x0, y0)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy
        # Draw edges of the triangle
        draw_line_midpoint(round(x1), round(y1), round(x2), round(y2))
        draw_line_midpoint(round(x2), round(y2), round(x3), round(y3))
        draw_line_midpoint(round(x3), round(y3), round(x1), round(y1))

    # Nose coordinates
    x1, y1 = x, y + height / 2 + 10  # Tip of the nose
    x2, y2 = x - width / 2, y + height / 2  # Bottom Left of the nose
    x3, y3 = x + width / 2, y + height / 2  # Bottom Right of the nose
    draw_triangle_midpoint(x1, y1, x2, y2, x3, y3)
    glEnd()

def draw():
    global Count_score, missed_count, Misfired_count, game_over, lives, bomb_projectiles
    glClear(GL_COLOR_BUFFER_BIT)
    if game_over== True:
        print("Game Over! Final Score:", Count_score)
        return
    drawrocket(rocket_x, rocket_y, rocket_radius, 60)

    for projectile in projectiles:
        projectile.update()
        projectile.draw()
    for circle in falling_circles:
        circle.update()
        circle.draw()
    for bomb in falling_bombs:
        bomb.update()
        bomb.draw()
    for bomb in bomb_projectiles:
        bomb.update()
        bomb.draw()
    for protein in falling_proteins:
        protein.update()
        protein.draw()

    # Collision Check
    for projectile in projectiles[:]: #Score
        for circle in falling_circles:
            dx = projectile.x - circle.x
            dy = projectile.y - circle.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < projectile.radius + circle.radius:
                projectiles.remove(projectile)
                falling_circles.remove(circle)
                Count_score += 1
                print("Score:", Count_score)
    
    for bomb in bomb_projectiles[:]:
        for circle in falling_circles[:]:
            dx = bomb.x - circle.x
            dy = bomb.y - circle.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < bomb.radius + circle.radius:
                bomb_projectiles.remove(bomb)
                falling_circles.remove(circle)
                Count_score += 2
                print("Score:", Count_score)

    for projectile in projectiles[:]: #Misfire
        if projectile.y > screen_h:
            projectiles.remove(projectile)
            Misfired_count += 1
            lives-= 1
            print("Misfires:", Misfired_count)
            #if Misfired_count >= 3:
            if lives == 0:
                #print("Game Over! Three misfires.")
                print("Game Over! Final Score:", Count_score)
                falling_circles.clear()
                falling_bombs.clear()
                game_over = True

    for circle in falling_circles[:]: #Missed
        if circle.y < 0:
            glColor3f(0.0, 1.0, 0.0)
            glBegin(GL_POINTS)
            drawing_circle(circle.x, circle.y, circle.radius)
            glEnd()
            falling_circles.remove(circle)
            missed_count += 1
            lives-= 1
            print("Misses:", missed_count)
            #if missed_count >= 3:
            if lives == 0:
                #print("Game Over!")
                print("Game Over! Final Score:", Count_score)
                game_over = True
                falling_circles.clear()
                falling_bombs.clear()

    check_rocket_collision()
    check_bomb_collision()
    check_protein_collision()
    draw_hud() # Draw HUD: Score and Bombs, Health Bar
    draw_health_bar()

    if play_button_visibility:
        play()
    else:
        pause()
    cross()
    glFlush()

def animation():
    global game_mode, Count_score, missed_count
    if game_mode == 0 and not game_over:
        for projectile in projectiles:
            projectile.update()
        for circle in falling_circles:
            circle.update()
        glutPostRedisplay()

# keyboard inputs
def KeyboardFunc(key, x, y):
    global rocket_x, collected_bombs
    if game_over == True:
        return
    if key == b'a' and rocket_x - rocket_radius >= -10:
        rocket_x -= rocket_speed
    elif key == b'd' and rocket_x + rocket_radius <= screen_w + 10:
        rocket_x += rocket_speed
    elif key == b' ':
        projectiles.append(Projectile(rocket_x, rocket_y + rocket_radius))
    elif key == b'b' and collected_bombs > 0:
        collected_bombs -= 1
        bomb_projectiles.append(FireBomb(rocket_x, rocket_y + rocket_radius))  # Fire a bomb
    elif key == b'b' and collected_bombs == 0:
        print("Collect bomb(s) first!")

def timer(value):
    if game_over == False:
        if rd.random() < 0.01:
            falling_circles.append(EnemyCircle())
        if rd.random() < 0.0008:
            falling_bombs.append(Bomb())
        if rd.random() < 0.0008:
            falling_proteins.append(ProteinBar()) 
    glutTimerFunc(1000 // 60, timer, 0)

def reset_game(show_message= False):
    global falling_circles, Count_score, game_over, rocket_x, missed_count, Misfired_count, collected_bombs, falling_bombs, lives, falling_proteins
    falling_circles = []
    falling_bombs= []
    falling_proteins= []
    Count_score = 0
    missed_count = 0
    Misfired_count = 0
    collected_bombs= 0
    game_over = False
    rocket_x = screen_w / 2
    lives= 10

glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(screen_w, screen_h)
glutInitWindowPosition(50, 50)
glutCreateWindow(b'Spaceship Game')
gluOrtho2D(0, screen_w, 0, screen_h)
glutDisplayFunc(draw)
glutIdleFunc(animation)
glutKeyboardFunc(KeyboardFunc)
glutMouseFunc(mouseclickfunc)
glutTimerFunc(1000 // 60, timer, 0)
glutMainLoop()