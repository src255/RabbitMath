import time
import numpy as np
import pygame as pg
from collections import Counter

# COLOURS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (175, 175, 175)
GENTIAN = (100, 25, 255)
BRIGHTER_GENTIAN = (150, 25, 255)
BROWN1 = (170, 90, 5)
BROWN2 = (150, 110, 10)
DULL_RED = (200, 0, 0)
RED = (255, 0, 0)
BLUE = (70, 210, 255)
BRIGHT_GREEN = (0, 255, 0)
GREEN = (0, 200, 0)


class Pad:
    def __init__(self, colour, radius, x, y, hide=True):
        self.colour = colour
        self.radius = int(round(radius))
        self.x = int(round(x))
        self.y = int(round(y))
        self.hide = hide

    def mark(self):
        a = Pad(WHITE, self.radius, self.x, self.y, False)
        return a


class Table:
    def __init__(self, s, colour, radius, x, y, pc):
        self.size = s
        self.colour = colour
        self.radius = int(round(radius))
        self.angle = 0
        self.x = int(round(x))
        self.y = int(round(y))
        self.pads = list(Pad(pc[j], self.radius*pow(4, 0.75)/(3 * pow(size, 0.75)), self.x + self.radius*2/3 *
                         np.cos(self.angle + j * np.pi * 2 / size),
                         self.y + self.radius*2/3 * np.sin(self.angle + j
                                                           * np.pi * 2 / size)) for j in range(size))
        self.spin_count = 0
        self.choices = 0

    def shift(self, n, m):
        colours = [pad.colour for pad in self.pads]
        for i in range(self.size):
            self.pads[(i + m) % self.size].colour = colours[(i + n) % self.size]

    def spin(self):
        self.choices = 0
        self.angle = np.random.uniform(0, 2*np.pi)
        for j in range(self.size):
            self.pads[j].x = int(round(self.x + self.radius*2/3 * np.cos(self.angle + j * np.pi * 2 / self.size)))
            self.pads[j].y = int(round(self.y + self.radius*2/3 * np.sin(self.angle + j * np.pi * 2 / self.size)))
        self.spin_count += 1
        for pad in self.pads:
            pad.hide = True

    def switch(self, pad):
        i = self.pads.index(pad)
        if self.pads[i].colour == RED:
            self.pads[i].colour = BLUE
        else:
            self.pads[i].colour = RED


def random_colour():
    if np.random.randint(2) == 0:
        return RED
    else:
        return BLUE


# game prep (must be done in terminal)
size = int(input('Enter number of pads: '))
hands = int(input('Enter number of hands: '))
# SIZE AT LEAST 4 FOR GOOD SPACING
# size = 4
# hands = 2

# START PYGAME
pg.init()

display_width = 1000
display_height = 600

game_display = pg.display.set_mode((display_width, display_height))
pg.display.set_caption("Table Spin")
pg.display.update()
clock = pg.time.Clock()

pad_colours = [0] * size
table = Table(size, 0, 0, 0, 0, pad_colours)
win = False
click = False
reveal = False
adversary = False


def see():
    global reveal
    reveal = True


def set_up():
    # create random pad colours
    global pad_colours
    pad_colours = [random_colour() for j in range(size)]
    # initialize table
    global table
    table = Table(size, BROWN1, display_height * 3 / 8, display_width / 2, display_height * 4 / 9, pad_colours)


def draw(obj, hidden=False, white=False):
    if white:
        pg.draw.circle(game_display, WHITE, (obj.x, obj.y), obj.radius)
    elif hidden:
        pg.draw.circle(game_display, GREY, (obj.x, obj.y), obj.radius)
    else:
        pg.draw.circle(game_display, obj.colour, (obj.x, obj.y), obj.radius)


def show_button(pad, ic, ac):
    mouse = pg.mouse.get_pos()

    if np.sqrt(np.square(pad.x - mouse[0]) + np.square(pad.y - mouse[1])) < pad.radius:
        pg.draw.circle(game_display, ac, (pad.x, pad.y), pad.radius)

        if click and table.choices < hands:
            pad.hide = False
            draw(pad, white=True)
            table.choices += 1

    else:
        pg.draw.circle(game_display, ic, (pad.x, pad.y), pad.radius)


def switch_button(pad):
    mouse = pg.mouse.get_pos()
    # click = pg.mouse.get_pressed()

    draw(pad, pad.hide)
    if np.sqrt(np.square(pad.x - mouse[0]) + np.square(pad.y - mouse[1])) < pad.radius and click:
        if not pad.hide:
            table.switch(pad)
            draw(pad, pad.hide)


def game_spin():
    game_display.fill(BLACK)
    pg.display.update()
    time.sleep(0.5)
    global reveal, win, adversary
    adversary = False
    reveal = False
    table.spin()


def spin_button():
    square_button("SPIN", display_width/2 - 112, 540, 100, 50, GENTIAN, BRIGHTER_GENTIAN, game_spin)


def reveal_button():
    square_button("REVEAL", display_width/2 + 12, 540, 100, 50, GENTIAN, BRIGHTER_GENTIAN, see)


def menu_button():
    square_button("MENU", 875, 540, 100, 50, DULL_RED, RED, game_intro)


def buttons():
    spin_button()
    reveal_button()
    menu_button()


def draw_pads1():
    for pad in table.pads:
        if pad.hide:
            show_button(pad, GREY, WHITE)
        else:
            draw(pad.mark())


def draw_pads2():
    global adversary
    if not adversary:
        chosen = [not a.hide for a in table.pads]
        ids = [i for i, x in enumerate(chosen) if not x]
        n = len(ids)
        skips = []
        for i in range(n):
            if n == 1:
                break
            elif i == n - 1:
                skip = table.size % (ids[i] - ids[0])
            else:
                skip = ids[i+1] - ids[i]
            if Counter(a[0] for a in skips)[str(skip)] == 0:
                skips.append([skip, ids[i]])
        for skip in skips:
            for i in range(table.size):
                if table.pads[i].colour != table.pads[(i+skip[0]) % table.size].colour:
                    # if (ids[0] + skip) % table.size == ids[1]:
                    #     n = ids[0]
                    # else:
                    #     n = ids[1]
                    table.shift(i, skip[1])
                    adversary = True
                    break
    for pad in table.pads:
        if pad.hide:
            draw(pad, hidden=True)
        else:
            draw(pad.mark())


def draw_pads3():
    for pad in table.pads:
        if pad.hide:
            draw(pad, hidden=True)
        else:
            switch_button(pad)


def text_object(text, font):
    text_surface = font.render(text, True, WHITE)
    return text_surface, text_surface.get_rect()


def message_display(text, s, x, y):
    normal_text = pg.font.Font('freesansbold.ttf', s)
    text_surf, text_rect = text_object(text, normal_text)
    text_rect.center = (round(x), round(y))
    game_display.blit(text_surf, text_rect)

    pg.display.update()


def win_msg():
    for pad in table.pads:
        draw(pad)
    pg.display.update()
    time.sleep(1)
    game_display.fill(BLACK)
    message_display("Congratulations,", 80, display_width/2, display_height/3)
    if table.spin_count == 0:
        message_display("you won without spinning!", 65, display_width/2, display_height/2)
    elif table.spin_count == 1:
        message_display("you won after a single spin!", 65, display_width/2, display_height/2)
    else:
        message_display("you won after " + str(table.spin_count) + " spins!", 80, display_width/2, display_height/2)
    pg.display.update()
    time.sleep(3)
    game_intro()


def square_button(msg, x, y, w, h, ic, ac, action=None):
    global click
    x = int(round(x))
    y = int(round(y))
    w = int(round(w))
    h = int(round(h))
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pg.draw.rect(game_display, ac, (x, y, w, h))

        if click[0] == 1 and action is not None:
            action()
    else:
        pg.draw.rect(game_display, ic, (x, y, w, h))

    small_text = pg.font.Font("freesansbold.ttf", 20)
    text_surf, text_rect = text_object(msg, small_text)
    text_rect.center = (int(x+(w/2)), int(y+(h/2)))
    game_display.blit(text_surf, text_rect)


def game_loop():
    global win, click, reveal
    win = False
    reveal = False
    game_display.fill(BLACK)
    while not win:
        click = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                click = True
        draw(table)
        if reveal:
            draw_pads3()
        elif table.choices < hands:
            draw_pads1()
        elif table.choices == hands:
            draw_pads2()
        message_display("Spin Count: " + str(table.spin_count), 30, display_width / 2, 515)
        buttons()
        if all(table.pads[i].colour == table.pads[0].colour for i in range(1, size)):
            win = True
        pg.display.update()
        clock.tick(60)
    win_msg()
    time.sleep(2)
    game_intro()


def game_intro():
    set_up()
    if all(pad_colours[0] == pad_colours[i] for i in range(1, size)):
        table.switch(table.pads[size - 1])
    game_display.fill(BLACK)
    while True:
        for event in pg.event.get():
            print(event)
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        message_display("Table Spin", 100, display_width/2, display_height/3)

        square_button("Play", 250, 450, 100, 50, GREEN, BRIGHT_GREEN, game_loop)
        square_button("Quit", 650, 450, 100, 50, DULL_RED, RED, quit)
        pg.display.update()
        clock.tick(60)


game_intro()