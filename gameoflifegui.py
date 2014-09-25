"""

    CONWAY'S GAME OF LIFE

    this python version was written by
    JP ARMSTRONG http://www.jparmstrong.com/

    I developed this game just to learn python.

    MIT-LICENSE

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#################################################
"""


import pygame, random, time, random, os
import RPi.GPIO as GPIO

from pygame.locals import *
from boxes import Box

# Init framebuffer/touchscreen environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

ENTER = 18 # right most button, the 4th button
KEYB = 21 # to the left of 18, the 3rd button

GPIO.setup(ENTER, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(KEYB, GPIO.IN, pull_up_down = GPIO.PUD_UP)


MAX_X = 32
MAX_Y = 24
SIZE = 10
DEBUG = False

DEAD_CELL = '.'
LIVE_CELL = 'o'

rand_col = False
keep_background = False

# MAKING THE BOXES
boxes = [''] * MAX_X
    
for i in range(MAX_X):
    boxes[i] = [''] * MAX_Y

pygame.init()
pygame.display.set_caption('Conway\'s Game of Life by jparmstrong.com')
screen = pygame.display.set_mode([MAX_X * SIZE, MAX_Y * SIZE])
pygame.mouse.set_visible(0)


# MAKING THE BOARD
board = [DEAD_CELL] * MAX_X
    
for i in range(MAX_X):
    board[i] = [DEAD_CELL] * MAX_Y



# ALLOWING THE BOARD TO WRAP AROUND, "INFINITE PLAYING FIELD"
def borderless(n, t):

    if n < 0:
        n = t + n;
    elif n >= t:
        n = abs(n) % t

    return n

# THE RULES TO LIFE
def rulesOfLife(b):

    total_pop = 0;

    pop_list = ['0'] * MAX_X
    
    for i in range(MAX_X):
        pop_list[i] = ['0'] * MAX_Y

   # CHECKING TO SEE WHAT IS POPULATED AROUND EACH CELL
    for y in range(MAX_Y):
        for x in range(MAX_X):

            pop = 0
            buf = []

            # ROW A
            if b[borderless(x-1, MAX_X)][borderless(y-1, MAX_Y)] == LIVE_CELL:
                buf.append("a1 ")
                pop += 1
                
            if b[borderless(x, MAX_X)][borderless(y-1, MAX_Y)] == LIVE_CELL:
                buf.append("a2 ")
                pop += 1
                
            if b[borderless(x+1, MAX_X)][borderless(y-1, MAX_Y)] == LIVE_CELL:
                buf.append("a3 ")
                pop += 1

            # ROW B
            if b[borderless(x-1, MAX_X)][borderless(y, MAX_Y)] == LIVE_CELL:
                buf.append("b1 ")
                pop += 1
            if b[borderless(x+1, MAX_X)][borderless(y, MAX_Y)] == LIVE_CELL:
                buf.append("b3 ")
                pop += 1

            # ROW C
            if b[borderless(x-1, MAX_X)][borderless(y+1, MAX_Y)] == LIVE_CELL:
                buf.append("c1 ")
                pop += 1
                
            if b[borderless(x, MAX_X)][borderless(y+1, MAX_Y)] == LIVE_CELL:
                buf.append("c2 ")
                pop += 1
                
            if b[borderless(x+1, MAX_X)][borderless(y+1, MAX_Y)] == LIVE_CELL:
                buf.append("c3 ")
                pop += 1

            if DEBUG and pop > 0:
                print x,y,":",''.join(buf),pop

            total_pop += pop

            pop_list[x][y] = pop

    
    # NOW THAT WE KNOW WHATS AROUND EACH CELL, WE IMPLEMENT THE RULES OF LIFE
    for y in range(MAX_Y):
        for x in range(MAX_X):

            if b[x][y] == LIVE_CELL and (pop_list[x][y] < 2 or pop_list[x][y] > 3):
                b[x][y] = DEAD_CELL
                
            elif b[x][y] == DEAD_CELL and pop_list[x][y] == 3:
                b[x][y] = LIVE_CELL


def updateDisplay():

    
    for dy in range(MAX_Y):
        for dx in range(MAX_X):
            if board[dx][dy] == LIVE_CELL:
                if rand_col:
                    boxes[dx][dy] = Box([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)], [dx * SIZE, dy * SIZE], SIZE)
                else:
                    boxes[dx][dy] = Box([255, 255, 255], [dx * SIZE, dy * SIZE], SIZE)
            elif keep_background == False:
                boxes[dx][dy] = Box([0, 0, 0], [dx * SIZE, dy * SIZE], SIZE)

            try:
                screen.blit(boxes[dx][dy].image, boxes[dx][dy].rect)
            except:
                pass
    
    pygame.display.update()

def initCallback():
    GPIO.add_event_detect(ENTER,GPIO.FALLING, callback=cb_ButtonEnter, bouncetime=100)
    GPIO.add_event_detect(KEYB,GPIO.FALLING, callback=cb_ButtonK, bouncetime=100)

def disableCallback():
    GPIO.remove_event_detect(ENTER) #remove to avoid some queueing it seemed
    GPIO.remove_event_detect(KEYB) #remove to avoid some queueing it seemed

def cb_ButtonEnter(x):
    global running
    running = not running

def cb_ButtonK(x):
    global running
    keep_background = not keep_background
    
initCallback()
running = False
button_down = False
keys = pygame.key.get_pressed()

for i in range(random.randint(10, 20)):
    sx = random.randint(0, MAX_X)
    sy = random.randint(0, MAX_Y)

    if random.randint(0, 1) == 1:
        board[borderless(sx + 1, MAX_X)][borderless(sy + 0, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 2, MAX_X)][borderless(sy + 1, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 0, MAX_X)][borderless(sy + 2, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 1, MAX_X)][borderless(sy + 2, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 2, MAX_X)][borderless(sy + 2, MAX_Y)] = LIVE_CELL;
    else:
        board[borderless(sx + 1, MAX_X)][borderless(sy + 0, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 0, MAX_X)][borderless(sy + 1, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 0, MAX_X)][borderless(sy + 2, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 1, MAX_X)][borderless(sy + 2, MAX_Y)] = LIVE_CELL;
        board[borderless(sx + 2, MAX_X)][borderless(sy + 2, MAX_Y)] = LIVE_CELL;

    
updateDisplay()


running = True
rand_col = True

try:
    while running:
            updateDisplay()
            rulesOfLife(board)
            pygame.time.delay(10)
    
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
    
GPIO.cleanup()           # clean up GPIO on normal exit  


        
