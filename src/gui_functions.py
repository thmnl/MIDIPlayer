import sys
import cv2
import numpy as np
from color import *
import sdl2.ext
import particles
import gui_handler
import os
import mido

RESOURCES = os.path.join(os.path.dirname(__file__), "../resources/")
PIANO_PNG_PATH = f"{RESOURCES}piano.png"
scx, scy = 0, 0  # screen x, screen y default 1020, 646
PIANO_X = 1020  # piano.jpg X
PIANO_Y = 109  # piano.jpg piano height
PIANO_PIX_START = 519  # piano.jpg piano is starting at pixel 519
FUTUR_PART_TIME = 3  # time in the futur
image_base = None  # cv2 image
pos_list = None  # note polygon coord list
window = None  # sdl2 window
windowArray = None  # sdl2 pixel3d


def set_new_index(partition, i, x, y, length, modif, notes, port, paused):
    """If the user click on the player bar,
    this function shut the music and particles, and then,
    return the new index and the modification that we need to apply to time
    """
    if y >= scy - 25 and y <= scy:
        target_time = length * x / scx
        l = 0
        while partition[l]:
            if partition[l]["time"] > target_time:
                modif += partition[l]["time"] - partition[i]["time"]
                for note in notes:
                    if port:
                        # shut all channel to avoid parasite notes
                        for channel in range(0, 16):
                            shut_msg = mido.Message(
                                "note_off",
                                note=note.id + 21,
                                channel=channel,
                                velocity=0,
                                time=0,
                            )
                            # dont use reset or panic method, too slow.
                            port.send(shut_msg)
                    note.playuntil = 0
                if particles.particles:
                    particles.particles = []
                return modif, l, paused
            l += 1
    return modif, i, paused


def get_events(partition, i, length, modif, notes, port, paused):
    events = sdl2.ext.get_events()
    for e in events:
        if e.type == sdl2.SDL_QUIT:
            sdl2.ext.quit()
            break
        if e.type == sdl2.SDL_KEYDOWN:
            if e.key.keysym.sym == 27:  # ESC
                sdl2.ext.quit()
                break
            if e.key.keysym.sym == ord(" "):
                paused = not paused  # reverse True False
        if e.type == sdl2.SDL_MOUSEBUTTONDOWN:
            modif, i, paused = set_new_index(
                partition, i, e.button.x, e.button.y, length, modif, notes, port, paused
            )
    return modif, i, paused


def draw_rect(image, x1, y1, x2, y2, color):
    pt1 = (x1, y1)
    pt2 = (x1, y2)
    pt3 = (x2, y2)
    pt4 = (x2, y1)
    pts = np.array([pt1, pt2, pt3, pt4], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.fillPoly(image, [pts], color)
    cv2.polylines(image, [pts], True, BLACK)


def draw_futurpart(image, futurpart, timecode, notes, tnow):
    """Draw the futur partition, then draw the actual playing note
       x, width, y, height
    """
    if not futurpart:
        return
    for note in futurpart:
        if note["msg"].type == "note_on" and note["new_velocity"]:
            n = note["msg"].note - 21
            x = pos_list[n][0][0] + 1
            w = pos_list[n][-1][0] - pos_list[n][0][0] - 1
            velocity = note["new_velocity"] / 10
            h = velocity / FUTUR_PART_TIME * PIANO_PIX_START
            t = note["time"] - timecode
            y = t / FUTUR_PART_TIME * PIANO_PIX_START
            y = PIANO_PIX_START - y
            color = COLOR_CHANNEL[note["msg"].channel]
            if not notes[note["msg"].note - 21].is_white:
                color = COLOR_CHANNEL_DARK[note["msg"].channel]
            draw_rect(image, x, y - h, x + w, y, color)
    for note in notes:
        diff = note.playuntil - tnow
        if diff <= 0:
            continue
        n = note.id
        x = pos_list[n][0][0] + 1
        w = pos_list[n][-1][0] - pos_list[n][0][0] - 1
        h = diff / FUTUR_PART_TIME * (PIANO_PIX_START - 1)
        y = PIANO_PIX_START - 1
        color = COLOR_CHANNEL[note.channel]
        if not note.is_white:
            color = COLOR_CHANNEL_DARK[note.channel]
        draw_rect(image, x, y - h, x + w, y, color)


def print_text(texte, image, x=0, y=250, alpha=1):
    font = cv2.FONT_HERSHEY_COMPLEX
    overlay = image.copy()
    cv2.putText(overlay, texte, (x, y), font, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)


def draw_player(image, length, timecode):
    w = timecode / length * PIANO_X
    draw_rect(
        image, 0, PIANO_PIX_START + PIANO_Y + 1, w, PIANO_PIX_START + PIANO_Y + 16, RED
    )


def draw_note(image, p, note):
    pts = np.array(p, np.int32)
    pts = pts.reshape((-1, 1, 2))
    color = COLOR_CHANNEL[note.channel]
    if not note.is_white:
        color = COLOR_CHANNEL_DARK[note.channel]
    cv2.fillPoly(image, [pts], color)
    cv2.polylines(image, [pts], True, BLACK)


def find_note_polygon(image, color, x):
    """return a list of tuple that contain the x, y position of every corner
       starting from top left to to right.
    """
    pos_list = [(x, PIANO_PIX_START)]
    if np.all(color == WHITE):
        for i in range(PIANO_PIX_START, PIANO_PIX_START + PIANO_Y):
            if x == 0:
                break
            if np.all(image[i][x - 1] == color):
                pos_list.append((x, i))
                while x > 0:
                    if np.all(image[i][x] != color):
                        pos_list.append((x, i))
                        break
                    x -= 1
                break
        y = PIANO_PIX_START + PIANO_Y - 1
        pos_list.append((x, y))
        while x < image.shape[1] - 1:
            if np.all(image[y][x + 1] != color):
                break
            x += 1
        pos_list.append((x, y))
        for i in range(PIANO_PIX_START + PIANO_Y - 1, PIANO_PIX_START, -1):
            if np.all(image[i][x] != color):
                pos_list.append((x, i + 1))
                while x > 0:
                    if np.all(image[i][x] == color):
                        pos_list.append((x, i + 1))
                        break
                    x -= 1
                break
        pos_list.append((x, PIANO_PIX_START))
    else:
        for i in range(PIANO_PIX_START, PIANO_PIX_START + PIANO_Y - 1):
            if np.all(image[i + 1][x] != color):
                pos_list.append((x, i + 1))
                while np.all(image[i][x] == color):
                    x += 1
                break
        pos_list.append((x, i + 1))
        pos_list.append((x, PIANO_PIX_START))
    return pos_list


def get_note_position(image):
    """return a list that contain the the outline position of every notes
       Keep in mind that the notes are pure black/pure white.
    """
    last = BLACK
    i = 0
    pos_list = []
    for x in range(0, image.shape[1]):
        color = image[PIANO_PIX_START][x]
        if np.all(color != WHITE) and np.all(color != BLACK):
            last = color
        elif np.all(color == last):
            continue
        else:
            i += 1
            pos_list.append(find_note_polygon(image, color, x))
            last = color
    return pos_list


def init(background_image, background_transparency, window_size):
    global image_base
    global pos_list
    global windowArray
    global window
    global scx, scy

    if window_size:
        scx, scy = window_size[0], window_size[1]
    else:
        scx, scy = 1020, 646
    image_base = cv2.imread(PIANO_PNG_PATH, cv2.IMREAD_UNCHANGED)
    pos_list = get_note_position(image_base[:, :, 0])
    if background_image:
        new_image = image_base.copy()
        b = cv2.imread(f"{RESOURCES}{background_image}.png", cv2.IMREAD_UNCHANGED)
        resized = cv2.resize(
            b, (PIANO_X, PIANO_PIX_START - 1), interpolation=cv2.INTER_AREA
        )
        new_image[: PIANO_PIX_START - 1, :] = resized
        alpha = background_transparency
        cv2.addWeighted(new_image, alpha, image_base, 1 - alpha, 0, image_base)
    sdl2.ext.init()
    window = sdl2.ext.Window("Midi Vizualizer", size=(scx, scy))
    windowArray = sdl2.ext.pixels3d(window.get_surface())
    window.show()
