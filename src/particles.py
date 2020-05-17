from color import COLOR_CHANNEL, change_color_bright
import glm
import random
import cv2
import numpy as np
import gui_functions as gui
import logger
import os

RESOURCES = os.path.join(os.path.dirname(__file__), "../resources/")
P_LIFE = 2  # + velocity
particles = None
colored_texture = []
texture_x = 0
texture_y = 0


class Particle(object):
    def __init__(self, velocity, channel, x1, x2):
        self.pos = glm.vec3()
        self.speed = glm.vec3()
        self.life = velocity + P_LIFE
        self.velocity = velocity
        self.x1, self.x2 = x1 + 1, x2
        self.channel = channel
        self.cycle = 0


def remove_dead_particles(particles):
    for particle in particles:
        if particle.life <= 0:
            particles.remove(particle)


def simulate_particules(particles, delta):
    """ y : Going up fast, then stoping and falling (if the note particle live enough)
        x, z : Slowly going left/right
        Every x cycle, add some randomness to the trajectory
    """
    for p in particles:
        p.life -= delta
        p.cycle += 1
        if p.life > 0:
            p.speed += glm.vec3(p.velocity * 2, -10, p.velocity * 2) * delta * 0.5
            p.pos += p.speed * delta
            p.pos.y += (1 + p.velocity) * 90 * delta * 0.5
            if p.cycle % 4 == 0:
                p.pos.y += random.randrange(-1, 2)
                p.pos.x += random.randrange(-1, 2)
                p.pos.z += random.randrange(-1, 2)
            if p.pos.y >= gui.PIANO_PIX_START - 12:
                p.life = 0
            if p.pos.y <= 0:
                p.pos.y = 1
    remove_dead_particles(particles)


def create_particles(note_pos, note):
    if particles == None:
        return
    particles.append(
        Particle(note.velocity / 10, note.channel, note_pos[0][0], note_pos[-1][0],)
    )


def put_texture_in_image(back, texture, x, y, alpha):
    rows, cols, channels = texture.shape
    alpha_transparency = texture[..., 3] != 0
    overlay = back[y : y + rows, x : x + cols]
    overlay_copy = overlay.copy()
    try:
        overlay[alpha_transparency] = texture[alpha_transparency]
    except IndexError:
        pass
    cv2.addWeighted(overlay, alpha, overlay_copy, 1 - alpha, 0, overlay_copy)
    back[y : y + rows, x : x + cols] = overlay_copy


def draw_particles(image, delta):
    global texture_x, texture_y

    if particles == None:
        return
    simulate_particules(particles, delta)
    for p in particles:
        texture = colored_texture[p.channel].copy()
        x1 = p.x1 - int(p.pos.x) if p.x1 - int(p.pos.x) > 0 else None
        x2 = p.x2 + int(p.pos.z) if p.x2 + int(p.pos.z) < gui.PIANO_X else None
        alpha = p.life / (p.velocity + P_LIFE)  # life / life max
        if x1:
            put_texture_in_image(
                image,
                texture,
                x1,
                gui.PIANO_PIX_START - texture_y - int(p.pos.y),
                alpha,
            )
        if x2:
            put_texture_in_image(
                image,
                texture,
                x2 - texture_x,
                gui.PIANO_PIX_START - texture_y - int(p.pos.y),
                alpha,
            )


def get_note_texture(texture_str):
    """ Load the particles texture,
        change the pure black by the channel's color
        and the pure white by full transparency
    """
    global texture_x, texture_y
    global colored_texture

    texture = cv2.imread(f"{RESOURCES}{texture_str}.png")
    if texture is None:
        logger.my_logger.warning(
            f"{RESOURCES}{texture_str}.png",
            "doesn't exist or is invalid, using dot texture for particles",
        )
        texture = cv2.imread(f"{RESOURCES}dot.png")
    texture_y, texture_x = texture.shape[0], texture.shape[1]
    texture = np.dstack((texture, np.zeros((texture_y, texture_x))))
    for color in COLOR_CHANNEL:
        if sum(color[:3]) / 3 > 127:
            color = change_color_bright(color, -50)
        else:
            color = change_color_bright(color, 50)
        colored_image = texture.copy()
        for y in range(0, texture_y):
            for x in range(0, texture_x):
                if np.all(colored_image[y][x] == [0, 0, 0, 0]):
                    colored_image[y][x] = color
                elif np.all(colored_image[y][x] == [255, 255, 255, 0]):
                    colored_image[y][x] = [255, 255, 255, 0]
                else:
                    colored_image[y][x][3] = 1
        colored_texture.append(colored_image.astype("uint8"))


def init(no_particles, particles_texture):
    global particles

    if not no_particles:
        particles = []
        get_note_texture(particles_texture)
