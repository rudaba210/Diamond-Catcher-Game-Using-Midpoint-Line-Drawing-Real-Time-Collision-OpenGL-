from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, time

WIDTH, HEIGHT = 500, 500


x1, x2, x3, x4 = 20, 50, 200, 230
y1, y2 = 10, 50
CATCHER_SPEED_STEP = 14


DIAMOND_W = 10
DIAMOND_H = 25
diamond_pos = [random.uniform(DIAMOND_W, WIDTH - DIAMOND_W), HEIGHT - DIAMOND_H]
fall_speed = 160.0
fall_accel = 18.0
fall_boost_on_catch = 24.0
BRIGHT_MIN = 0.65

pause_flag = False
start_flag = False
over_flag = False
score_count = 0

diamond_color = (
    random.uniform(BRIGHT_MIN, 1.0),
    random.uniform(BRIGHT_MIN, 1.0),
    random.uniform(BRIGHT_MIN, 1.0),
)

_last_time = time.time()

def draw_points(x, y):
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def zone_for_segment(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    shallow = abs(dx) >= abs(dy)
    if shallow:
        if dy >= 0:
            return 0 if dx >= 0 else 3
        else:
            return 7 if dx >= 0 else 4
    else:
        if dy >= 0:
            return 1 if dx >= 0 else 2
        else:
            return 6 if dx >= 0 else 5

def to_zone0(z, x, y):
    if z == 0: return  x,  y
    if z == 1: return  y,  x
    if z == 2: return  y, -x
    if z == 3: return -x,  y
    if z == 4: return -x, -y
    if z == 5: return -y, -x
    if z == 6: return -y,  x
    if z == 7: return  x, -y

def from_zone0(z, x, y):
    if z == 0: return  x,  y
    if z == 1: return  y,  x
    if z == 2: return -y,  x
    if z == 3: return -x,  y
    if z == 4: return -x, -y
    if z == 5: return -y, -x
    if z == 6: return  y, -x
    if z == 7: return  x, -y


def line_points(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    z = zone_for_segment(x0, y0, x1, y1)

    ax0, ay0 = to_zone0(z, x0, y0)
    ax1, ay1 = to_zone0(z, x1, y1)

    if ax0 > ax1:
        ax0, ax1 = ax1, ax0
        ay0, ay1 = ay1, ay0

    dx = ax1 - ax0
    dy = ay1 - ay0

    if dx == 0:
        step = 1 if ay1 >= ay0 else -1
        for yy in range(ay0, ay1 + step, step):
            px, py = from_zone0(z, ax0, yy)
            draw_points(px, py)
        return

    d     = 2 * dy - dx
    incE  = 2 * dy
    incNE = 2 * (dy - dx)

    x, y = ax0, ay0
    glBegin(GL_POINTS)
    while x <= ax1:
        px, py = from_zone0(z, x, y)
        glVertex2f(px, py)
        if d <= 0:
            d += incE
            x += 1
        else:
            d += incNE
            x += 1
            y += 1
    glEnd()


def draw_catcher():
    global over_flag
    if not over_flag: glColor3f(1.0, 1.0, 1.0)
    else:             glColor3f(1.0, 0.0, 0.0)
    line_points(x2, y1, x3, y1)
    line_points(x1, y2, x2, y1)
    line_points(x3, y1, x4, y2)
    line_points(x1, y2, x4, y2)

def draw_diamond(cx, cy):
    glColor3f(*diamond_color)
    if 0 <= cx <= WIDTH and 0 <= cy <= HEIGHT:
        line_points(cx,cy - DIAMOND_H, cx + DIAMOND_W, cy)
        line_points(cx + DIAMOND_W, cy, cx, cy + DIAMOND_H)
        line_points(cx, cy + DIAMOND_H, cx - DIAMOND_W, cy)
        line_points(cx - DIAMOND_W, cy, cx, cy - DIAMOND_H)

def left_arrow():
    glColor3f(0.0, 1.0, 1.0)
    line_points(50, 425, 100, 425)
    line_points(70, 430, 50, 425)
    line_points(70, 420, 50, 425)

def cross():
    glColor3f(1.0, 0.0, 0.0)
    line_points(400, 400, 450, 450)
    line_points(400, 450, 450, 400)

def play_icon():
    glColor3f(1.0, 1.0, 0.0)
    line_points(250, 450, 250, 400)
    line_points(250, 450, 270, 425)
    line_points(250, 400, 270, 425)

def pause_icon():
    glColor3f(1.0, 1.0, 0.0)
    line_points(250, 450, 250, 400)
    line_points(265, 450, 265, 400)


def aabb_collide(ax, ay, aw, ah, bx1, by1, bx2, by2):
    ax1 = ax - aw
    ay1 = ay - ah
    ax2 = ax + aw
    ay2 = ay + ah
    return (ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1)


def specialKeyListener(key, x, y):
    global x1, x2, x3, x4, pause_flag
    if pause_flag or over_flag: return
    if key == GLUT_KEY_RIGHT:
        if x4 + CATCHER_SPEED_STEP <= WIDTH:
            x1 += CATCHER_SPEED_STEP; x2 += CATCHER_SPEED_STEP; x3 += CATCHER_SPEED_STEP; x4 += CATCHER_SPEED_STEP
        else:
            shift = WIDTH - x4
            x1 += shift; x2 += shift; x3 += shift; x4 += shift
    elif key == GLUT_KEY_LEFT:
        if x1 - CATCHER_SPEED_STEP >= 0:
            x1 -= CATCHER_SPEED_STEP; x2 -= CATCHER_SPEED_STEP; x3 -= CATCHER_SPEED_STEP; x4 -= CATCHER_SPEED_STEP
        else:
            shift = -x1
            x1 += shift; x2 += shift; x3 += shift; x4 += shift
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global pause_flag, x1, x2, x3, x4, score_count, start_flag, over_flag
    global diamond_pos, fall_speed, diamond_color
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN: return
    new_y = HEIGHT - y

    if 250 <= x <= 270 and 400 <= new_y <= 450:
        pause_flag = not pause_flag
        print(("Pause" if pause_flag else "Resume") + f" Score: {score_count}")

    if 400 <= x <= 450 and 400 <= new_y <= 450:
        over_flag = True
        print(f"Goodbye! Total Score: {score_count}")
        glutLeaveMainLoop()
        return

    if 50 <= x <= 100 and 420 <= new_y <= 430:
        x1, x2, x3, x4 = 20, 50, 200, 230
        start_flag = True
        score_count = 0
        over_flag = False
        pause_flag = False
        diamond_pos = [random.uniform(DIAMOND_W, WIDTH - DIAMOND_W), HEIGHT - DIAMOND_H]
        fall_speed = 160.0
        diamond_color = (
            random.uniform(BRIGHT_MIN, 1.0),
            random.uniform(BRIGHT_MIN, 1.0),
            random.uniform(BRIGHT_MIN, 1.0),
        )
        print(f"Starting Over! Score: {score_count}")
    glutPostRedisplay()


def animation():
    global diamond_pos, fall_speed, score_count, _last_time, over_flag, diamond_color
    now = time.time()
    dt = now - _last_time
    _last_time = now

    if not pause_flag and not over_flag:
        fall_speed += fall_accel * dt
        diamond_pos[1] -= fall_speed * dt

        if aabb_collide(diamond_pos[0], diamond_pos[1], DIAMOND_W, DIAMOND_H, x1, y1, x4, y2):
            score_count += 1
            print(f"Score: {score_count}")
            diamond_pos = [random.uniform(DIAMOND_W, WIDTH - DIAMOND_W), HEIGHT - DIAMOND_H]
            diamond_color = (
                random.uniform(BRIGHT_MIN, 1.0),
                random.uniform(BRIGHT_MIN, 1.0),
                random.uniform(BRIGHT_MIN, 1.0),
            )
            fall_speed = min(fall_speed + fall_boost_on_catch, 700.0)

        if diamond_pos[1] + DIAMOND_H < 0:
            over_flag = True
            print(f"Game Over! Final Score: {score_count}")

    glutPostRedisplay()


def iterate():
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, WIDTH, 0.0, HEIGHT, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()

    draw_catcher()
    left_arrow()
    cross()

    if not over_flag:
        draw_diamond(diamond_pos[0], diamond_pos[1])

    if pause_flag:
        play_icon()
    else:
        pause_icon()

    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(WIDTH, HEIGHT)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow(b"Diamond Game - Midpoint + Eight-Way Symmetry (GL_POINTS)")

glutDisplayFunc(showScreen)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutIdleFunc(animation)

glClearColor(0.0, 0.0, 0.0, 1.0)
glutMainLoop() 
