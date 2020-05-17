import numpy as np


def change_color_bright(color, factor=0):
    # this function will change the brightness of the color
    # if the factor > 0, it will be lighter, else, darker.
    b = np.clip(color[0] + factor, 0, 255)
    g = np.clip(color[1] + factor, 0, 255)
    r = np.clip(color[2] + factor, 0, 255)
    a = 1
    return [int(b), int(g), int(r), int(a)]


#           B    G    R    A
SKYBLUE = [250, 206, 135, 1]
SKYBLUE_FLASH = [255, 255, 0, 1]
PURPLE_BLUE = [240, 144, 141, 1]
GREY_BLUE = [162, 161, 130, 1]
YELLOW = [79, 243, 241, 1]
YELLOW_FLASH = [0, 255, 255, 1]
PINK = [249, 99, 233, 1]
PURPLE = [157, 40, 145, 1]
ORANGE = [40, 153, 242, 1]
LIGHT_BROWN = [141, 196, 240, 1]
RED = [100, 100, 255, 1]
SCARLET_RED = [24, 24, 165, 1]
BROWN = [65, 103, 155, 1]
GREEN = [100, 255, 100, 1]
GREEN_CLEAR = [141, 240, 185, 1]
DARK_GREEN = [20, 150, 20, 1]
GREY = [75, 75, 75, 1]
WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
COLOR_CHANNEL = [
    PINK,
    SKYBLUE,
    GREEN,
    PURPLE_BLUE,
    GREY_BLUE,
    YELLOW,
    YELLOW_FLASH,
    PINK,
    PURPLE,
    ORANGE,
    LIGHT_BROWN,
    RED,
    SCARLET_RED,
    BROWN,
    SKYBLUE_FLASH,
    GREEN_CLEAR,
    DARK_GREEN,
]
COLOR_CHANNEL_DARK = []
for color in COLOR_CHANNEL:
    COLOR_CHANNEL_DARK.append(change_color_bright(color, factor=-58))
